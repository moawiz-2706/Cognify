"""Tests for authentication functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.services.auth import get_password_hash

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user(setup_database):
    """Test user registration."""
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_user(setup_database):
    """Test registration with duplicate username."""
    # First registration
    client.post("/auth/register", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpassword"
    })
    
    # Second registration with same username
    response = client.post("/auth/register", json={
        "username": "testuser2",
        "email": "test3@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 400

def test_login_success(setup_database):
    """Test successful login."""
    # Register user first
    client.post("/auth/register", json={
        "username": "testuser3",
        "email": "test3@example.com",
        "password": "testpassword"
    })
    
    # Login
    response = client.post("/auth/token", data={
        "username": "testuser3",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(setup_database):
    """Test login with invalid credentials."""
    response = client.post("/auth/token", data={
        "username": "nonexistent",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_current_user(setup_database):
    """Test getting current user information."""
    # Register and login
    client.post("/auth/register", json={
        "username": "testuser4",
        "email": "test4@example.com",
        "password": "testpassword"
    })
    
    login_response = client.post("/auth/token", data={
        "username": "testuser4",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser4"
