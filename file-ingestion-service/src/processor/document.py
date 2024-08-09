from datetime import datetime
import hashlib
from typing import List
from src.config import CHUNK_BATCH_SIZE, FIRST_CHUNK, NEXT_CHUNK
from src.client.graph_db import GraphDBDataAccess
from src.models.chunk import (
    ChunkDocument,
    ChunkGraphDocumentPair,
    ChunkNode,
    ChunkRelationship,
)
from src.models.document import DocumentNode
from src.processor.embedding import (
    EmbeddingGenerator,
)
from src.processor.graph import GraphGenerator
from src.utils import clean_documents, split_file_into_chunks
from langchain.docstore.document import Document
from langchain_community.graphs.graph_document import GraphDocument


class DocumentProcessor:
    def __init__(
        self,
        db_dao: GraphDBDataAccess,
        graph_generator: GraphGenerator,
        embedding_generator: EmbeddingGenerator,
    ):
        self.db_dao = db_dao
        self.graph_generator = graph_generator
        self.embedding_generator = embedding_generator

    def process_document(self, file_name: str, pages: List[Document]) -> dict:
        # check if the document is already processed or processing by other worker
        # document = self.db_dao.get_document(file_name)
        # if document[0].status in ["Processing", "Completed"]:
        #     return

        # Create the document node
        source_node = DocumentNode(
            file_name=file_name,
            status="Processing",
        )
        self.db_dao.add_document(source_node)

        # prepare the document
        pages = clean_documents(pages)
        chunks = split_file_into_chunks(pages)

        # build a graph that represents the chunked document
        chunk_nodes, chunk_relationships, chunk_documents = (
            _build_chunk_graph_structure(chunks, file_name)
        )
        self.db_dao.insert_chunk_graph(chunk_nodes, chunk_relationships)

        count_nodes, count_relationships = self._process_chunks(
            file_name,
            chunk_documents,
        )

        source_node = DocumentNode(
            file_name=file_name,
            updated_at=datetime.now(),
            node_count=count_nodes,
            processed_chunk=len(chunks),
            relationship_count=count_relationships,
            total_chunks=len(chunks),
            total_pages=len(pages),
            status="Completed",
        )
        self.db_dao.update_document(source_node)

        return {
            "file_name": file_name,
            "node_count": count_nodes,
            "relationship_count": count_relationships,
            "status": "Completed",
        }

    def _process_chunks(
        self,
        file_name: str,
        chunk_documents: List[ChunkDocument],
    ) -> tuple[int, int]:

        # create and add embeddings to the database
        embedding = self.embedding_generator.generate_embeddings(chunk_documents)
        self.db_dao.insert_chunk_embeddings(file_name, embedding)

        # create and add graph documents to the database
        graph_documents = self.graph_generator.generate_graph(chunk_documents)
        self.db_dao.add_graph_documents(graph_documents)

        # connect the chunks to the entities in the graph documents
        chunks_and_graph_documents = _get_chunk_and_graph_document_pairs(
            graph_documents
        )
        self.db_dao.add_relationships_between_chunk_and_entities(
            chunks_and_graph_documents
        )

        # Done, now counting
        distinct_nodes = {
            (node.id, node.type)
            for graph_document in graph_documents
            for node in graph_document.nodes
        }

        relations = [
            relation.type
            for graph_document in graph_documents
            for relation in graph_document.relationships
        ]

        return len(distinct_nodes), len(relations)


def _build_chunk_graph_structure(
    chunks: List[Document], file_name: str
) -> tuple[List[ChunkNode], List[ChunkRelationship], List[ChunkDocument]]:
    chunk_nodes = []
    chunk_relationships = []
    current_chunk_id = ""
    offset = 0

    for i, chunk in enumerate(chunks):
        page_content_sha1 = hashlib.sha1(chunk.page_content.encode()).hexdigest()
        previous_chunk_id = current_chunk_id
        current_chunk_id = page_content_sha1
        position = i + 1
        offset += len(chunks[i - 1].page_content) if i > 0 else 0

        chunk_data = ChunkNode(
            id=current_chunk_id,
            text=chunk.page_content,
            position=position,
            length=len(chunk.page_content),
            file_name=file_name,
            previous_id=previous_chunk_id,
            content_offset=offset,
            **{
                k: v
                for k, v in chunk.metadata.items()
                if k in ["page_number", "start_time", "end_time"]
            }
        )

        chunk_nodes.append(chunk_data)
        chunk_relationships.append(
            ChunkRelationship(
                type=FIRST_CHUNK if i == 0 else NEXT_CHUNK,
                previous_chunk_id=previous_chunk_id,
                current_chunk_id=current_chunk_id,
            )
        )

    chunk_documents = [
        ChunkDocument(chunk_id=data.id, chunk_doc=chunk)
        for data, chunk in zip(chunk_nodes, chunks)
    ]

    return chunk_nodes, chunk_relationships, chunk_documents


def _get_chunk_and_graph_document_pairs(
    documents: List[GraphDocument],
) -> List[ChunkGraphDocumentPair]:
    list_doc_chunkid = []
    for graph_document in documents:
        for chunk_id in graph_document.source.metadata["combined_chunk_ids"]:
            list_doc_chunkid.append(
                ChunkGraphDocumentPair(
                    chunk_id=chunk_id,
                    graph_document=graph_document,
                )
            )

    return list_doc_chunkid
