# backend/domain/repositories/tenant_repository.py
from abc import abstractmethod
from typing import Optional
from .base import BaseRepository
from ..entities.tenant import Tenant

class TenantRepository(BaseRepository[Tenant]):
    @abstractmethod
    async def get_by_domain(self, domain: str) -> Optional[Tenant]:
        pass