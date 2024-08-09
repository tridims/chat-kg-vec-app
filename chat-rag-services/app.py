from contextlib import asynccontextmanager
from dataclasses import dataclass
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from langchain_community.graphs import Neo4jGraph
from controller import get_chat_completions
from src.processor.completions import QAEngine

load_dotenv()

qa_engine = None


def get_engine():
    return qa_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    global qa_engine
    db = Neo4jGraph(sanitize=True)
    qa_engine = QAEngine(db)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@dataclass
class ChatRequest:
    questions: str
    session: int


@app.get("/chat/completions")
async def get_chat_completion(
    req: ChatRequest, qa_engine: QAEngine = Depends(get_engine)
):
    try:
        result = get_chat_completions(qa_engine, req.questions, req.session)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
