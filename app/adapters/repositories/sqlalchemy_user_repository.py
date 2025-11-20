from typing import Optional
from app.core.entities.user_entity import UserEntity
from app.core.interfaces.user_repository import UserRepository
from app.models import User

class SqlAlchemyUserRepository(UserRepository):
    def _to_entity(self, model: User) -> UserEntity:
        return UserEntity(
            id=model.id,
            username=model.username,
            email=model.email,
        )

    def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        model = User.query.get(user_id)
        return self._to_entity(model) if model else None
