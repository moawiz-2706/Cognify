"""Simple models for the Cognify application without database."""

from datetime import datetime
from typing import List, Optional
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


class FlashcardBase(BaseModel):
    """Base flashcard model."""
    front: str = Field(..., min_length=1, max_length=1000)
    back: str = Field(..., min_length=1, max_length=1000)
    tags: Optional[List[str]] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    subject: Optional[str] = None
    topic: Optional[str] = None


class FlashcardCreate(FlashcardBase):
    """Flashcard creation model."""
    pass


class FlashcardUpdate(BaseModel):
    """Flashcard update model."""
    front: Optional[str] = None
    back: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty: Optional[DifficultyLevel] = None
    subject: Optional[str] = None
    topic: Optional[str] = None


class Flashcard(FlashcardBase):
    """Flashcard model."""
    id: int
    created_at: datetime
    updated_at: datetime
    status: CardStatus = CardStatus.NEW
    difficulty_score: float = 0.5
    next_review_time: Optional[datetime] = None
    review_count: int = 0
    correct_count: int = 0


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
    created_at: datetime


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
    total_cards: int
    mastered_cards: int
    learning_cards: int
    review_cards: int
    average_accuracy: float
    study_streak: int
    last_study_date: Optional[datetime]
    performance_trend: List[float]


class Course(BaseModel):
    """Course model."""
    code: str
    name: str
    credit_hours: str
    semester: int


class Semester(BaseModel):
    """Semester model."""
    number: int
    courses: List[Course]


class DegreeProgram(str, Enum):
    """Degree program options."""
    CS = "CS"  # Computer Science
    SE = "SE"  # Software Engineering
    AI = "AI"  # Artificial Intelligence
    DS = "DS"  # Data Science
    CYS = "CYS"  # Cybersecurity


class UserPreferences(BaseModel):
    """User preferences model."""
    degree_program: Optional[DegreeProgram] = None
    current_semester: Optional[int] = Field(None, ge=1, le=8)
    selected_courses: List[str] = []  # List of course codes


class UserPreferencesUpdate(BaseModel):
    """User preferences update model."""
    degree_program: Optional[DegreeProgram] = None
    current_semester: Optional[int] = Field(None, ge=1, le=8)
    selected_courses: Optional[List[str]] = None
