# backend/domain/entities/user.py
from datetime import datetime
from typing import Optional
import uuid

class User:
    def __init__(
        self,
        email: str,
        tenant_id: uuid.UUID,
        hashed_password: str,
        first_name: str,
        last_name: str,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        is_active: bool = True
    ):
        self.id = id or uuid.uuid4()
        self.email = email
        self.tenant_id = tenant_id
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = created_at or datetime.utcnow()
        self.is_active = is_active
        
        # Business rules
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        if not first_name or len(first_name.strip()) == 0:
            raise ValueError("First name cannot be empty")