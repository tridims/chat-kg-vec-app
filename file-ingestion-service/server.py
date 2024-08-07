import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import requests

from src.extractor import extract_graph_from_local_file
from src.graph_dao import GraphDBDataAccess
from src.models.source_node import SourceNode
from langchain_community.graphs import Neo4jGraph


app = FastAPI()
load_dotenv()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/extraction")
def file_extraction(file_uri: str):
    print("extracting file_uri", file_uri)
    try:
        response = requests.get(file_uri)
        response.raise_for_status()

        file_name = os.path.basename(file_uri)
        file_path = os.path.join("data", file_name)
        with open(file_path, "wb") as f:
            f.write(response.content)

        source_node = SourceNode(
            file_name=file_name,
        )

        graph = Neo4jGraph()
        data_access = GraphDBDataAccess(graph)
        data_access.create_source_node(source_node)

        result = extract_graph_from_local_file(graph, file_path, file_name)

        return result
    except requests.RequestException as e:
        return HTTPException(
            status_code=400, detail=f"FILE NOT FOUND. Detail : \n{str(e)}"
        )
    except Exception as e:
        return HTTPException(
            status_code=500, detail=f"INTERNAL SERVER ERROR. Detail : \n{str(e)}"
        )
