from dataclasses import dataclass, asdict
from typing import Optional
from langchain.docstore.document import Document
from langchain_community.graphs.graph_document import GraphDocument


@dataclass
class ChunkNode:
    id: str
    text: str
    position: int
    length: int
    file_name: str
    previous_id: str
    content_offset: int
    page_number: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class ChunkRelationship:
    type: str
    previous_chunk_id: str
    current_chunk_id: str

    def to_dict(self):
        return asdict(self)


@dataclass
class ChunkDocument:
    chunk_id: str
    chunk_doc: Document


@dataclass
class ChunkEmbedding:
    chunk_id: str
    embedding: list

    def to_dict(self):
        return asdict(self)


@dataclass
class ChunkEntityRelationship:
    chunk_id: str
    entity_type: str
    entity_id: str


@dataclass
class ChunkGraphDocumentPair:
    chunk_id: str
    graph_document: GraphDocument

    def to_dict(self):
        return asdict(self)
