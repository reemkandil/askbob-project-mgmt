# backend/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app
from infrastructure.database.connection import get_db_session
from infrastructure.database.models import Base

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_db():
    """Create test database"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    yield async_session
    
    await engine.dispose()

@pytest.fixture
def client(test_db):
    """Create test client with test database"""
    async def override_get_db():
        async with test_db() as session:
            yield session
    
    app.dependency_overrides[get_db_session] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_register_user(client):
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "tenant_name": "Test Company",
        "tenant_domain": "test-company"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user(client):
    """Test user login"""
    # First register a user
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "tenant_name": "Test Company",
        "tenant_domain": "test-company"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Now try to login
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 401

def test_register_duplicate_email(client):
    """Test registration with duplicate email"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "tenant_name": "Test Company",
        "tenant_domain": "test-company"
    }
    
    # Register first user
    response1 = client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Try to register with same email
    user_data["tenant_domain"] = "different-domain"
    response2 = client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400

def test_protected_route_without_token(client):
    """Test accessing protected route without token"""
    response = client.get("/api/v1/projects")
    assert response.status_code == 401

def test_protected_route_with_token(client):
    """Test accessing protected route with valid token"""
    # Register and login to get token
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "tenant_name": "Test Company",
        "tenant_domain": "test-company"
    }
    register_response = client.post("/api/v1/auth/register", json=user_data)
    token = register_response.json()["access_token"]
    
    # Access protected route with token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/projects", headers=headers)
    
    assert response.status_code == 200