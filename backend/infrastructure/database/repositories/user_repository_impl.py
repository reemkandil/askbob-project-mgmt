# backend/infrastructure/database/repositories/user_repository_impl.py
from typing import Optional, List
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from ..models import UserModel
from ..mappers import UserMapper

class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: User) -> User:
        model = UserMapper.to_model(entity)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return UserMapper.to_domain(model)

    async def get_by_id(self, id: uuid.UUID) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == id)
        )
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    async def get_by_tenant(self, tenant_id: uuid.UUID) -> List[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.tenant_id == tenant_id)
        )
        models = result.scalars().all()
        return [UserMapper.to_domain(model) for model in models]

    async def get_by_email_and_tenant(self, email: str, tenant_id: uuid.UUID) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(
                UserModel.email == email,
                UserModel.tenant_id == tenant_id
            )
        )
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    async def update(self, entity: User) -> User:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError("User not found")
        
        model.email = entity.email
        model.first_name = entity.first_name
        model.last_name = entity.last_name
        model.is_active = entity.is_active
        
        await self.session.commit()
        await self.session.refresh(model)
        return UserMapper.to_domain(model)

    async def delete(self, id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True