from concurrent.futures import ThreadPoolExecutor
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain.docstore.document import Document
from langchain_community.graphs.graph_document import GraphDocument
from typing import List
import concurrent
from src.config import CHUNK_COMBINE_SIZE, MAX_WORKERS
from src.client.llm import LLMModel
from src.models.chunk import ChunkDocument
from src.utils import batch


class GraphGenerator:
    def __init__(
        self,
        llm_model: LLMModel,
        allowed_nodes: List[str] = [],
        allowed_relationships: List[str] = [],
    ):
        self.llm_model = llm_model
        self.transformer = LLMGraphTransformer(
            llm=llm_model.get_chat_model(),
            node_properties=["description"],
            allowed_nodes=allowed_nodes,
            allowed_relationships=allowed_relationships,
        )

    def generate_graph(
        self, chunk_documents: List[ChunkDocument]
    ) -> List[GraphDocument]:
        """Accepts a list of ChunkDocuments and returns a list of Documents (with nodes and relationships properties inside it)"""
        combined_chunk_document_list = self._combine_chunks(chunk_documents)
        graph_document_list = []

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(self.transformer.convert_to_graph_documents, [doc])
                for doc in combined_chunk_document_list  # note: the old code is remaking the Documents by encoding it in utf-8
            ]

            for future in concurrent.futures.as_completed(futures):
                try:
                    graph_document = future.result()
                    graph_document_list.append(graph_document[0])
                except Exception as e:
                    print(f"An error occurred when generating a graph document: {e}")

        return graph_document_list

    @staticmethod
    def _combine_chunks(chunkDocuments: List[ChunkDocument]) -> List[Document]:
        combined_chunk_document_list = []

        for _, _, chunk in batch(chunkDocuments, CHUNK_COMBINE_SIZE):
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
