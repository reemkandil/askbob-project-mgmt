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