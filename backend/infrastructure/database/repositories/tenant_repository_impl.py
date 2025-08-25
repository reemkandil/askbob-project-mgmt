# backend/infrastructure/database/repositories/tenant_repository_impl.py
from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.tenant import Tenant
from domain.repositories.tenant_repository import TenantRepository
from ..models import TenantModel
from ..mappers import TenantMapper

class TenantRepositoryImpl(TenantRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: Tenant) -> Tenant:
        model = TenantMapper.to_model(entity)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return TenantMapper.to_domain(model)

    async def get_by_id(self, id: uuid.UUID) -> Optional[Tenant]:
        result = await self.session.execute(
            select(TenantModel).where(TenantModel.id == id)
        )
        model = result.scalar_one_or_none()
        return TenantMapper.to_domain(model) if model else None

    async def get_by_domain(self, domain: str) -> Optional[Tenant]:
        result = await self.session.execute(
            select(TenantModel).where(TenantModel.domain == domain)
        )
        model = result.scalar_one_or_none()
        return TenantMapper.to_domain(model) if model else None

    async def update(self, entity: Tenant) -> Tenant:
        result = await self.session.execute(
            select(TenantModel).where(TenantModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError("Tenant not found")
        
        model.name = entity.name
        model.domain = entity.domain
        
        await self.session.commit()
        await self.session.refresh(model)
        return TenantMapper.to_domain(model)

    async def delete(self, id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(TenantModel).where(TenantModel.id == id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True