# backend/domain/entities/auth.py
from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel

class TokenData(BaseModel):
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    exp: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    tenant_name: str  # For creating new tenant during registration
    tenant_domain: str