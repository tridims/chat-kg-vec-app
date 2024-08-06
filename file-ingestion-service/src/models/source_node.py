from datetime import datetime
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SourceNode:
    """A node that represents the source file
    (pdf) in which the data/graph was extracted from.
    """

    file_name: str = None
    status: str = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    node_count: int = None
    relationship_count: int = None
    total_pages: int = None
    total_chunks: int = None
    processed_chunk: int = None
