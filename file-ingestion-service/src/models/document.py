from datetime import datetime
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class DocumentNode:
    """A node that represents the source file
    (pdf) in which the data/graph was extracted from.
    """

    file_name: str = None
    status: str = None
    created_at: datetime = None
    updated_at: datetime = field(default_factory=datetime.now)
    node_count: int = 0
    relationship_count: int = 0
    total_pages: int = 0
    total_chunks: int = 0
    processed_chunk: int = 0

    def to_dict(self):
        return asdict(self)

    def fill_default(self):
        if not self.status:
            self.status = "NEW"
        if self.created_at is None:
            self.created_at = datetime.now()
        return self

    def to_dict_not_default(self):
        if self.created_at == self.updated_at:
            self.created_at = None
        return {k: v for k, v in asdict(self).items() if v not in [None, "", 0]}
