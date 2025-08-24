# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import projects, tasks
from infrastructure.database.connection import engine
from infrastructure.database.models import Base

app = FastAPI(
    title="AskBob Project Management API",
    description="Multi-tenant project management system with Clean Architecture",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])

@app.get("/")
async def root():
    return {"message": "AskBob Project Management API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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

# backend/api/routes/projects.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from application.use_cases.project_use_cases import ProjectUseCases
from application.dto.project_dto import CreateProjectRequest, UpdateProjectRequest, ProjectResponse
from api.dependencies import get_project_use_cases, get_current_tenant, get_current_user

router = APIRouter()

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    project_use_cases: ProjectUseCases = Depends(get_project_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    user_id: uuid.UUID = Depends(get_current_user)
):
    """Create a new project"""
    try:
        project = await project_use_cases.create_project(
            name=request.name,
            tenant_id=tenant_id,
            created_by=user_id,
            description=request.description
        )
        
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            tenant_id=project.tenant_id,
            created_by=project.created_by,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    project_use_cases: ProjectUseCases = Depends(get_project_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Get all projects for the current tenant"""
    projects = await project_use_cases.get_projects_by_tenant(tenant_id)
    
    return [
        ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            tenant_id=project.tenant_id,
            created_by=project.created_by,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
        for project in projects
    ]

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    project_use_cases: ProjectUseCases = Depends(get_project_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Get a specific project"""
    try:
        project = await project_use_cases.get_project(project_id, tenant_id)
        
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            tenant_id=project.tenant_id,
            created_by=project.created_by,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    request: UpdateProjectRequest,
    project_use_cases: ProjectUseCases = Depends(get_project_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Update a project"""
    try:
        project = await project_use_cases.update_project(
            project_id=project_id,
            tenant_id=tenant_id,
            name=request.name,
            description=request.description,
            status=request.status
        )
        
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            tenant_id=project.tenant_id,
            created_by=project.created_by,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    project_use_cases: ProjectUseCases = Depends(get_project_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Delete a project"""
    try:
        success = await project_use_cases.delete_project(project_id, tenant_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# backend/api/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from application.use_cases.task_use_cases import TaskUseCases
from application.dto.task_dto import CreateTaskRequest, UpdateTaskRequest, TaskResponse
from api.dependencies import get_task_use_cases, get_current_tenant, get_current_user

router = APIRouter()

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: uuid.UUID,
    request: CreateTaskRequest,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    user_id: uuid.UUID = Depends(get_current_user)
):
    """Create a new task in a project"""
    try:
        task = await task_use_cases.create_task(
            title=request.title,
            project_id=project_id,
            tenant_id=tenant_id,
            created_by=user_id,
            description=request.description,
            priority=request.priority,
            assigned_to=request.assigned_to,
            due_date=request.due_date
        )
        
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            project_id=task.project_id,
            tenant_id=task.tenant_id,
            created_by=task.created_by,
            assigned_to=task.assigned_to,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def list_tasks_by_project(
    project_id: uuid.UUID,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Get all tasks for a project"""
    try:
        tasks = await task_use_cases.get_tasks_by_project(project_id, tenant_id)
        
        return [
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                project_id=task.project_id,
                tenant_id=task.tenant_id,
                created_by=task.created_by,
                assigned_to=task.assigned_to,
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in tasks
        ]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    request: UpdateTaskRequest,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Update a task"""
    try:
        task = await task_use_cases.update_task(
            task_id=task_id,
            tenant_id=tenant_id,
            title=request.title,
            description=request.description,
            status=request.status,
            priority=request.priority,
            assigned_to=request.assigned_to,
            due_date=request.due_date
        )
        
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            project_id=task.project_id,
            tenant_id=task.tenant_id,
            created_by=task.created_by,
            assigned_to=task.assigned_to,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Delete a task"""
    try:
        success = await task_use_cases.delete_task(task_id, tenant_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))