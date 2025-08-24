# backend/api/dependencies.py
from functools import lru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.connection import get_db_session
from infrastructure.database.repositories.project_repository_impl import ProjectRepositoryImpl
from infrastructure.database.repositories.task_repository_impl import TaskRepositoryImpl
from application.use_cases.project_use_cases import ProjectUseCases
from application.use_cases.task_use_cases import TaskUseCases
import uuid

# For now, we'll use a mock tenant_id. In a real app, this would come from JWT token
MOCK_TENANT_ID = uuid.uuid4()
MOCK_USER_ID = uuid.uuid4()

async def get_project_repository(session: AsyncSession = Depends(get_db_session)):
    return ProjectRepositoryImpl(session)

async def get_task_repository(session: AsyncSession = Depends(get_db_session)):
    return TaskRepositoryImpl(session)

async def get_project_use_cases(
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository)
):
    return ProjectUseCases(project_repo)

async def get_task_use_cases(
    task_repo: TaskRepositoryImpl = Depends(get_task_repository),
    project_repo: ProjectRepositoryImpl = Depends(get_project_repository)
):
    return TaskUseCases(task_repo, project_repo)

# Mock authentication - in real app, decode JWT token
async def get_current_tenant() -> uuid.UUID:
    return MOCK_TENANT_ID

async def get_current_user() -> uuid.UUID:
    return MOCK_USER_ID