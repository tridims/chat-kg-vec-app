import os
import shutil
import requests
import src.controller as controller
from contextlib import asynccontextmanager
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile
from langchain_community.graphs import Neo4jGraph
from src.config import TEMP_STORAGE
from src.client.llm import LLMModel
from src.client.graph_db import GraphDBDataAccess


load_dotenv()

db = None
llm_model = None


def get_db():
    global db
    return db


def get_llm_model():
    global llm_model
    return llm_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    global llm_model
    db = GraphDBDataAccess(Neo4jGraph())
    llm_model = LLMModel()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


def extract_file_task(db, llm_model, filename):
    try:
        result = controller.extract_pdf_document(db, llm_model, filename, filename)
        os.remove(filename)
    except Exception as e:
        print(f"INTERNAL SERVER ERROR. Detail : \n{str(e)}")


@app.post("/extract")
async def file_extraction(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    try:
        with open(file.filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    background_tasks.add_task(
        extract_file_task, get_db(), get_llm_model(), file.filename
    )
    return {"message": "File extraction started in the background"}


class RemoteFileExtractionRequest(BaseModel):
    file_uri: str
    notification_callback: str


@app.post("/extraction-remote-file")
async def remotefile_extraction(
    req: RemoteFileExtractionRequest,
    db: GraphDBDataAccess = Depends(get_db),
    llm_model=Depends(get_llm_model),
):
    print("extracting file_uri", req.file_uri)
    try:
        # Download the file
        response = requests.get(req.file_uri)
        response.raise_for_status()
        file_name = os.path.basename(req.file_uri)
        file_path = os.path.join(TEMP_STORAGE, file_name)
        with open(file_path, "wb") as f:
            f.write(response.content)

        result = controller.extract_pdf_document(db, llm_model, file_path, file_name)

        # delete document after processing
        os.remove(file_path)

        return result
    except requests.RequestException as e:
        return HTTPException(
            status_code=400, detail=f"FILE NOT FOUND. Detail : \n{str(e)}"
        )
    except Exception as e:
        return HTTPException(
            status_code=500, detail=f"INTERNAL SERVER ERROR. Detail : \n{str(e)}"
        )
