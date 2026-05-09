"""Pydantic models for the Cognify application."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class DifficultyLevel(str, Enum):
    """Difficulty levels for flashcards."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CardStatus(str, Enum):
    """Status of flashcard review."""
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    MASTERED = "mastered"


class UserBase(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=6)


class User(UserBase):
    """User model."""
    id: int
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True


class FlashcardBase(BaseModel):
    """Base flashcard model."""
    front: str = Field(..., min_length=1, max_length=1000)
    back: str = Field(..., min_length=1, max_length=1000)
    tags: Optional[List[str]] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class FlashcardCreate(FlashcardBase):
    """Flashcard creation model."""
    pass


class FlashcardUpdate(BaseModel):
    """Flashcard update model."""
    front: Optional[str] = None
    back: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty: Optional[DifficultyLevel] = None


class Flashcard(FlashcardBase):
    """Flashcard model."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    status: CardStatus = CardStatus.NEW
    difficulty_score: float = 0.5
    next_review_time: Optional[datetime] = None
    review_count: int = 0
    correct_count: int = 0
    
    class Config:
        from_attributes = True


class ReviewSessionBase(BaseModel):
    """Base review session model."""
    flashcard_id: int
    response_accuracy: float = Field(..., ge=0.0, le=1.0)
    response_time: float = Field(..., gt=0.0)
    user_answer: Optional[str] = None  # User's answer for detailed explanation


class ReviewSessionCreate(ReviewSessionBase):
    """Review session creation model."""
    pass


class ReviewSession(ReviewSessionBase):
    """Review session model."""
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentInput(BaseModel):
    """Input for the Cognify Agent."""
    user_id: str
    flashcard_id: str
    response_accuracy: float = Field(..., ge=0.0, le=1.0)
    response_time: float = Field(..., gt=0.0)


class AgentOutput(BaseModel):
    """Output from the Cognify Agent."""
    next_review_time: datetime
    difficulty_score: float = Field(..., ge=0.0, le=1.0)
    recommendation: str


class LearningAnalytics(BaseModel):
    """Learning analytics model."""
    user_id: int
    total_cards: int
    mastered_cards: int
    learning_cards: int
    review_cards: int
    average_accuracy: float
    study_streak: int
    last_study_date: Optional[datetime]
    performance_trend: List[float]


class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
