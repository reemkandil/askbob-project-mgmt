# backend/api/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from infrastructure.database.connection import get_db_session
from infrastructure.database.repositories.project_repository_impl import ProjectRepositoryImpl
from infrastructure.database.repositories.task_repository_impl import TaskRepositoryImpl
from application.use_cases.project_use_cases import ProjectUseCases
from application.use_cases.task_use_cases import TaskUseCases
from .auth_middleware import get_current_tenant_id, get_current_user_id

# Repository Dependencies
async def get_project_repository(session: AsyncSession = Depends(get_db_session)):
    return ProjectRepositoryImpl(session)

async def get_task_repository(session: AsyncSession = Depends(get_db_session)):
    return TaskRepositoryImpl(session)

# Use Case Dependencies
async def get_project_use_cases(
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository)
):
    return ProjectUseCases(project_repo)

async def get_task_use_cases(
    task_repo: TaskRepositoryImpl = Depends(get_task_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository)
):
    return TaskUseCases(task_repo, project_repo)

# Authentication Dependencies - Replace the mock ones
async def get_current_tenant(tenant_id: uuid.UUID = Depends(get_current_tenant_id)) -> uuid.UUID:
    """Get current tenant ID from JWT token"""
    return tenant_id

async def get_current_user(user_id: uuid.UUID = Depends(get_current_user_id)) -> uuid.UUID:
    """Get current user ID from JWT token"""
    return user_id