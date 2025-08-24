# backend/domain/repositories/user_repository.py
from abc import abstractmethod
from typing import Optional, List
import uuid
from .base import BaseRepository
from ..entities.user import User

class UserRepository(BaseRepository[User]):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_tenant(self, tenant_id: uuid.UUID) -> List[User]:
        pass
    
    @abstractmethod
    async def get_by_email_and_tenant(self, email: str, tenant_id: uuid.UUID) -> Optional[User]:
        pass