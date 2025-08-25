# backend/infrastructure/auth/jwt_handler.py
import os
from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from domain.entities.auth import TokenData
from fastapi import HTTPException, status

class JWTHandler:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, user_id: uuid.UUID, tenant_id: uuid.UUID, email: str) -> str:
        """Create a JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "email": email,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            tenant_id: str = payload.get("tenant_id")
            email: str = payload.get("email")
            exp: datetime = datetime.fromtimestamp(payload.get("exp"))
            
            if user_id is None or tenant_id is None or email is None:
                return None
                
            return TokenData(
                user_id=uuid.UUID(user_id),
                tenant_id=uuid.UUID(tenant_id),
                email=email,
                exp=exp
            )
        except JWTError:
            return None
    
    def get_current_user_from_token(self, token: str) -> TokenData:
        """Get current user from token, raise exception if invalid"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        token_data = self.verify_token(token)
        if token_data is None:
            raise credentials_exception
            
        # Check if token is expired
        if datetime.utcnow() > token_data.exp:
            raise credentials_exception
            
        return token_data