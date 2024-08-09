import src.controller as controller
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from langchain_community.graphs import Neo4jGraph
from src.config import TEMP_STORAGE
from src.client.llm import LLMModel
from src.client.graph_db import GraphDBDataAccess

load_dotenv()

db = GraphDBDataAccess(Neo4jGraph())
llm_model = LLMModel()

result = controller.extract_pdf_document(
    db, llm_model, "./tests/data/The King in Yellow.pdf", "The King in Yellow.pdf"
)

print(result)
