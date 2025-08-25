# AskBob Project Management System

A multi-tenant project management system built with Clean Architecture principles using FastAPI, React, and PostgreSQL.

## 🏗️ Architecture Overview

This project implements **Clean Architecture** with clear separation of concerns:

```
backend/
├── domain/           # Business Logic & Entities (Core)
│   ├── entities/     # Business objects (Project, Task, User, Tenant)
│   └── repositories/ # Repository interfaces (contracts)
├── application/      # Application Business Rules
│   ├── use_cases/    # Business operations orchestration
│   └── dto/          # Data Transfer Objects
├── infrastructure/   # Frameworks & External Tools
│   ├── database/     # SQLAlchemy implementations
│   └── auth/         # JWT authentication
└── api/             # Interface Adapters
    └── routes/      # FastAPI endpoints
```

### Key Architectural Decisions

1. **Clean Architecture Layers**:
   - **Domain Layer**: Pure Python classes with business logic, no framework dependencies
   - **Application Layer**: Use cases that orchestrate business operations
   - **Infrastructure Layer**: Concrete implementations (database, auth)
   - **API Layer**: HTTP interface using FastAPI

2. **Dependency Flow**: Following dependency inversion principle - high-level modules don't depend on low-level modules

3. **Multi-Tenancy Strategy**: 
   - Shared database with tenant_id column approach
   - Complete data isolation through JWT tokens containing tenant information
   - All queries automatically filtered by tenant_id

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git

### Database Setup

1. Install PostgreSQL and ensure it's running:
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

2. Create database and user:
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE askbob_db;
CREATE USER askbob_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE askbob_db TO askbob_user;
\q
```

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` file:
```env
DATABASE_URL=postgresql+asyncpg://askbob_user:your_password@localhost:5432/askbob_db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. (Optional) Create sample data:
```bash
python setup.py
```

7. Start the backend server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000
API documentation at: http://localhost:8000/docs

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at: http://localhost:5173

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user & tenant | No |
| POST | `/api/v1/auth/login` | Login user | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |

### Project Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/projects` | List all projects for tenant | Yes |
| POST | `/api/v1/projects` | Create new project | Yes |
| GET | `/api/v1/projects/{id}` | Get specific project | Yes |
| PUT | `/api/v1/projects/{id}` | Update project | Yes |
| DELETE | `/api/v1/projects/{id}` | Delete project | Yes |

### Task Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/projects/{project_id}/tasks` | List tasks for project | Yes |
| POST | `/api/v1/projects/{project_id}/tasks` | Create task in project | Yes |
| PUT | `/api/v1/tasks/{id}` | Update task | Yes |
| DELETE | `/api/v1/tasks/{id}` | Delete task | Yes |

## 🔐 Authentication & Multi-Tenancy

- **JWT Authentication**: Secure token-based authentication
- **Password Security**: Bcrypt hashing for password storage
- **Tenant Isolation**: Every user belongs to a tenant (organization)
- **Automatic Filtering**: All data queries automatically filtered by tenant_id from JWT token

## 🧪 Testing

Run backend tests:
```bash
cd backend
pytest tests/ -v
```

## 📝 Default Credentials

If you ran `python setup.py`, you can login with:
- **Email**: demo@askbob.com
- **Password**: password123

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern async Python web framework
- **SQLAlchemy 2.0**: ORM with async support
- **PostgreSQL**: Relational database
- **Alembic**: Database migration tool
- **JWT**: Token-based authentication
- **Bcrypt**: Password hashing

### Frontend
- **React 18**: UI library
- **React Router v6**: Client-side routing
- **React Query**: Server state management
- **React Hook Form**: Form handling
- **Axios**: HTTP client

## 📦 Project Structure

```
askbob-project-mgmt/
├── backend/
│   ├── domain/              # Core business logic
│   ├── application/         # Use cases
│   ├── infrastructure/      # External implementations
│   ├── api/                 # HTTP endpoints
│   ├── alembic/            # Database migrations
│   ├── tests/              # Unit tests
│   └── main.py             # Application entry point
├── frontend/
│   ├── src/
│   │   ├── features/       # Feature modules
│   │   ├── context/        # React contexts
│   │   ├── lib/           # Utilities
│   │   └── App.jsx        # Main component
│   └── package.json
└── README.md
```

## 🎯 Design Decisions

### Why Clean Architecture?

1. **Testability**: Business logic can be tested without frameworks
2. **Flexibility**: Easy to swap frameworks or databases
3. **Maintainability**: Clear separation of concerns
4. **Independence**: Business rules don't depend on external libraries

### Multi-Tenancy Approach

We chose the **shared database with tenant_id** approach because:
- Simpler to implement and maintain
- Cost-effective for small to medium scale
- Easy to backup and manage
- Good performance with proper indexing

### Technology Choices

- **FastAPI**: Chosen for its modern async support, automatic API documentation, and excellent performance
- **SQLAlchemy 2.0**: Industry standard ORM with new async capabilities
- **PostgreSQL**: Robust, scalable, and supports advanced features
- **React**: Popular, well-supported, and excellent ecosystem
- **JWT**: Stateless authentication suitable for distributed systems

## 📌 Assumptions Made

1. Each user belongs to exactly one tenant (organization)
2. The first user registering creates the tenant and becomes the admin
3. Tenant domains must be unique across the system
4. Tasks must belong to a project
5. All timestamps are stored in UTC
6. Email addresses are unique across the entire system

## 🚧 Future Enhancements

- [ ] User roles and permissions (Admin, Manager, Member)
- [ ] Task assignments to specific users
- [ ] File attachments for tasks
- [ ] Email notifications
- [ ] Activity logs
- [ ] Advanced search and filtering
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Real-time updates using WebSockets

## 📄 License

This project was created as an assessment for Hook EG.

## 👤 Author

Reem Kandil

## 📞 Support

For any questions or issues, please create an issue in the GitHub repository.