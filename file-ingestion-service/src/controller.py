from pathlib import Path
from langchain.docstore.document import Document
from langchain_community.graphs import Neo4jGraph
from typing import List
from .client.graph_db import GraphDBDataAccess
from .client.llm import LLMModel
from .processor.embedding import EmbeddingGenerator
from .processor.graph import GraphGenerator
from .processor.document import DocumentProcessor
from .utils import load_pdf


def extract_pdf_document(
    db: GraphDBDataAccess,
    llm: LLMModel,
    file_path: str,
    file_name: str,
):
    pages = load_documents(file_path)
    if pages == None or len(pages) == 0:
        raise Exception(f"File content is not available for file : {file_name}")

    graph_gen = GraphGenerator(llm)
    embed_gen = EmbeddingGenerator(llm)
    dp = DocumentProcessor(db, graph_gen, embed_gen)
    result = dp.process_document(file_name, pages)
    return result


def load_documents(file_path: str) -> List[Document]:
    if Path(file_path).exists():
        try:
            pages = load_pdf(file_path)
        except Exception as e:
            raise Exception("Error while reading the file content or metadata")
    else:
        raise Exception(f"File {Path(file_path).name} does not exist")
    return pages
