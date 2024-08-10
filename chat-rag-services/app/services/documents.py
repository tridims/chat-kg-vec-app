from app.db.graph_db import GraphDBDataAccess


def get_documents(
    graph_db_dao: GraphDBDataAccess,
):
    return graph_db_dao.get_documents()


def delete_document(
    graph_db_dao: GraphDBDataAccess,
    file_name: str,
):
    return graph_db_dao.delete_document(file_name)
