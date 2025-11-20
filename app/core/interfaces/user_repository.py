from abc import ABC, abstractmethod
from typing import Optional
from app.core.entities.user_entity import UserEntity

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        raise NotImplementedError
