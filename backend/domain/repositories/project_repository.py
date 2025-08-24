# backend/domain/repositories/project_repository.py
from abc import abstractmethod
from typing import List, Optional
import uuid
from .base import BaseRepository
from ..entities.project import Project, ProjectStatus

class ProjectRepository(BaseRepository[Project]):
    @abstractmethod
    async def get_by_tenant(self, tenant_id: uuid.UUID) -> List[Project]:
        pass
    
    @abstractmethod
    async def get_by_tenant_and_id(self, tenant_id: uuid.UUID, project_id: uuid.UUID) -> Optional[Project]:
        pass
    
    @abstractmethod
    async def get_by_status(self, tenant_id: uuid.UUID, status: ProjectStatus) -> List[Project]:
        pass