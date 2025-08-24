# backend/tests/test_domain_entities.py
import pytest
from datetime import datetime
import uuid
from domain.entities.project import Project, ProjectStatus
from domain.entities.task import Task, TaskStatus, TaskPriority

class TestProject:
    def test_create_project_success(self):
        """Test successful project creation"""
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        project = Project(
            name="Test Project",
            tenant_id=tenant_id,
            created_by=user_id,
            description="A test project"
        )
        
        assert project.name == "Test Project"
        assert project.tenant_id == tenant_id
        assert project.created_by == user_id
        assert project.description == "A test project"
        assert project.status == ProjectStatus.PLANNING
        assert project.id is not None
        assert project.created_at is not None

    def test_create_project_empty_name_fails(self):
        """Test that empty project name raises ValueError"""
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            Project(
                name="",
                tenant_id=tenant_id,
                created_by=user_id
            )
        
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            Project(
                name="   ",  # Only whitespace
                tenant_id=tenant_id,
                created_by=user_id
            )

    def test_create_project_name_too_long_fails(self):
        """Test that project name over 200 characters raises ValueError"""
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        long_name = "x" * 201  # 201 characters
        
        with pytest.raises(ValueError, match="Project name cannot exceed 200 characters"):
            Project(
                name=long_name,
                tenant_id=tenant_id,
                created_by=user_id
            )

    def test_update_project_status_success(self):
        """Test successful status update"""
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        project = Project(
            name="Test Project",
            tenant_id=tenant_id,
            created_by=user_id
        )
        
        original_updated_at = project.updated_at
        
        # Wait a bit to ensure timestamp changes
        import time
        time.sleep(0.001)
        
        project.update_status(ProjectStatus.IN_PROGRESS)
        
        assert project.status == ProjectStatus.IN_PROGRESS
        assert project.updated_at > original_updated_at

    def test_cancelled_project_status_transition_rules(self):
        """Test business rule: cancelled projects can only go back to planning"""
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        project = Project(
            name="Test Project",
            tenant_id=tenant_id,
            created_by=user_id,
            status=ProjectStatus.CANCELLED
        )
        
        # Should allow transition to planning
        project.update_status(ProjectStatus.PLANNING)
        assert project.status == ProjectStatus.PLANNING
        
        # Set back to cancelled
        project.update_status(ProjectStatus.CANCELLED)
        
        # Should not allow direct transition to other statuses
        with pytest.raises(ValueError, match="Cannot change status of cancelled project"):
            project.update_status(ProjectStatus.IN_PROGRESS)

class TestTask:
    def test_create_task_success(self):
        """Test successful task creation"""
        project_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        task = Task(
            title="Test Task",
            project_id=project_id,
            tenant_id=tenant_id,
            created_by=user_id,
            description="A test task",
            priority=TaskPriority.HIGH
        )
        
        assert task.title == "Test Task"
        assert task.project_id == project_id
        assert task.tenant_id == tenant_id
        assert task.created_by == user_id
        assert task.description == "A test task"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.TODO
        assert task.assigned_to is None

    def test_create_task_empty_title_fails(self):
        """Test that empty task title raises ValueError"""
        project_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(
                title="",
                project_id=project_id,
                tenant_id=tenant_id,
                created_by=user_id
            )

    def test_assign_task_to_user(self):
        """Test assigning task to a user"""
        project_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        assignee_id = uuid.uuid4()
        
        task = Task(
            title="Test Task",
            project_id=project_id,
            tenant_id=tenant_id,
            created_by=user_id
        )
        
        original_updated_at = task.updated_at
        
        import time
        time.sleep(0.001)
        
        task.assign_to_user(assignee_id)
        
        assert task.assigned_to == assignee_id
        assert task.updated_at > original_updated_at

    def test_task_status_transition_rules(self):
        """Test business rule: cannot go from DONE directly to TODO"""
        project_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        task = Task(
            title="Test Task",
            project_id=project_id,
            tenant_id=tenant_id,
            created_by=user_id,
            status=TaskStatus.DONE
        )
        
        # Should not allow direct transition from DONE to TODO
        with pytest.raises(ValueError, match="Cannot move completed task back to TODO"):
            task.update_status(TaskStatus.TODO)
        
        # Should allow other transitions
        task.update_status(TaskStatus.IN_PROGRESS)
        assert task.status == TaskStatus.IN_PROGRESS

# backend/tests/test_use_cases.py
import pytest
from unittest.mock import AsyncMock, Mock
import uuid
from application.use_cases.project_use_cases import ProjectUseCases
from application.use_cases.task_use_cases import TaskUseCases
from domain.entities.project import Project, ProjectStatus
from domain.entities.task import Task, TaskStatus

class TestProjectUseCases:
    @pytest.fixture
    def mock_project_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def project_use_cases(self, mock_project_repository):
        return ProjectUseCases(mock_project_repository)

    @pytest.mark.asyncio
    async def test_create_project_success(self, project_use_cases, mock_project_repository):
        """Test successful project creation use case"""
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        # Setup mock to return the created project
        expected_project = Project(
            name="Test Project",
            tenant_id=tenant_id,
            created_by=user_id,
            description="Test description"
        )
        mock_project_repository.create.return_value = expected_project
        
        # Execute use case
        result = await project_use_cases.create_project(
            name="Test Project",
            tenant_id=tenant_id,
            created_by=user_id,
            description="Test description"
        )
        
        # Verify repository was called correctly
        mock_project_repository.create.assert_called_once()
        created_project = mock_project_repository.create.call_args[0][0]
        assert created_project.name == "Test Project"
        assert created_project.tenant_id == tenant_id
        assert created_project.created_by == user_id
        
        # Verify result
        assert result == expected_project

    @pytest.mark.asyncio
    async def test_get_projects_by_tenant(self, project_use_cases, mock_project_repository):
        """Test getting projects by tenant"""
        tenant_id = uuid.uuid4()
        expected_projects = [
            Project(name="Project 1", tenant_id=tenant_id, created_by=uuid.uuid4()),
            Project(name="Project 2", tenant_id=tenant_id, created_by=uuid.uuid4()),
        ]
        
        mock_project_repository.get_by_tenant.return_value = expected_projects
        
        result = await project_use_cases.get_projects_by_tenant(tenant_id)
        
        mock_project_repository.get_by_tenant.assert_called_once_with(tenant_id)
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, project_use_cases, mock_project_repository):
        """Test getting project that doesn't exist"""
        tenant_id = uuid.uuid4()
        project_id = uuid.uuid4()
        
        mock_project_repository.get_by_tenant_and_id.return_value = None
        
        with pytest.raises(ValueError, match="Project not found or access denied"):
            await project_use_cases.get_project(project_id, tenant_id)

class TestTaskUseCases:
    @pytest.fixture
    def mock_task_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_project_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def task_use_cases(self, mock_task_repository, mock_project_repository):
        return TaskUseCases(mock_task_repository, mock_project_repository)

    @pytest.mark.asyncio
    async def test_create_task_success(self, task_use_cases, mock_task_repository, mock_project_repository):
        """Test successful task creation"""
        project_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        # Setup: project exists
        existing_project = Project(
            name="Test Project",
            tenant_id=tenant_id,
            created_by=user_id
        )
        mock_project_repository.get_by_tenant_and_id.return_value = existing_project
        
        # Setup: task creation returns task
        expected_task = Task(
            title="Test Task",
            project_id=project_id,
            tenant_id=tenant_id,
            created_by=user_id
        )
        mock_task_repository.create.return_value = expected_task
        
        result = await task_use_cases.create_task(
            title="Test Task",
            project_id=project_id,
            tenant_id=tenant_id,
            created_by=user_id
        )
        
        # Verify project was checked
        mock_project_repository.get_by_tenant_and_id.assert_called_once_with(tenant_id, project_id)
        
        # Verify task was created
        mock_task_repository.create.assert_called_once()
        
        assert result == expected_task

    @pytest.mark.asyncio
    async def test_create_task_project_not_found(self, task_use_cases, mock_project_repository):
        """Test creating task when project doesn't exist"""
        project_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        mock_project_repository.get_by_tenant_and_id.return_value = None
        
        with pytest.raises(ValueError, match="Project not found or access denied"):
            await task_use_cases.create_task(
                title="Test Task",
                project_id=project_id,
                tenant_id=tenant_id,
                created_by=user_id
            )

# Run tests with: pytest -v tests/