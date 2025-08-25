# backend/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.auth_use_cases import AuthUseCases
from application.dto.auth_dto import LoginRequest, RegisterRequest, TokenResponse
from infrastructure.database.connection import get_db_session
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.database.repositories.tenant_repository_impl import TenantRepositoryImpl
from infrastructure.auth.jwt_handler import JWTHandler

router = APIRouter()
security = HTTPBearer()

async def get_auth_dependencies(session: AsyncSession = Depends(get_db_session)):
    user_repo = UserRepositoryImpl(session)
    tenant_repo = TenantRepositoryImpl(session)
    jwt_handler = JWTHandler()
    return AuthUseCases(user_repo, tenant_repo, jwt_handler)

@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: RegisterRequest,
    auth_use_cases: AuthUseCases = Depends(get_auth_dependencies)
):
    """Register a new user and create their tenant"""
    try:
        token = await auth_use_cases.register_user(request)
        return token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@router.post("/auth/login", response_model=TokenResponse)
async def login_user(
    request: LoginRequest,
    auth_use_cases: AuthUseCases = Depends(get_auth_dependencies)
):
    """Authenticate user and return JWT token"""
    try:
        token = await auth_use_cases.login_user(request)
        return token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@router.get("/auth/me")
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_use_cases: AuthUseCases = Depends(get_auth_dependencies)
):
    """Get current user information from JWT token"""
    try:
        user = await auth_use_cases.get_current_user(credentials.credentials)
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "tenant_id": user.tenant_id,
            "is_active": user.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")