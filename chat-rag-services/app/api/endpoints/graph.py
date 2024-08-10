from fastapi import APIRouter
from app.services import graph
from app.api.dependencies import get_graph_db_dao

router = APIRouter()


@router.get("")
async def get_graph():
    return graph.get_graphs(get_graph_db_dao())
