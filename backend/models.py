from dataclasses import dataclass, field, asdict
from datetime import datetime
from uuid import uuid4


@dataclass
class TodoItem:
    content: str
    priority: str  # urgent_important | urgent_not_important | not_urgent_important | not_urgent_not_important
    period: str    # daily | weekly | monthly
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "active"  # active | completed | uncompleted

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TodoItem":
        return cls(**data)
