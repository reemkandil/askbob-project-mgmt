# backend/application/dto/project_dto.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import uuid
from domain.entities.project import ProjectStatus

class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None

class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    status: ProjectStatus
    tenant_id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# backend/application/dto/task_dto.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import uuid
from domain.entities.task import TaskStatus, TaskPriority

class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None

class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    project_id: uuid.UUID
    tenant_id: uuid.UUID
    created_by: uuid.UUID
    assigned_to: Optional[uuid.UUID]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# backend/application/use_cases/project_use_cases.py
from typing import List
import uuid
from domain.entities.project import Project
from domain.repositories.project_repository import ProjectRepository

class ProjectUseCases:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    async def create_project(
        self, 
        name: str, 
        tenant_id: uuid.UUID, 
        created_by: uuid.UUID,
        description: str = None
    ) -> Project:
        """Create a new project with tenant isolation"""
        project = Project(
            name=name,
            tenant_id=tenant_id,
            created_by=created_by,
            description=description
        )
        
        return await self.project_repository.create(project)

    async def get_projects_by_tenant(self, tenant_id: uuid.UUID) -> List[Project]:
        """Get all projects for a specific tenant"""
        return await self.project_repository.get_by_tenant(tenant_id)

    async def get_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> Project:
        """Get a specific project ensuring tenant isolation"""
        project = await self.project_repository.get_by_tenant_and_id(tenant_id, project_id)
        if not project:
            raise ValueError("Project not found or access denied")
        return project

    async def update_project(
        self, 
        project_id: uuid.UUID, 
        tenant_id: uuid.UUID,
        name: str = None,
        description: str = None,
        status = None
    ) -> Project:
        """Update a project ensuring tenant isolation"""
        project = await self.get_project(project_id, tenant_id)
        
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if status is not None:
            project.update_status(status)
            
        return await self.project_repository.update(project)

    async def delete_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
        """Delete a project ensuring tenant isolation"""
        project = await self.get_project(project_id, tenant_id)
        return await self.project_repository.delete(project.id)

# backend/application/use_cases/task_use_cases.py
from typing import List, Optional
import uuid
from domain.entities.task import Task, TaskStatus
from domain.repositories.task_repository import TaskRepository
from domain.repositories.project_repository import ProjectRepository

class TaskUseCases:
    def __init__(
        self, 
        task_repository: TaskRepository,
        project_repository: ProjectRepository
    ):
        self.task_repository = task_repository
        self.project_repository = project_repository

    async def create_task(
        self,
        title: str,
        project_id: uuid.UUID,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        description: str = None,
        priority = None,
        assigned_to: uuid.UUID = None,
        due_date = None
    ) -> Task:
        """Create a new task ensuring project belongs to tenant"""
        # Verify project belongs to tenant
        project = await self.project_repository.get_by_tenant_and_id(tenant_id, project_id)
        if not project:
            raise ValueError("Project not found or access denied")

        task = Task(
            title=title,
            project_id=project_id,
            tenant_id=tenant_id,
            created_by=created_by,
            description=description,
            priority=priority,
            assigned_to=assigned_to,
            due_date=due_date
        )
        
        return await self.task_repository.create(task)

    async def get_tasks_by_project(
        self, 
        project_id: uuid.UUID, 
        tenant_id: uuid.UUID
    ) -> List[Task]:
        """Get all tasks for a project ensuring tenant isolation"""
        # Verify project belongs to tenant
        project = await self.project_repository.get_by_tenant_and_id(tenant_id, project_id)
        if not project:
            raise ValueError("Project not found or access denied")
        
        return await self.task_repository.get_by_project(project_id, tenant_id)

    async def get_task(
        self, 
        task_id: uuid.UUID, 
        tenant_id: uuid.UUID
    ) -> Optional[Task]:
        """Get a specific task ensuring tenant isolation"""
        return await self.task_repository.get_by_tenant_and_id(tenant_id, task_id)

    async def update_task(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
        title: str = None,
        description: str = None,
        status: TaskStatus = None,
        priority = None,
        assigned_to: uuid.UUID = None,
        due_date = None
    ) -> Task:
        """Update a task ensuring tenant isolation"""
        task = await self.get_task(task_id, tenant_id)
        if not task:
            raise ValueError("Task not found or access denied")

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.update_status(status)
        if priority is not None:
            task.priority = priority
        if assigned_to is not None:
            task.assign_to_user(assigned_to)
        if due_date is not None:
            task.due_date = due_date

        return await self.task_repository.update(task)

    async def delete_task(self, task_id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
        """Delete a task ensuring tenant isolation"""
        task = await self.get_task(task_id, tenant_id)
        if not task:
            raise ValueError("Task not found or access denied")
        
        return await self.task_repository.delete(task.id)

# backend/application/use_cases/__init__.py
from .project_use_cases import ProjectUseCases
from .task_use_cases import TaskUseCases

__all__ = ["ProjectUseCases", "TaskUseCases"]