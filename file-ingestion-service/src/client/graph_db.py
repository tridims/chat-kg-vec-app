import logging
from typing import Any, Dict, List
from langchain_community.graphs import Neo4jGraph
from langchain_community.graphs.graph_document import GraphDocument
from src.config import KNN_MIN_SCORE
from src.models.chunk import (
    ChunkEmbedding,
    ChunkGraphDocumentPair,
    ChunkNode,
    ChunkRelationship,
)
from src.models.document import DocumentNode
from src.config import FIRST_CHUNK, NEXT_CHUNK


class GraphDBDataAccess:
    def __init__(self, graph: Neo4jGraph):
        self.graph = graph

    def add_document(self, node: DocumentNode) -> None:
        try:
            self.graph.query(
                """
                MERGE (d:Document {file_name: $file_name})
                ON CREATE SET d = $props
                """,
                {"file_name": node.file_name, "props": node.fill_default().to_dict()},
            )
        except Exception as e:
            logging.error(f"Error creating source node: {str(e)}")

    def update_document(self, node: DocumentNode):
        try:
            self.graph.query(
                """
                MERGE (d:Document {file_name: $file_name})
                ON MATCH SET d += $props
                """,
                {"file_name": node.file_name, "props": node.to_dict_not_default()},
            )
        except Exception as e:
            logging.error(f"Error upserting source node: {str(e)}")

    def get_documents(self) -> List[DocumentNode]:
        result = self.graph.query(
            """
            MATCH (d:Document)
            RETURN d
            ORDER BY d.updatedAt DESC
            """
        )

        return [DocumentNode(**record["d"]) for record in result]

    def get_document(self, file_name: str) -> List[DocumentNode]:
        result = self.graph.query(
            """
            MATCH (d:Document {file_name: $file_name})
            RETURN d
            """,
            {"file_name": file_name},
        )
        return DocumentNode(**result[0]["d"])

    def update_knn_graph(self) -> None:
        index = self.graph.query(
            "SHOW INDEXES YIELD * WHERE type = 'VECTOR' AND name = 'vector'"
        )

        if index:
            logging.info("Updating KNN graph")
            self.graph.query(
                """
                MATCH (c:Chunk)
                WHERE c.embedding IS NOT NULL AND count { (c)-[:SIMILAR]-() } < 5
                CALL db.index.vector.queryNodes('vector', 6, c.embedding) YIELD node, score
                WHERE node <> c AND score >= $score
                MERGE (c)-[rel:SIMILAR]-(node)
                SET rel.score = score
                """,
                {"score": KNN_MIN_SCORE},
            )
        else:
            logging.info("Vector index does not exist. KNN graph not updated.")

    def delete_document(self, file_name: str) -> tuple:
        result = self.graph.query(
            """
            MATCH (d:Document {file_name: $file_name})
            WITH collect(d) AS documents
            UNWIND documents AS d
            OPTIONAL MATCH (d)<-[:PART_OF]-(c:Chunk)
            CALL {
                WITH c, documents
                MATCH (c)-[:HAS_ENTITY]->(e)
                WHERE NOT exists { (d2)<-[:PART_OF]-()-[:HAS_ENTITY]->(e) WHERE NOT d2 IN documents }
                DETACH DELETE e
                RETURN count(*) AS entities
            }
            DETACH DELETE c, d
            RETURN sum(entities) AS deleted_entities, count(*) AS deleted_chunks
            """,
            {"file_name": file_name},
        )
        logging.info(f"Deleting document {file_name} with result {result}")

        return result

    def create_vector_index(self, dimension: int) -> None:
        self.graph.query(
            """
            CREATE VECTOR INDEX vector IF NOT EXISTS FOR (c:Chunk) ON (c.embedding)
            OPTIONS {
                indexConfig: {
                    `vector.dimensions`: $dimension,
                    `vector.similarity_function`: 'cosine'
                }
            }
            """,
            {"dimension": dimension},
        )

    def insert_chunk_embeddings(self, file_name: str, embedding: List[ChunkEmbedding]):
        data = [chunk.to_dict() for chunk in embedding]

        self.graph.query(
            """
            UNWIND $data AS row
            MATCH (d:Document {file_name: $file_name})
            MERGE (c:Chunk {id: row.chunk_id})
            SET c.embedding = row.embeddings
            MERGE (c)-[:PART_OF]->(d)
            """,
            params={"file_name": file_name, "data": data},
        )

    def add_graph_documents(
        self,
        graph_documents: List[GraphDocument],
        include_source: bool = False,
        baseEntityLabel: bool = False,
    ) -> None:
        self.graph.add_graph_documents(graph_documents, include_source, baseEntityLabel)

    def add_relationships_between_chunk_and_entities(
        self, datas: List[ChunkGraphDocumentPair]
    ):
        batch_data = []
        for data in datas:
            for node in data.graph_document.nodes:
                query_data = {
                    "chunk_id": data.chunk_id,
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
            self.graph.query(unwind_query, {"batch_data": batch_data})
        else:
            logging.info(
                "Attempt in calling add_relationships_between_chunk_and_entities with empty data"
            )

    def insert_chunk_graph(
        self,
        batch_data: List[ChunkNode],
        relationships: List[ChunkRelationship],
    ) -> None:
        query = """
        UNWIND $batch_data AS data
        MERGE (c:Chunk {id: data.id})
        SET c.text = data.text, c.position = data.position, c.length = data.length, 
            c.file_name = data.file_name, c.content_offset = data.content_offset,
            c.page_number = CASE WHEN data.page_number IS NOT NULL THEN data.page_number END,
            c.start_time = CASE WHEN data.start_time IS NOT NULL THEN data.start_time END,
            c.end_time = CASE WHEN data.end_time IS NOT NULL THEN data.end_time END
        WITH data, c
        MATCH (d:Document {file_name: data.file_name})
        MERGE (c)-[:PART_OF]->(d)
        WITH d
        UNWIND $relationships AS rel
        MATCH (c1:Chunk {id: rel.current_chunk_id}), (c2:Chunk {id: rel.previous_chunk_id})
        CALL {
            WITH d, c1, rel
            WITH d, c1, rel WHERE rel.type = $FIRST_CHUNK
            MERGE (d)-[:FIRST_CHUNK]->(c1)
        }
        CALL {
            WITH c1, c2, rel
            WITH c1, c2, rel WHERE rel.type = $NEXT_CHUNK
            MERGE (c2)-[:NEXT_CHUNK]->(c1)
        }
        """

        self.graph.query(
            query,
            params={
                "batch_data": [data.to_dict() for data in batch_data],
                "relationships": [rel.to_dict() for rel in relationships],
                "FIRST_CHUNK": FIRST_CHUNK,
                "NEXT_CHUNK": NEXT_CHUNK,
            },
        )
