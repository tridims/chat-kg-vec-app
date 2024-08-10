import logging
from typing import Any, Dict, List
from langchain_community.graphs import Neo4jGraph
from langchain_community.graphs.graph_document import GraphDocument
from app.models.document import DocumentNode


class GraphDBDataAccess:
    def __init__(self, graph: Neo4jGraph):
        self.graph = graph

    def get_graphs(self):
        result = self.graph.query(
            """
            MATCH (n)
            WHERE NOT n:Document AND NOT n:Chunk AND NOT n:Session AND NOT n:Message
            WITH n
            MATCH (n)-[r]-(m)
            WHERE NOT (m:Document OR m:Chunk OR m:Session OR m:Message)
            RETURN n, labels(n) AS nodeLabels, r, m, labels(m) AS relatedNodeLabels
            """
        )
        return result

    def get_documents(self) -> List[DocumentNode]:
        result = self.graph.query(
            """
            MATCH (d:Document)
            RETURN d
            ORDER BY d.updated_at DESC
            """
        )

        docs = [DocumentNode(**record["d"]) for record in result]
        for doc in docs:
            doc.created_at = doc.created_at.to_native()
            doc.updated_at = doc.updated_at.to_native()

        return docs

    def get_document(self, file_name: str) -> List[DocumentNode]:
        result = self.graph.query(
            """
            MATCH (d:Document {file_name: $file_name})
            RETURN d
            """,
            {"file_name": file_name},
        )
        return DocumentNode(**result[0]["d"])

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

    def create_vector_index(self):
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
            {"dimension": 768},  # TODO: Change this to a config value
        )
