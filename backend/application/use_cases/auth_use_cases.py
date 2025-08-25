# backend/application/use_cases/auth_use_cases.py
from typing import Optional
from fastapi import HTTPException, status
from domain.entities.user import User
from domain.entities.tenant import Tenant
from domain.repositories.user_repository import UserRepository
from domain.repositories.tenant_repository import TenantRepository
from infrastructure.auth.jwt_handler import JWTHandler
from application.dto.auth_dto import LoginRequest, RegisterRequest, TokenResponse

class AuthUseCases:
    def __init__(
        self, 
        user_repository: UserRepository,
        tenant_repository: TenantRepository,
        jwt_handler: JWTHandler
    ):
        self.user_repository = user_repository
        self.tenant_repository = tenant_repository
        self.jwt_handler = jwt_handler
    
    async def register_user(self, user_data: RegisterRequest) -> TokenResponse:
        """Register a new user and create their tenant"""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if tenant domain already exists
        existing_tenant = await self.tenant_repository.get_by_domain(user_data.tenant_domain)
        if existing_tenant:
            raise ValueError("Tenant domain already exists")
        
        # Create tenant first
        tenant = Tenant(
            name=user_data.tenant_name,
            domain=user_data.tenant_domain
        )
        created_tenant = await self.tenant_repository.create(tenant)
        
        # Hash password and create user
        hashed_password = self.jwt_handler.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            tenant_id=created_tenant.id,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        created_user = await self.user_repository.create(user)
        
        # Generate JWT token
        access_token = self.jwt_handler.create_access_token(
            user_id=created_user.id,
            tenant_id=created_user.tenant_id,
            email=created_user.email
        )
        
        return TokenResponse(access_token=access_token, token_type="bearer")
    
    async def login_user(self, login_data: LoginRequest) -> TokenResponse:
        """Authenticate user and return JWT token"""
        # Get user by email
        user = await self.user_repository.get_by_email(login_data.email)
        if not user:
            raise ValueError("Incorrect email or password")
        
        # Verify password
        if not self.jwt_handler.verify_password(login_data.password, user.hashed_password):
            raise ValueError("Incorrect email or password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("Inactive user")
        
        # Generate JWT token
        access_token = self.jwt_handler.create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            email=user.email
        )
        
        return TokenResponse(access_token=access_token, token_type="bearer")
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        token_data = self.jwt_handler.get_current_user_from_token(token)
        
        user = await self.user_repository.get_by_id(token_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user