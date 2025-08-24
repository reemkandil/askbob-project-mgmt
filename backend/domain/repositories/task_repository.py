# backend/domain/repositories/task_repository.py
from abc import abstractmethod
from typing import List, Optional
import uuid
from .base import BaseRepository
from ..entities.task import Task, TaskStatus

class TaskRepository(BaseRepository[Task]):
    @abstractmethod
    async def get_by_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> List[Task]:
        pass
    
    @abstractmethod
    async def get_by_assignee(self, user_id: uuid.UUID, tenant_id: uuid.UUID) -> List[Task]:
        pass
    
    @abstractmethod
    async def get_by_tenant_and_id(self, tenant_id: uuid.UUID, task_id: uuid.UUID) -> Optional[Task]:
        pass
    
    @abstractmethod
    async def get_by_status(self, tenant_id: uuid.UUID, status: TaskStatus) -> List[Task]:
        pass