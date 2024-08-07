from dataclasses import dataclass
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import requests
from langchain_community.graphs import Neo4jGraph
from src.qa_processor import QA_RAG_Vector_Graph

app = FastAPI()
load_dotenv()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@dataclass
class ChatRequest:
    questions: str
    session: int


@app.get("/chat/completions")
async def get_chat_completion(req: ChatRequest):
    try:
        graph = Neo4jGraph(sanitize=True)
        result = QA_RAG_Vector_Graph(
            graph=graph, question=req.questions, session_id=req.session
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
