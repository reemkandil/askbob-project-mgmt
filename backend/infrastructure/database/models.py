# backend/infrastructure/database/models.py
from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

from domain.entities.project import ProjectStatus
from domain.entities.task import TaskStatus, TaskPriority

Base = declarative_base()

class TenantModel(Base):
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    domain = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    users = relationship("UserModel", back_populates="tenant")
    projects = relationship("ProjectModel", back_populates="tenant")
    tasks = relationship("TaskModel", back_populates="tenant")

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="users")
    created_projects = relationship("ProjectModel", back_populates="creator")
    created_tasks = relationship("TaskModel", foreign_keys="TaskModel.created_by", back_populates="creator")
    assigned_tasks = relationship("TaskModel", foreign_keys="TaskModel.assigned_to", back_populates="assignee")
    
    # Unique constraint on email per tenant
    __table_args__ = (
        {"schema": None}  # Add unique constraint in Alembic migration
    )

class ProjectModel(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNING)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="projects")
    creator = relationship("UserModel", back_populates="created_projects")
    tasks = relationship("TaskModel", back_populates="project")

class TaskModel(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.TODO)
    priority = Column(SQLEnum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("ProjectModel", back_populates="tasks")
    tenant = relationship("TenantModel", back_populates="tasks")
    creator = relationship("UserModel", foreign_keys=[created_by], back_populates="created_tasks")
    assignee = relationship("UserModel", foreign_keys=[assigned_to], back_populates="assigned_tasks")

# backend/infrastructure/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/askbob_db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Use NullPool for async
    echo=True,  # Set to False in production
)

# Create session factory
AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_session() -> AsyncSession:
    """Dependency for getting database session"""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()

# backend/infrastructure/database/mappers.py
"""
Mappers to convert between domain entities and database models
"""
from typing import List
from domain.entities.tenant import Tenant
from domain.entities.user import User
from domain.entities.project import Project
from domain.entities.task import Task
from .models import TenantModel, UserModel, ProjectModel, TaskModel

class TenantMapper:
    @staticmethod
    def to_domain(model: TenantModel) -> Tenant:
        return Tenant(
            id=model.id,
            name=model.name,
            domain=model.domain,
            created_at=model.created_at
        )
    
    @staticmethod
    def to_model(entity: Project) -> ProjectModel:
        return ProjectModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            status=entity.status,
            tenant_id=entity.tenant_id,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

class TaskMapper:
    @staticmethod
    def to_domain(model: TaskModel) -> Task:
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            status=model.status,
            priority=model.priority,
            project_id=model.project_id,
            tenant_id=model.tenant_id,
            created_by=model.created_by,
            assigned_to=model.assigned_to,
            due_date=model.due_date,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    @staticmethod
    def to_model(entity: Task) -> TaskModel:
        return TaskModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            status=entity.status,
            priority=entity.priority,
            project_id=entity.project_id,
            tenant_id=entity.tenant_id,
            created_by=entity.created_by,
            assigned_to=entity.assigned_to,
            due_date=entity.due_date,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )(entity: Tenant) -> TenantModel:
        return TenantModel(
            id=entity.id,
            name=entity.name,
            domain=entity.domain,
            created_at=entity.created_at
        )

class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            tenant_id=model.tenant_id,
            hashed_password=model.hashed_password,
            first_name=model.first_name,
            last_name=model.last_name,
            is_active=model.is_active,
            created_at=model.created_at
        )
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            tenant_id=entity.tenant_id,
            hashed_password=entity.hashed_password,
            first_name=entity.first_name,
            last_name=entity.last_name,
            is_active=entity.is_active,
            created_at=entity.created_at
        )

class ProjectMapper:
    @staticmethod
    def to_domain(model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            status=model.status,
            tenant_id=model.tenant_id,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    @staticmethod
    def to_model