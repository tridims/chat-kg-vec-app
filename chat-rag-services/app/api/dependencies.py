from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.db.graph_db import GraphDBDataAccess
from app.services.chat import QAEngine
from langchain_community.graphs import Neo4jGraph

qa_engine = None
graph_db_dao = None


def get_engine():
    global qa_engine
    return qa_engine


def get_graph_db_dao():
    global graph_db_dao
    return graph_db_dao


@asynccontextmanager
async def initialize_deps(app: FastAPI):
    global qa_engine
    global graph_db_dao

    db = Neo4jGraph(sanitize=True)
    qa_engine = QAEngine(db)
    graph_db_dao = GraphDBDataAccess(db)

    yield
