# backend/domain/repositories/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
import uuid

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        pass