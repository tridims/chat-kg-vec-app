from concurrent.futures import ThreadPoolExecutor
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs import Neo4jGraph
from langchain.docstore.document import Document
from typing import List
import concurrent
from config import CHUNK_COMBINE_SIZE, MAX_WORKERS
from llm import get_llm_model
from models.chunk_data import ChunkIdDocPair
from utils.chunker import batch


def generate_graph_documents(
    chunk_id_doc_pairs: List[ChunkIdDocPair],
    allowedNodes: List[str] = [],
    allowedRelationship: List[str] = [],
):
    combined_chunk_document_list = _combine_chunks(chunk_id_doc_pairs)

    llm = get_llm_model()

    return _get_graph_documents(
        llm, combined_chunk_document_list, allowedNodes, allowedRelationship
    )


def _combine_chunks(chunkId_chunkDoc_list: List[ChunkIdDocPair]):
    combined_chunk_document_list = []

    for _, _, chunk in batch(chunkId_chunkDoc_list, CHUNK_COMBINE_SIZE):
        combined_page_content = "".join(
            document.chunk_doc.page_content for document in chunk
        )
        combined_ids = [document.chunk_id for document in chunk]
        combined_chunk_document_list.append(
            Document(
                page_content=combined_page_content,
                metadata={"combined_chunk_ids": combined_ids},
            )
        )

    return combined_chunk_document_list


def _get_graph_documents(
    llm, chunk_documents, allowed_nodes, allowed_relationships
) -> List[Document]:

    llm_transformer = LLMGraphTransformer(
        llm=llm,
        node_properties=["description"],
        allowed_nodes=allowed_nodes,
        allowed_relationships=allowed_relationships,
    )

    graph_document_list = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(llm_transformer.convert_to_graph_documents, [doc])
            for doc in chunk_documents  # note: the old code is remaking the Documents by encoding it in utf-8
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                graph_document = future.result()
                graph_document_list.append(graph_document[0])
            except Exception as e:
                print(f"An error occurred: {e}")

    return graph_document_list
