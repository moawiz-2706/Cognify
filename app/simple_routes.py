"""Simple routes with session-based authentication."""

from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, status, Cookie
from app.simple_models import (
    Flashcard, FlashcardCreate, FlashcardUpdate, 
    ReviewSessionCreate, LearningAnalytics,
    UserPreferences, UserPreferencesUpdate, Semester, Course
)
from app.simple_service import flashcard_service
from app.curriculum import get_curriculum, get_semester_courses

# Try to use MongoDB auth, fallback to simple auth
try:
    from app.mongodb_auth import mongodb_auth
    auth = mongodb_auth
except Exception:
    from app.simple_auth import simple_auth
    auth = simple_auth


def get_username_from_session(session_id: Optional[str] = Cookie(None)) -> str:
    """Get username from session, default to 'default' if no session."""
    if not session_id:
        return "default"
    
    user = auth.get_user_from_session(session_id)
    if user:
        return user["username"]
    return "default"

router = APIRouter(prefix="/api", tags=["flashcards"])
preferences_router = APIRouter(prefix="/api", tags=["preferences"])
curriculum_router = APIRouter(prefix="/api", tags=["curriculum"])


@router.post("/flashcards/", response_model=Flashcard)
async def create_flashcard(flashcard: FlashcardCreate, session_id: Optional[str] = Cookie(None)):
    """Create a new flashcard."""
    username = get_username_from_session(session_id)
    return flashcard_service.create_flashcard(flashcard, username)


@router.get("/flashcards/", response_model=List[Flashcard])
async def get_flashcards(skip: int = 0, limit: int = 100, session_id: Optional[str] = Cookie(None)):
    """Get all flashcards."""
    username = get_username_from_session(session_id)
    flashcards = flashcard_service.get_flashcards(skip, limit, username)
    print(f"API: Returning {len(flashcards)} flashcards for user {username}")
    return flashcards


@router.get("/flashcards/due", response_model=List[Flashcard])
async def get_due_flashcards(session_id: Optional[str] = Cookie(None)):
    """Get flashcards that are due for review."""
    username = get_username_from_session(session_id)
    return flashcard_service.get_due_flashcards(username)


@router.get("/flashcards/{flashcard_id}", response_model=Flashcard)
async def get_flashcard(flashcard_id: int, session_id: Optional[str] = Cookie(None)):
    """Get a specific flashcard."""
    username = get_username_from_session(session_id)
    flashcard = flashcard_service.get_flashcard(flashcard_id, username)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    return flashcard


@router.put("/flashcards/{flashcard_id}", response_model=Flashcard)
async def update_flashcard(flashcard_id: int, flashcard_update: FlashcardUpdate, session_id: Optional[str] = Cookie(None)):
    """Update a flashcard."""
    username = get_username_from_session(session_id)
    flashcard = flashcard_service.update_flashcard(flashcard_id, flashcard_update, username)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    return flashcard


@router.delete("/flashcards/{flashcard_id}")
async def delete_flashcard(flashcard_id: int, session_id: Optional[str] = Cookie(None)):
    """Delete a flashcard."""
    username = get_username_from_session(session_id)
    success = flashcard_service.delete_flashcard(flashcard_id, username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    return {"message": "Flashcard deleted successfully"}


@router.post("/flashcards/{flashcard_id}/review")
async def submit_review(flashcard_id: int, review_data: ReviewSessionCreate, session_id: Optional[str] = Cookie(None)):
    """Submit a review session for a flashcard with detailed explanations."""
    username = get_username_from_session(session_id)
    # Update review data with flashcard_id
    review_data.flashcard_id = flashcard_id
    
    try:
        result = flashcard_service.process_review(
            review_data, 
            user_answer=review_data.user_answer,
            username=username
        )
        return {
            "message": "Review submitted successfully",
            "agent_output": result["agent_output"],
            "updated_flashcard": result["updated_flashcard"],
            "detailed_explanation": result["agent_output"].get("detailed_explanation")
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/analytics/learning", response_model=LearningAnalytics)
async def get_learning_analytics(session_id: Optional[str] = Cookie(None)):
    """Get learning analytics."""
    username = get_username_from_session(session_id)
    return flashcard_service.get_learning_analytics(username)


# User Preferences Routes
@preferences_router.get("/preferences", response_model=UserPreferences)
async def get_preferences(session_id: Optional[str] = Cookie(None)):
    """Get user preferences."""
    username = get_username_from_session(session_id)
    return flashcard_service.get_user_preferences(username)


@preferences_router.put("/preferences", response_model=UserPreferences)
async def update_preferences(preferences: UserPreferencesUpdate, session_id: Optional[str] = Cookie(None)):
    """Update user preferences."""
    username = get_username_from_session(session_id)
    return flashcard_service.update_user_preferences(preferences, username)


@preferences_router.post("/preferences/courses/{course_code}")
async def add_course(course_code: str, session_id: Optional[str] = Cookie(None)):
    """Add a course to the current semester."""
    username = get_username_from_session(session_id)
    print(f"Adding course {course_code} for user {username}")
    success = flashcard_service.add_course_to_semester(course_code, username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course already added or invalid course code"
        )
    
    # Verify flashcards were created
    flashcards = flashcard_service.get_flashcards(0, 100, username)
    print(f"Total flashcards for {username} after adding {course_code}: {len(flashcards)}")
    
    return {
        "message": f"Course {course_code} added successfully", 
        "course_code": course_code,
        "flashcards_generated": len([f for f in flashcards if f.subject == course_code])
    }


@preferences_router.delete("/preferences/courses/{course_code}")
async def remove_course(course_code: str, session_id: Optional[str] = Cookie(None)):
    """Remove a course from the current semester."""
    username = get_username_from_session(session_id)
    success = flashcard_service.remove_course_from_semester(course_code, username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found in selected courses"
        )
    return {"message": f"Course {course_code} removed successfully"}


# Curriculum Routes
@curriculum_router.get("/curriculum")
async def get_full_curriculum():
    """Get the complete curriculum for all semesters."""
    curriculum = get_curriculum()
    # Convert to dict with string keys for JSON serialization
    result = {}
    for semester_num, semester in curriculum.items():
        result[str(semester_num)] = {
            "number": semester.number,
            "courses": [course.dict() for course in semester.courses]
        }
    return result


@curriculum_router.get("/curriculum/semester/{semester_number}", response_model=List[Course])
async def get_semester_courses_endpoint(semester_number: int):
    """Get courses for a specific semester."""
    if semester_number < 1 or semester_number > 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Semester number must be between 1 and 8"
        )
    courses = get_semester_courses(semester_number)
    return courses
