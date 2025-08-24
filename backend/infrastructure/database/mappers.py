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
    def to_model(entity: Tenant) -> TenantModel:
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
        )