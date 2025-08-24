# backend/infrastructure/database/repositories/task_repository_impl.py
from typing import List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.task import Task, TaskStatus
from domain.repositories.task_repository import TaskRepository
from ..models import TaskModel
from ..mappers import TaskMapper

class TaskRepositoryImpl(TaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: Task) -> Task:
        model = TaskMapper.to_model(entity)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return TaskMapper.to_domain(model)

    async def get_by_id(self, id: uuid.UUID) -> Optional[Task]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == id)
        )
        model = result.scalar_one_or_none()
        return TaskMapper.to_domain(model) if model else None

    async def get_by_tenant_and_id(self, tenant_id: uuid.UUID, task_id: uuid.UUID) -> Optional[Task]:
        result = await self.session.execute(
            select(TaskModel).where(
                TaskModel.tenant_id == tenant_id,
                TaskModel.id == task_id
            )
        )
        model = result.scalar_one_or_none()
        return TaskMapper.to_domain(model) if model else None

    async def get_by_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> List[Task]:
        result = await self.session.execute(
            select(TaskModel).where(
                TaskModel.project_id == project_id,
                TaskModel.tenant_id == tenant_id
            )
        )
        models = result.scalars().all()
        return [TaskMapper.to_domain(model) for model in models]

    async def get_by_assignee(self, user_id: uuid.UUID, tenant_id: uuid.UUID) -> List[Task]:
        result = await self.session.execute(
            select(TaskModel).where(
                TaskModel.assigned_to == user_id,
                TaskModel.tenant_id == tenant_id
            )
        )
        models = result.scalars().all()
        return [TaskMapper.to_domain(model) for model in models]

    async def get_by_status(self, tenant_id: uuid.UUID, status: TaskStatus) -> List[Task]:
        result = await self.session.execute(
            select(TaskModel).where(
                TaskModel.tenant_id == tenant_id,
                TaskModel.status == status
            )
        )
        models = result.scalars().all()
        return [TaskMapper.to_domain(model) for model in models]

    async def update(self, entity: Task) -> Task:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError("Task not found")
        
        # Update fields
        model.title = entity.title
        model.description = entity.description
        model.status = entity.status
        model.priority = entity.priority
        model.assigned_to = entity.assigned_to
        model.due_date = entity.due_date
        model.updated_at = entity.updated_at
        
        await self.session.commit()
        await self.session.refresh(model)
        return TaskMapper.to_domain(model)

    async def delete(self, id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True