from typing import List
from pathlib import Path
from itertools import islice
from langchain_text_splitters import TokenTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.docstore.document import Document


def split_file_into_chunks(pages: List[Document]) -> List[Document]:
    text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=20)
    chunks = []
    if "page" in pages[0].metadata:
        for i, document in enumerate(pages):
            page_number = i + 1
            for chunk in text_splitter.split_documents([document]):
                chunks.append(
                    Document(
                        page_content=chunk.page_content,
                        metadata={"page_number": page_number},
                    )
                )
    else:
        chunks = text_splitter.split_documents(pages)
    return chunks


def clean_documents(pages: List[Document]) -> List[Document]:
    translation_table = str.maketrans({'"': "", "'": "", "\n": " "})

    for i in range(len(pages)):
        text = pages[i].page_content.translate(translation_table)
        pages[i] = Document(page_content=text, metadata=pages[i].metadata)

    return pages


def batch(iterable, batch_size: int):
    it = iter(iterable)
    start_index = 0
    while True:
        chunk = list(islice(it, batch_size))
        if not chunk:
            break
        end_index = start_index + len(chunk) - 1
        yield start_index, end_index, chunk
        start_index += batch_size


def delete_file(file_path: str):
    file_path = Path(file_path)
    if file_path.exists():
        file_path.unlink()


def load_pdf(file_path: str) -> List[Document]:
    loader = PyMuPDFLoader(file_path)
    return loader.load()
