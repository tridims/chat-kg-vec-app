from pathlib import Path
from langchain.docstore.document import Document
from langchain_community.graphs import Neo4jGraph
from typing import List
from processor.process import process_source
from utils.file_tools import load_pdf


def extract_graph_from_local_file(
    graph: Neo4jGraph,
    file_path: str,
    file_name: str,
    allowed_nodes: List[str] = [],
    allowed_relationship: List[str] = [],
):
    pages = get_documents(file_path)
    if pages == None or len(pages) == 0:
        raise Exception(f"File content is not available for file : {file_name}")

    return process_source(
        graph,
        file_name,
        pages,
        allowed_nodes,
        allowed_relationship,
    )


def get_documents(file_path: str) -> List[Document]:
    if Path(file_path).exists():
        try:
            pages = load_pdf(file_path)
        except Exception as e:
            raise Exception("Error while reading the file content or metadata")
    else:
        raise Exception(f"File {Path(file_path).name} does not exist")
    return pages
