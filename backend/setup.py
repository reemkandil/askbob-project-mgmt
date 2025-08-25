# setup.py - Run this to set up the database with sample data
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.connection import AsyncSessionLocal, engine
from infrastructure.database.models import Base
from infrastructure.database.repositories.tenant_repository_impl import TenantRepositoryImpl
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.database.repositories.project_repository_impl import ProjectRepositoryImpl
from infrastructure.auth.jwt_handler import JWTHandler
from domain.entities.tenant import Tenant
from domain.entities.user import User
from domain.entities.project import Project

async def create_sample_data():
    """Create sample data for testing"""
    async with AsyncSessionLocal() as session:
        try:
            # Create repositories
            tenant_repo = TenantRepositoryImpl(session)
            user_repo = UserRepositoryImpl(session)
            project_repo = ProjectRepositoryImpl(session)
            jwt_handler = JWTHandler()

            # Create a sample tenant
            sample_tenant = Tenant(
                name="AskBob Demo Company",
                domain="askbob-demo"
            )
            created_tenant = await tenant_repo.create(sample_tenant)
            print(f"Created tenant: {created_tenant.name}")

            # Create a sample user
            hashed_password = jwt_handler.get_password_hash("password123")
            sample_user = User(
                email="demo@askbob.com",
                tenant_id=created_tenant.id,
                hashed_password=hashed_password,
                first_name="Demo",
                last_name="User"
            )
            created_user = await user_repo.create(sample_user)
            print(f"Created user: {created_user.email}")

            # Create a sample project
            sample_project = Project(
                name="Sample Project",
                description="This is a sample project to get you started",
                tenant_id=created_tenant.id,
                created_by=created_user.id
            )
            created_project = await project_repo.create(sample_project)
            print(f"Created project: {created_project.name}")

            print("\n" + "="*50)
            print("Sample data created successfully!")
            print("You can now login with:")
            print("Email: demo@askbob.com")
            print("Password: password123")
            print("="*50)

        except Exception as e:
            print(f"Error creating sample data: {e}")
            await session.rollback()

async def main():
    """Main setup function"""
    print("Setting up AskBob Project Management System...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")
    
    # Create sample data
    await create_sample_data()

if __name__ == "__main__":
    asyncio.run(main())