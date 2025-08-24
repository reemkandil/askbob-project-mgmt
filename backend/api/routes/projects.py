# backend/api/routes/projects.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from application.use_cases.project_use_cases import ProjectUseCases
from application.dto.project_dto import CreateProjectRequest, UpdateProjectRequest, ProjectResponse
from api.dependencies import get_project_use_cases, get_current_tenant, get_current_user

router = APIRouter()

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    project_use_cases: ProjectUseCases = Depends(get_project_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    user_id: uuid.UUID = Depends(get_current_user)
):
    """Create a new project"""
    try:
        project = await project_use_cases.create_project(
            name=request.name,
            tenant_id=tenant_id,
            created_by=user_id,
            description=request.description
        )
        
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            tenant_id=project.tenant_id,
            created_by=project.created_by,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    project_use_cases: ProjectUseCases = Depends(get_project_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Get all projects for the current tenant"""
    projects = await project_use_cases.get_projects_by_tenant(tenant_id)
    
    return [
        ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            tenant_id=project.tenant_id,
            created_by=project.created_by,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
        for project in projects
    ]

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    project_use_cases: ProjectUseCases = Depends(get_project_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Get a specific project"""
    try:
        project = await project_use_cases.get_project(project_id, tenant_id)
        
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            tenant_id=project.tenant_id,
            created_by=project.created_by,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    request: UpdateProjectRequest,
    project_use_cases: ProjectUseCases = Depends(get_project_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Update a project"""
    try:
        project = await project_use_cases.update_project(
            project_id=project_id,
            tenant_id=tenant_id,
            name=request.name,
            description=request.description,
            status=request.status
        )
        
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            tenant_id=project.tenant_id,
            created_by=project.created_by,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    project_use_cases: ProjectUseCases = Depends(get_project_use_cases),
    tenant_id: uuid.UUID = Depends(get_current_tenant)
):
    """Delete a project"""
    try:
        success = await project_use_cases.delete_project(project_id, tenant_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))