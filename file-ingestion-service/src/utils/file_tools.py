from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from typing import List
from langchain.docstore.document import Document


def delete_file(file_path: str):
    file_path = Path(file_path)
    if file_path.exists():
        file_path.unlink()


def load_pdf(file_path: str) -> List[Document]:
    loader = PyMuPDFLoader(file_path)
    return loader.load()
