# backend/domain/entities/project.py
from datetime import datetime
from typing import Optional
import uuid
from enum import Enum

class ProjectStatus(Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Project:
    def __init__(
        self,
        name: str,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        description: Optional[str] = None,
        status: ProjectStatus = ProjectStatus.PLANNING,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or uuid.uuid4()
        self.name = name
        self.tenant_id = tenant_id
        self.created_by = created_by
        self.description = description
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Business rules
        if not name or len(name.strip()) == 0:
            raise ValueError("Project name cannot be empty")
        if len(name) > 200:
            raise ValueError("Project name cannot exceed 200 characters")

    def update_status(self, new_status: ProjectStatus) -> None:
        """Business logic for status transitions"""
        if self.status == ProjectStatus.CANCELLED and new_status != ProjectStatus.PLANNING:
            raise ValueError("Cannot change status of cancelled project except back to planning")
        
        self.status = new_status
        self.updated_at = datetime.utcnow()