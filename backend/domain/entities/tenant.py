# backend/domain/entities/tenant.py
from datetime import datetime
from typing import Optional
import uuid

class Tenant:
    def __init__(
        self,
        name: str,
        domain: str,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id or uuid.uuid4()
        self.name = name
        self.domain = domain
        self.created_at = created_at or datetime.utcnow()
        
        # Business rules
        if not name or len(name.strip()) == 0:
            raise ValueError("Tenant name cannot be empty")
        if not domain or len(domain.strip()) == 0:
            raise ValueError("Tenant domain cannot be empty")

# backend/domain/entities/user.py
from datetime import datetime
from typing import Optional
import uuid

class User:
    def __init__(
        self,
        email: str,
        tenant_id: uuid.UUID,
        hashed_password: str,
        first_name: str,
        last_name: str,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        is_active: bool = True
    ):
        self.id = id or uuid.uuid4()
        self.email = email
        self.tenant_id = tenant_id
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = created_at or datetime.utcnow()
        self.is_active = is_active
        
        # Business rules
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        if not first_name or len(first_name.strip()) == 0:
            raise ValueError("First name cannot be empty")

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

# backend/domain/entities/task.py
from datetime import datetime
from typing import Optional
import uuid
from enum import Enum

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task:
    def __init__(
        self,
        title: str,
        project_id: uuid.UUID,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.TODO,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_to: Optional[uuid.UUID] = None,
        due_date: Optional[datetime] = None,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or uuid.uuid4()
        self.title = title
        self.project_id = project_id
        self.tenant_id = tenant_id
        self.created_by = created_by
        self.description = description
        self.status = status
        self.priority = priority
        self.assigned_to = assigned_to
        self.due_date = due_date
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Business rules
        if not title or len(title.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        if len(title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")

    def assign_to_user(self, user_id: uuid.UUID) -> None:
        """Assign task to a user"""
        self.assigned_to = user_id
        self.updated_at = datetime.utcnow()

    def update_status(self, new_status: TaskStatus) -> None:
        """Update task status with business logic"""
        # Business rule: Can't go from DONE back to TODO directly
        if self.status == TaskStatus.DONE and new_status == TaskStatus.TODO:
            raise ValueError("Cannot move completed task back to TODO. Move to IN_PROGRESS first.")
        
        self.status = new_status
        self.updated_at = datetime.utcnow()

# backend/domain/entities/__init__.py
from .tenant import Tenant
from .user import User
from .project import Project, ProjectStatus
from .task import Task, TaskStatus, TaskPriority

__all__ = [
    "Tenant",
    "User", 
    "Project",
    "ProjectStatus",
    "Task",
    "TaskStatus",
    "TaskPriority"
]