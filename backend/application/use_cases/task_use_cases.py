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