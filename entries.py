from dataclasses import dataclass
from datetime import datetime

from users import User

@dataclass
class Entry():
    text: str
    author: User
    private: bool
    timestamp: datetime
    eid: int = 0