"""Flashcard routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.models import (
    Flashcard, FlashcardCreate, FlashcardUpdate, 
    ReviewSessionCreate, LearningAnalytics
)
from app.services.flashcard_service import FlashcardService
from app.routers.auth import get_current_user

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.post("/", response_model=Flashcard)
async def create_flashcard(
    flashcard: FlashcardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new flashcard."""
    service = FlashcardService(db)
    return service.create_flashcard(flashcard, current_user.id)


@router.get("/", response_model=List[Flashcard])
async def get_flashcards(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all flashcards for the current user."""
    service = FlashcardService(db)
    return service.get_flashcards(current_user.id, skip, limit)


@router.get("/due", response_model=List[Flashcard])
async def get_due_flashcards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get flashcards that are due for review."""
    service = FlashcardService(db)
    return service.get_due_flashcards(current_user.id)


@router.get("/{flashcard_id}", response_model=Flashcard)
async def get_flashcard(
    flashcard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific flashcard."""
    service = FlashcardService(db)
    flashcard = service.get_flashcard(flashcard_id, current_user.id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    return flashcard


@router.put("/{flashcard_id}", response_model=Flashcard)
async def update_flashcard(
    flashcard_id: int,
    flashcard_update: FlashcardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a flashcard."""
    service = FlashcardService(db)
    flashcard = service.update_flashcard(flashcard_id, flashcard_update, current_user.id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    return flashcard


@router.delete("/{flashcard_id}")
async def delete_flashcard(
    flashcard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a flashcard."""
    service = FlashcardService(db)
    success = service.delete_flashcard(flashcard_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    return {"message": "Flashcard deleted successfully"}


@router.post("/{flashcard_id}/review")
async def submit_review(
    flashcard_id: int,
    review_data: ReviewSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a review session for a flashcard."""
    service = FlashcardService(db)
    
    # Ensure the flashcard belongs to the user
    flashcard = service.get_flashcard(flashcard_id, current_user.id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    # Update review data with flashcard_id
    review_data.flashcard_id = flashcard_id
    
    try:
        result = service.process_review(
            review_data, 
            current_user.id, 
            user_answer=review_data.user_answer
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
