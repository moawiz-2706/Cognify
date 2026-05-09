"""Simple main FastAPI application without database or authentication."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Create FastAPI app
app = FastAPI(
    title="Cognify - Simple Adaptive Learning Assistant",
    description="A simple AI-powered flashcard system with adaptive learning capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3011,http://localhost:7000,http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include simple routes
from app.simple_routes import router, preferences_router, curriculum_router
from app.simple_auth_routes import router as auth_router
app.include_router(auth_router)
app.include_router(router)
app.include_router(preferences_router)
app.include_router(curriculum_router)

# Serve static files (React build)
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Cognify - Simple Adaptive Learning Assistant",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.simple_main:app",
        host="0.0.0.0",
        port=3001,
        reload=True
    )
