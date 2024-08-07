from src.config import PARALLEL_BATCH_SIZE
from src.llm import get_embedding_model
from src.models.chunk_data import ChunkIdDocPair
from src.utils.chunker import batch
from langchain_community.graphs import Neo4jGraph
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any


def update_embedding_create_vector_index(
    graph: Neo4jGraph,
    chunkId_chunkDoc_list: List[ChunkIdDocPair],
    file_name: str,
    batch_size: int = PARALLEL_BATCH_SIZE,
):
    embeddings_model, dimension = get_embedding_model()

    def create_vector_index():
        graph.query(
            """
            CREATE VECTOR INDEX vector IF NOT EXISTS FOR (c:Chunk) ON (c.embedding)
            OPTIONS {
                indexConfig: {
                    `vector.dimensions`: $dimensions,
                    `vector.similarity_function`: 'cosine'
                }
            }
            """,
            {"dimensions": dimension},
        )

    def process_batch(batch: List[ChunkIdDocPair]):
        embedded_batch = [
            {
                "chunkId": row.chunk_id,
                "embeddings": embeddings_model.embed_query(row.chunk_doc.page_content),
            }
            for row in batch
        ]

        graph.query(
            """
            UNWIND $data AS row
            MATCH (d:Document {fileName: $fileName})
            MERGE (c:Chunk {id: row.chunkId})
            SET c.embedding = row.embeddings
            MERGE (c)-[:PART_OF]->(d)
            """,
            params={"fileName": file_name, "data": embedded_batch},
        )

    # Create vector index
    create_vector_index()

    # Process chunks in batches
    with ThreadPoolExecutor() as executor:
        futures = []
        for _, _, data in batch(chunkId_chunkDoc_list, batch_size):
            futures.append(executor.submit(process_batch, data))

        for future in as_completed(futures):
            future.result()  # This will raise any exceptions that occurred during execution
