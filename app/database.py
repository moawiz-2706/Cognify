"""Database configuration and models."""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.config import settings
from app.models import DifficultyLevel, CardStatus

# Database setup - lazy initialization to avoid import errors
_engine = None
_SessionLocal = None
Base = declarative_base()

def get_engine():
    """Get or create database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(settings.database_url)
        except Exception as e:
            # If database is not available, return None
            print(f"Warning: Could not initialize database: {e}")
            return None
    return _engine

def get_session_local():
    """Get or create session maker (lazy initialization)."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        if engine is None:
            return None
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal

# For backward compatibility, try to create engine (but don't fail if it doesn't work)
try:
    engine = get_engine()
    SessionLocal = get_session_local()
except Exception:
    engine = None
    SessionLocal = None


class User(Base):
    """User database model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    flashcards = relationship("Flashcard", back_populates="owner")
    review_sessions = relationship("ReviewSession", back_populates="user")


class Flashcard(Base):
    """Flashcard database model."""
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    tags = Column(Text)  # JSON string of tags
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    status = Column(SQLEnum(CardStatus), default=CardStatus.NEW)
    difficulty_score = Column(Float, default=0.5)
    next_review_time = Column(DateTime(timezone=True))
    review_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="flashcards")
    review_sessions = relationship("ReviewSession", back_populates="flashcard")


class ReviewSession(Base):
    """Review session database model."""
    __tablename__ = "review_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    response_accuracy = Column(Float, nullable=False)
    response_time = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    flashcard = relationship("Flashcard", back_populates="review_sessions")
    user = relationship("User", back_populates="review_sessions")


def get_db():
    """Get database session (lazy initialization)."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Database dependencies may not be installed.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Cannot create tables: Database engine not available.")
    Base.metadata.create_all(bind=engine)
