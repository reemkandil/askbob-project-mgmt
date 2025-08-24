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