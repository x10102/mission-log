from dataclasses import dataclass
from enum import IntEnum
from datetime import datetime

from flask_login import UserMixin

class UserRole(IntEnum):
    OWNER = 1,
    USER = 2

@dataclass
class User(UserMixin):
    login: str
    password: bytes
    role: UserRole
    uid: int = 0
    def get_id(self) -> str:
        return str(self.uid)
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, User):
            return self.uid == __value.uid
        elif isinstance(__value, int):
            return self.uid == __value
        else:
            return False