# backend/api/auth_middleware.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from infrastructure.database.connection import get_db_session
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.auth.jwt_handler import JWTHandler
from domain.entities.auth import TokenData

security = HTTPBearer()

async def get_current_user_data(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session)
) -> TokenData:
    """
    Dependency to get current user data from JWT token
    """
    try:
        jwt_handler = JWTHandler()
        token_data = jwt_handler.get_current_user_from_token(credentials.credentials)
        
        # Verify user exists in database
        user_repo = UserRepositoryImpl(session)
        user = await user_repo.get_by_id(token_data.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return token_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_tenant_id(
    token_data: TokenData = Depends(get_current_user_data)
) -> uuid.UUID:
    """Get current tenant ID from authenticated user"""
    return token_data.tenant_id

async def get_current_user_id(
    token_data: TokenData = Depends(get_current_user_data)
) -> uuid.UUID:
    """Get current user ID from authenticated user"""
    return token_data.user_id