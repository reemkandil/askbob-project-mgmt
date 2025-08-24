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

# backend/domain/repositories/tenant_repository.py
from abc import abstractmethod
from typing import Optional
from .base import BaseRepository
from ..entities.tenant import Tenant

class TenantRepository(BaseRepository[Tenant]):
    @abstractmethod
    async def get_by_domain(self, domain: str) -> Optional[Tenant]:
        pass

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

# backend/domain/repositories/project_repository.py
from abc import abstractmethod
from typing import List
import uuid
from .base import BaseRepository
from ..entities.project import Project, ProjectStatus

class ProjectRepository(BaseRepository[Project]):
    @abstractmethod
    async def get_by_tenant(self, tenant_id: uuid.UUID) -> List[Project]:
        pass
    
    @abstractmethod
    async def get_by_tenant_and_id(self, tenant_id: uuid.UUID, project_id: uuid.UUID) -> Project:
        pass
    
    @abstractmethod
    async def get_by_status(self, tenant_id: uuid.UUID, status: ProjectStatus) -> List[Project]:
        pass

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

# backend/domain/repositories/__init__.py
from .tenant_repository import TenantRepository
from .user_repository import UserRepository
from .project_repository import ProjectRepository
from .task_repository import TaskRepository

__all__ = [
    "TenantRepository",
    "UserRepository", 
    "ProjectRepository",
    "TaskRepository"
]