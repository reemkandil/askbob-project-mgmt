# backend/application/use_cases/project_use_cases.py
from typing import List
import uuid
from domain.entities.project import Project
from domain.repositories.project_repository import ProjectRepository

class ProjectUseCases:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    async def create_project(
        self, 
        name: str, 
        tenant_id: uuid.UUID, 
        created_by: uuid.UUID,
        description: str = None
    ) -> Project:
        """Create a new project with tenant isolation"""
        project = Project(
            name=name,
            tenant_id=tenant_id,
            created_by=created_by,
            description=description
        )
        
        return await self.project_repository.create(project)

    async def get_projects_by_tenant(self, tenant_id: uuid.UUID) -> List[Project]:
        """Get all projects for a specific tenant"""
        return await self.project_repository.get_by_tenant(tenant_id)

    async def get_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> Project:
        """Get a specific project ensuring tenant isolation"""
        project = await self.project_repository.get_by_tenant_and_id(tenant_id, project_id)
        if not project:
            raise ValueError("Project not found or access denied")
        return project

    async def update_project(
        self, 
        project_id: uuid.UUID, 
        tenant_id: uuid.UUID,
        name: str = None,
        description: str = None,
        status = None
    ) -> Project:
        """Update a project ensuring tenant isolation"""
        project = await self.get_project(project_id, tenant_id)
        
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if status is not None:
            project.update_status(status)
            
        return await self.project_repository.update(project)

    async def delete_project(self, project_id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
        """Delete a project ensuring tenant isolation"""
        project = await self.get_project(project_id, tenant_id)
        return await self.project_repository.delete(project.id)