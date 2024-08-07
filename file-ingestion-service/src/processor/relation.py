import hashlib
from typing import List
from langchain.docstore.document import Document
from src.models.chunk_data import ChunkData, ChunkIdDocPair, Relationship

FIRST_CHUNK = "FIRST_CHUNK"
NEXT_CHUNK = "NEXT_CHUNK"


def _process_chunks(
    chunks: List[Document], file_name: str
) -> tuple[List[ChunkData], List[Relationship]]:
    batch_data = []
    relationships = []
    current_chunk_id = ""
    offset = 0

    for i, chunk in enumerate(chunks):
        page_content_sha1 = hashlib.sha1(chunk.page_content.encode()).hexdigest()
        previous_chunk_id = current_chunk_id
        current_chunk_id = page_content_sha1
        position = i + 1
        offset += len(chunks[i - 1].page_content) if i > 0 else 0

        chunk_data = ChunkData(
            id=current_chunk_id,
            pg_content=chunk.page_content,
            position=position,
            length=len(chunk.page_content),
            f_name=file_name,
            previous_id=previous_chunk_id,
            content_offset=offset,
            **{
                k: v
                for k, v in chunk.metadata.items()
                if k in ["page_number", "start_time", "end_time"]
            }
        )

        batch_data.append(chunk_data)
        relationships.append(
            Relationship(
                type=FIRST_CHUNK if i == 0 else NEXT_CHUNK,
                previous_chunk_id=previous_chunk_id,
                current_chunk_id=current_chunk_id,
            )
        )

    return batch_data, relationships


def create_relation_between_chunks(
    graph, file_name: str, chunks: List[Document]
) -> List[ChunkIdDocPair]:
    batch_data, relationships = _process_chunks(chunks, file_name)

    query = """
    UNWIND $batch_data AS data
    MERGE (c:Chunk {id: data.id})
    SET c.text = data.pg_content, c.position = data.position, c.length = data.length, 
        c.fileName = data.f_name, c.content_offset = data.content_offset,
        c.page_number = CASE WHEN data.page_number IS NOT NULL THEN data.page_number END,
        c.start_time = CASE WHEN data.start_time IS NOT NULL THEN data.start_time END,
        c.end_time = CASE WHEN data.end_time IS NOT NULL THEN data.end_time END
    WITH data, c
    MATCH (d:Document {fileName: data.f_name})
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

    graph.query(
        query,
        params={
            "batch_data": [vars(data) for data in batch_data],
            "relationships": [vars(rel) for rel in relationships],
            "FIRST_CHUNK": FIRST_CHUNK,
            "NEXT_CHUNK": NEXT_CHUNK,
        },
    )

    return [
        ChunkIdDocPair(chunk_id=data.id, chunk_doc=chunk)
        for data, chunk in zip(batch_data, chunks)
    ]
