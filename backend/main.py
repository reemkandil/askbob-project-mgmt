# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import projects, tasks, auth
from infrastructure.database.connection import engine

app = FastAPI(
    title="AskBob Project Management API",
    description="Multi-tenant project management system with Clean Architecture",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])

@app.get("/")
async def root():
    return {"message": "AskBob Project Management API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}