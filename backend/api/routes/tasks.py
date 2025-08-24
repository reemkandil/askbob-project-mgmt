"""Task management API routes."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.task_dto import TaskCreateDTO, TaskUpdateDTO, TaskResponseDTO
from application.use_cases.task_use_cases import TaskUseCases
from infrastructure.database.connection import get_db_session
from infrastructure.database.repositories.task_repository import TaskRepository

router = APIRouter(prefix="/api/v1", tags=["tasks"])


def get_task_use_cases(db: AsyncSession = Depends(get_db_session)) -> TaskUseCases:
    """Dependency to get task use cases."""
    task_repository = TaskRepository(db)
    return TaskUseCases(task_repository)


@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponseDTO])
async def get_project_tasks(
    project_id: UUID,
    tenant_id: str = "default",  # In production, get from JWT token
    task_use_cases: TaskUseCases = Depends(get_task_use_cases)
):
    """Get all tasks for a specific project."""
    try:
        tasks = await task_use_cases.get_project_tasks(project_id, tenant_id)
        return [TaskResponseDTO.from_entity(task) for task in tasks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )


@router.post("/projects/{project_id}/tasks", response_model=TaskResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: UUID,
    task_data: TaskCreateDTO,
    tenant_id: str = "default",  # In production, get from JWT token
    task_use_cases: TaskUseCases = Depends(get_task_use_cases)
):
    """Create a new task in a project."""
    try:
        task = await task_use_cases.create_task(project_id, task_data, tenant_id)
        return TaskResponseDTO.from_entity(task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskResponseDTO)
async def get_task(
    task_id: UUID,
    tenant_id: str = "default",  # In production, get from JWT token
    task_use_cases: TaskUseCases = Depends(get_task_use_cases)
):
    """Get a specific task by ID."""
    try:
        task = await task_use_cases.get_task_by_id(task_id, tenant_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return TaskResponseDTO.from_entity(task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task: {str(e)}"
        )


@router.put("/tasks/{task_id}", response_model=TaskResponseDTO)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdateDTO,
    tenant_id: str = "default",  # In production, get from JWT token
    task_use_cases: TaskUseCases = Depends(get_task_use_cases)
):
    """Update a specific task."""
    try:
        task = await task_use_cases.update_task(task_id, task_data, tenant_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return TaskResponseDTO.from_entity(task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    tenant_id: str = "default",  # In production, get from JWT token
    task_use_cases: TaskUseCases = Depends(get_task_use_cases)
):
    """Delete a specific task."""
    try:
        success = await task_use_cases.delete_task(task_id, tenant_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )