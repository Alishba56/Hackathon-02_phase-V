from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from db import create_db_and_tables

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: cleanup if needed


# Initialize FastAPI app
app = FastAPI(
    title="Todo Application Backend API",
    description="Secure RESTful API for task management with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("BETTER_AUTH_URL", "http://localhost:3001"),
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import and register routers
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router
from routes.chat import router as chat_router

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(chat_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Todo Application Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
