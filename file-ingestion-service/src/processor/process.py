from datetime import datetime
from typing import List
from src.config import CHUNK_BATCH_SIZE
from src.graph_dao import GraphDBDataAccess
from src.models.chunk_data import ChunkIdDocPair
from src.models.source_node import SourceNode
from src.processor.embedding import update_embedding_create_vector_index
from src.processor.graph_documents import generate_graph_documents
from src.processor.relation import create_relation_between_chunks
from src.utils.chunker import batch, clean_documents, split_file_into_chunks
from langchain_community.graphs import Neo4jGraph
from langchain.docstore.document import Document


def process_source(
    graph: Neo4jGraph,
    file_name: str,
    pages: List[Document],
    allowed_nodes: List[str] = [],
    allowed_relationships: List[str] = [],
):
    data_repository = GraphDBDataAccess(graph)

    current_document = data_repository.get_current_status_document_node(file_name)
    document_status = current_document[0]["Status"]
    if document_status in ["Processing", "Completed"]:
        return

    pages = clean_documents(pages)
    chunks = split_file_into_chunks(pages)

    id_and_doc_list = create_relation_between_chunks(graph, file_name, chunks)

    source_node = SourceNode(
        file_name=file_name,
        status="Processing",
        total_chunks=len(chunks),
        total_pages=len(pages),
    )
    data_repository.update_source_node(source_node)

    total_nodes = 0
    total_relationships = 0
    for _, end_index, current_batch in batch(id_and_doc_list, CHUNK_BATCH_SIZE):
        count_nodes, count_relationships = _process_chunks(
            current_batch,
            graph,
            file_name,
            allowed_nodes,
            allowed_relationships,
            total_nodes,
            total_relationships,
        )

        total_nodes += count_nodes
        total_relationships += count_relationships

        source_node = SourceNode(
            file_name=file_name,
            updated_at=datetime.now(),
            node_count=total_nodes,
            processed_chunk=end_index,
            relationship_count=total_relationships,
        )
        data_repository.update_source_node(source_node)

    # update the status
    source_node = SourceNode(file_name=file_name, status="Completed")
    data_repository.update_source_node(source_node)

    return {
        "file_name": file_name,
        "node_count": total_nodes,
        "relationship_count": total_relationships,
        "status": "Completed",
        "success_count": 1,
    }


def _process_chunks(
    chunkId_chunkDoc_list: List[ChunkIdDocPair],
    graph: Neo4jGraph,
    file_name: str,
    allowedNodes: List[str],
    allowedRelationship: List[str],
    node_count: int,
    rel_count: int,
):
    # create vector index and update chunk node with embedding
    update_embedding_create_vector_index(graph, chunkId_chunkDoc_list, file_name)

    graph_documents = generate_graph_documents(
        chunkId_chunkDoc_list, allowedNodes, allowedRelationship
    )

    graph.add_graph_documents(graph_documents)

    chunks_and_graph_documents = _get_chunk_and_graph_documents(graph_documents)

    _merge_relationship_between_chunk_and_entites(graph, chunks_and_graph_documents)

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

    node_count += len(distinct_nodes)
    rel_count += len(relations)

    return node_count, rel_count


def _get_chunk_and_graph_documents(graph_document_list):
    lst_chunk_chunkId_document = []
    for graph_document in graph_document_list:
        for chunk_id in graph_document.source.metadata["combined_chunk_ids"]:
            lst_chunk_chunkId_document.append(
                {"graph_doc": graph_document, "chunk_id": chunk_id}
            )

    return lst_chunk_chunkId_document


def _merge_relationship_between_chunk_and_entites(
    graph: Neo4jGraph, graph_documents_chunk_chunk_Id: list
):
    batch_data = []
    for graph_doc_chunk_id in graph_documents_chunk_chunk_Id:
        for node in graph_doc_chunk_id["graph_doc"].nodes:
            query_data = {
                "chunk_id": graph_doc_chunk_id["chunk_id"],
                "node_type": node.type,
                "node_id": node.id,
            }
            batch_data.append(query_data)

    if batch_data:
        unwind_query = """
                    UNWIND $batch_data AS data
                    MATCH (c:Chunk {id: data.chunk_id})
                    CALL apoc.merge.node([data.node_type], {id: data.node_id}) YIELD node AS n
                    MERGE (c)-[:HAS_ENTITY]->(n)
                """
        graph.query(unwind_query, params={"batch_data": batch_data})
