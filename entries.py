from dataclasses import dataclass
from datetime import datetime

from users import User

@dataclass
class Entry():
    text: str
    author: User
    timestamp: datetime = datetime.now()
    eid: int = 0