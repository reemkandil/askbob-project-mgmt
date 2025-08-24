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