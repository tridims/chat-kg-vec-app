import logging
from typing import Any, Dict, List
from langchain_community.graphs import Neo4jGraph
import json
import os
from src.models import SourceNode
from src.utils.file_tools import delete_file


class GraphDBDataAccess:
    def __init__(self, graph: Neo4jGraph):
        self.graph = graph

    def update_exception(self, file_name: str, exp_msg: str) -> None:
        try:
            result = self.get_current_status_document_node(file_name)
            job_status = "Cancelled" if result[0]["is_cancelled"] else "Failed"

            self.graph.query(
                """
                MERGE (d:Document {fileName: $fName})
                SET d.status = $status, d.errorMessage = $error_msg
                """,
                {"fName": file_name, "status": job_status, "error_msg": exp_msg},
            )
        except Exception as e:
            logging.error(f"Error updating document node status as failed: {str(e)}")
            raise

    def create_source_node(self, obj_source_node: SourceNode) -> None:
        try:
            self.graph.query(
                """
                MERGE (d:Document {fileName: $fn})
                SET d.status = $st,
                    d.createdAt = $c_at,
                    d.updatedAt = $u_at,
                    d.errorMessage = $e_message,
                    d.nodeCount = $n_count,
                    d.relationshipCount = $r_count,
                    d.is_cancelled = False,
                    d.total_chunks = 0,
                    d.processed_chunk = 0,
                    d.total_pages = $total_pages
                """,
                {
                    "fn": obj_source_node.file_name,
                    "st": "New",
                    "c_at": obj_source_node.created_at,
                    "u_at": obj_source_node.created_at,
                    "e_message": "",
                    "n_count": 0,
                    "r_count": 0,
                    "total_pages": obj_source_node.total_pages,
                },
            )
        except Exception as e:
            logging.error(f"Error creating source node: {str(e)}")
            self.update_exception_db(obj_source_node.file_name, str(e))
            raise

    def update_source_node(self, obj_source_node: SourceNode) -> None:
        try:
            params = {
                "fileName": obj_source_node.file_name,
                "status": obj_source_node.status,
                "createdAt": obj_source_node.created_at,
                "updatedAt": obj_source_node.updated_at,
                "nodeCount": obj_source_node.node_count,
                "relationshipCount": obj_source_node.relationship_count,
                "total_pages": obj_source_node.total_pages,
                "total_chunks": obj_source_node.total_chunks,
                "processed_chunk": obj_source_node.processed_chunk,
            }
            params = {k: v for k, v in params.items() if v not in [None, "", 0]}

            self.graph.query(
                """
                MERGE (d:Document {fileName: $props.fileName})
                SET d += $props
                """,
                {"props": params},
            )
        except Exception as e:
            logging.error(f"Error updating document node status: {str(e)}")
            self.update_exception(obj_source_node.file_name, str(e))
            raise

    def get_source_list(self) -> List[Dict[str, Any]]:
        query = """
        MATCH (d:Document)
        WHERE d.fileName IS NOT NULL
        RETURN d
        ORDER BY d.updatedAt DESC
        """
        result = self.graph.query(query)
        return [entry["d"] for entry in result]

    def update_knn_graph(self) -> None:
        index = self.graph.query(
            "SHOW INDEXES YIELD * WHERE type = 'VECTOR' AND name = 'vector'"
        )
        knn_min_score = float(os.environ.get("KNN_MIN_SCORE", 0.94))

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
                {"score": knn_min_score},
            )
        else:
            logging.info("Vector index does not exist. KNN graph not updated.")

    def get_current_status_document_node(self, file_name: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (d:Document {fileName: $file_name})
        RETURN d.status AS Status,
               d.processingTime AS processingTime,
               d.nodeCount AS nodeCount,
               d.model AS model,
               d.relationshipCount AS relationshipCount,
               d.total_pages AS total_pages,
               d.total_chunks AS total_chunks,
               d.fileSize AS fileSize,
               d.is_cancelled AS is_cancelled,
               d.processed_chunk AS processed_chunk,
               d.fileSource AS fileSource
        """
        return self.graph.query(query, {"file_name": file_name})

    def delete_file_from_graph(
        self,
        filenames: str,
        source_types: str,
        delete_entities: bool,
        directory: str,
    ) -> tuple:
        filename_list = json.loads(filenames)
        source_types_list = json.loads(source_types)

        for file_name in filename_list:
            merged_file_path = os.path.join(directory, file_name)
            logging.info(
                f"Deleted File Path: {merged_file_path} and Deleted File Name: {file_name}"
            )
            delete_file(merged_file_path, file_name)

        query = self._get_delete_query(delete_entities)
        param = {"filename_list": filename_list, "source_types_list": source_types_list}

        result = self.graph.query(query, param)
        logging.info(
            f"Deleting {len(filename_list)} documents from {source_types_list}"
        )

        return result, len(filename_list)

    def _get_delete_query(self, delete_entities: bool) -> str:
        if delete_entities:
            return """
            MATCH (d:Document)
            WHERE d.fileName IN $filename_list AND d.fileSource IN $source_types_list
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
            RETURN sum(entities) AS deletedEntities, count(*) AS deletedChunks
            """
        else:
            return """
            MATCH (d:Document)
            WHERE d.fileName IN $filename_list AND d.fileSource IN $source_types_list
            WITH collect(d) AS documents
            UNWIND documents AS d
            OPTIONAL MATCH (d)<-[:PART_OF]-(c:Chunk)
            DETACH DELETE c, d
            RETURN count(*) AS deletedChunks
            """
