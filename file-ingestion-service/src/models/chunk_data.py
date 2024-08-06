from dataclasses import dataclass
from typing import Optional
from langchain.docstore.document import Document


@dataclass
class ChunkData:
    id: str
    pg_content: str
    position: int
    length: int
    f_name: str
    previous_id: str
    content_offset: int
    page_number: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class Relationship:
    type: str
    previous_chunk_id: str
    current_chunk_id: str


@dataclass
class ChunkIdDocPair:
    chunk_id: str
    chunk_doc: Document
