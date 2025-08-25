# backend/application/dto/auth_dto.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    tenant_name: str = Field(..., min_length=1, max_length=200)
    tenant_domain: str = Field(..., min_length=1, max_length=100)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    tenant_id: str
    is_active: bool