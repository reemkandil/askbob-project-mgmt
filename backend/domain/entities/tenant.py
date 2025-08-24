# backend/domain/entities/tenant.py
from datetime import datetime
from typing import Optional
import uuid

class Tenant:
    def __init__(
        self,
        name: str,
        domain: str,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id or uuid.uuid4()
        self.name = name
        self.domain = domain
        self.created_at = created_at or datetime.utcnow()
        
        # Business rules
        if not name or len(name.strip()) == 0:
            raise ValueError("Tenant name cannot be empty")
        if not domain or len(domain.strip()) == 0:
            raise ValueError("Tenant domain cannot be empty")