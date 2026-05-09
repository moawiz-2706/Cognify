"""Tests for flashcard functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base, User, Flashcard
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

@pytest.fixture
def test_user(setup_database):
    """Create a test user."""
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()

@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user."""
    login_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_flashcard(auth_headers):
    """Test creating a flashcard."""
    response = client.post("/flashcards/", 
        json={
            "front": "What is Python?",
            "back": "A programming language",
            "tags": ["programming", "python"],
            "difficulty": "medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["front"] == "What is Python?"
    assert data["back"] == "A programming language"
    assert data["difficulty"] == "medium"

def test_get_flashcards(auth_headers):
    """Test getting flashcards."""
    # Create a flashcard first
    client.post("/flashcards/", 
        json={
            "front": "Test question",
            "back": "Test answer",
            "difficulty": "easy"
        },
        headers=auth_headers
    )
    
    response = client.get("/flashcards/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["front"] == "Test question"

def test_update_flashcard(auth_headers):
    """Test updating a flashcard."""
    # Create a flashcard
    create_response = client.post("/flashcards/", 
        json={
            "front": "Original question",
            "back": "Original answer",
            "difficulty": "easy"
        },
        headers=auth_headers
    )
    flashcard_id = create_response.json()["id"]
    
    # Update the flashcard
    response = client.put(f"/flashcards/{flashcard_id}", 
        json={
            "front": "Updated question",
            "back": "Updated answer",
            "difficulty": "hard"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["front"] == "Updated question"
    assert data["difficulty"] == "hard"

def test_delete_flashcard(auth_headers):
    """Test deleting a flashcard."""
    # Create a flashcard
    create_response = client.post("/flashcards/", 
        json={
            "front": "To be deleted",
            "back": "This will be deleted",
            "difficulty": "easy"
        },
        headers=auth_headers
    )
    flashcard_id = create_response.json()["id"]
    
    # Delete the flashcard
    response = client.delete(f"/flashcards/{flashcard_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = client.get(f"/flashcards/{flashcard_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_submit_review(auth_headers):
    """Test submitting a review session."""
    # Create a flashcard
    create_response = client.post("/flashcards/", 
        json={
            "front": "Review test",
            "back": "Review answer",
            "difficulty": "medium"
        },
        headers=auth_headers
    )
    flashcard_id = create_response.json()["id"]
    
    # Submit a review
    response = client.post(f"/flashcards/{flashcard_id}/review", 
        json={
            "flashcard_id": flashcard_id,
            "response_accuracy": 0.8,
            "response_time": 5.5
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "agent_output" in data
    assert "updated_flashcard" in data

def test_get_analytics(auth_headers):
    """Test getting learning analytics."""
    response = client.get("/flashcards/analytics/learning", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_cards" in data
    assert "mastered_cards" in data
    assert "average_accuracy" in data
