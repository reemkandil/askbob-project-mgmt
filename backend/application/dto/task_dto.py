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