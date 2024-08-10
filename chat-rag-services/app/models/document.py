from dataclasses import dataclass, field
import datetime


@dataclass
class DocumentNode:
    """A node that represents the source file
    (pdf) in which the data/graph was extracted from.
    """

    file_name: str = None
    status: str = None
    created_at: datetime = None
    updated_at: datetime = None
    node_count: int = 0
    relationship_count: int = 0
    total_pages: int = 0
    total_chunks: int = 0
    processed_chunk: int = 0
