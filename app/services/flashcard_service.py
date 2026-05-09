"""Flashcard service for CRUD operations and learning logic."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.database import Flashcard, ReviewSession, User
from app.models import FlashcardCreate, FlashcardUpdate, ReviewSessionCreate, LearningAnalytics


class FlashcardService:
    """Service for flashcard operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_flashcard(self, flashcard: FlashcardCreate, user_id: int) -> Flashcard:
        """Create a new flashcard."""
        db_flashcard = Flashcard(
            front=flashcard.front,
            back=flashcard.back,
            tags=str(flashcard.tags) if flashcard.tags else None,
            difficulty=flashcard.difficulty,
            user_id=user_id,
            status="new",
            difficulty_score=0.5,
            review_count=0,
            correct_count=0
        )
        self.db.add(db_flashcard)
        self.db.commit()
        self.db.refresh(db_flashcard)
        return db_flashcard
    
    def get_flashcard(self, flashcard_id: int, user_id: int) -> Optional[Flashcard]:
        """Get a flashcard by ID."""
        return self.db.query(Flashcard).filter(
            and_(Flashcard.id == flashcard_id, Flashcard.user_id == user_id)
        ).first()
    
    def get_flashcards(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Flashcard]:
        """Get all flashcards for a user."""
        return self.db.query(Flashcard).filter(
            Flashcard.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def update_flashcard(self, flashcard_id: int, flashcard_update: FlashcardUpdate, user_id: int) -> Optional[Flashcard]:
        """Update a flashcard."""
        db_flashcard = self.get_flashcard(flashcard_id, user_id)
        if not db_flashcard:
            return None
        
        update_data = flashcard_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_flashcard, field, value)
        
        db_flashcard.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(db_flashcard)
        return db_flashcard
    
    def delete_flashcard(self, flashcard_id: int, user_id: int) -> bool:
        """Delete a flashcard."""
        db_flashcard = self.get_flashcard(flashcard_id, user_id)
        if not db_flashcard:
            return False
        
        # Also delete associated review sessions
        self.db.query(ReviewSession).filter(
            ReviewSession.flashcard_id == flashcard_id
        ).delete()
        
        self.db.delete(db_flashcard)
        self.db.commit()
        return True
    
    def get_due_flashcards(self, user_id: int) -> List[Flashcard]:
        """Get flashcards that are due for review."""
        now = datetime.now()
        return self.db.query(Flashcard).filter(
            and_(
                Flashcard.user_id == user_id,
                or_(
                    Flashcard.next_review_time <= now,
                    Flashcard.next_review_time.is_(None)
                ),
                Flashcard.status != "mastered"
            )
        ).order_by(Flashcard.next_review_time).all()
    
    def process_review(self, review_data: ReviewSessionCreate, user_id: int, user_answer: Optional[str] = None) -> dict:
        """Process a review session using the Cognify Agent with detailed explanations."""
        # Get the flashcard first
        flashcard = self.get_flashcard(review_data.flashcard_id, user_id)
        if not flashcard:
            raise ValueError("Flashcard not found")
        
        # Create review session record
        db_review = ReviewSession(
            flashcard_id=review_data.flashcard_id,
            user_id=user_id,
            response_accuracy=review_data.response_accuracy,
            response_time=review_data.response_time
        )
        self.db.add(db_review)
        self.db.flush()  # Flush to get the ID
        
        # Update flashcard statistics
        flashcard.review_count += 1
        if review_data.response_accuracy >= 0.7:  # Consider 70% as correct
            flashcard.correct_count += 1
        
        # Generate detailed explanation if answer is incorrect
        detailed_explanation = None
        if user_answer and review_data.response_accuracy < 0.8:
            try:
                from app.services.gemini_service import get_gemini_service
                gemini_service = get_gemini_service()
                if gemini_service:
                    detailed_explanation = gemini_service.generate_detailed_explanation(
                        question=flashcard.front,
                        correct_answer=flashcard.back,
                        user_answer=user_answer,
                        accuracy=review_data.response_accuracy
                    )
            except Exception as e:
                print(f"Error generating explanation: {e}")
        
        # Run Cognify Agent algorithm
        agent_output = self._simulate_agent_response(
            response_accuracy=review_data.response_accuracy,
            response_time=review_data.response_time,
            current_difficulty_score=flashcard.difficulty_score,
            review_count=flashcard.review_count
        )
        
        # Add detailed explanation to agent output
        if detailed_explanation:
            agent_output["detailed_explanation"] = detailed_explanation
        
        # Update flashcard with agent recommendations
        flashcard.difficulty_score = agent_output["difficulty_score"]
        flashcard.next_review_time = agent_output["next_review_time"]
        
        # Update status based on performance
        if review_data.response_accuracy >= 0.9 and flashcard.review_count >= 3:
            flashcard.status = "mastered"
        elif review_data.response_accuracy >= 0.7:
            flashcard.status = "learning"
        elif review_data.response_accuracy >= 0.5:
            flashcard.status = "review"
        else:
            flashcard.status = "new"
        
        flashcard.updated_at = datetime.now()
        
        self.db.commit()
        
        return {
            "review_session": db_review,
            "agent_output": agent_output,
            "updated_flashcard": flashcard
        }
    
    def _simulate_agent_response(self, response_accuracy: float, response_time: float, 
                                 current_difficulty_score: float, review_count: int) -> dict:
        """
        Cognify Agent Algorithm - Spaced Repetition with Adaptive Difficulty.
        
        This is the core learning algorithm that determines when to review next
        and how difficult the card should be.
        """
        # Base algorithm: Spaced Repetition
        if response_accuracy >= 0.9:
            # Expert level - user knows it very well
            next_review_hours = 48  # 2 days
            difficulty_score = min(1.0, current_difficulty_score + 0.1)
            recommendation = "🌟 Excellent! You've mastered this concept."
        elif response_accuracy >= 0.75:
            # Good understanding
            next_review_hours = 24  # 1 day
            difficulty_score = min(0.8, current_difficulty_score + 0.05)
            recommendation = "✅ Good progress! Keep practicing."
        elif response_accuracy >= 0.6:
            # Getting there
            next_review_hours = 12  # 12 hours
            difficulty_score = current_difficulty_score
            recommendation = "🟡 You're on the right track. Review the fundamentals."
        elif response_accuracy >= 0.5:
            # Struggling but improving
            next_review_hours = 6  # 6 hours
            difficulty_score = max(0.2, current_difficulty_score - 0.1)
            recommendation = "📚 This needs attention. Try breaking it down."
        else:
            # Not ready
            next_review_hours = 2  # 2 hours
            difficulty_score = max(0.1, current_difficulty_score - 0.2)
            recommendation = "🔄 Let's review this one more time."
        
        # Adjust based on response time
        if response_time < 2.0 and response_accuracy >= 0.8:
            # Fast and correct - can extend interval
            next_review_hours = int(next_review_hours * 1.5)
        elif response_time > 15.0 and response_accuracy < 0.7:
            # Slow and incorrect - reduce interval
            next_review_hours = max(2, int(next_review_hours * 0.75))
        
        next_review_time = datetime.now() + timedelta(hours=next_review_hours)
        
        return {
            "next_review_time": next_review_time,
            "difficulty_score": round(difficulty_score, 2),
            "recommendation": recommendation,
            "next_review_hours": next_review_hours,
            "algorithm": "Spaced Repetition + Adaptive Difficulty"
        }
    
    def get_learning_analytics(self, user_id: int) -> LearningAnalytics:
        """Get learning analytics for a user using complete data from database."""
        # Get all flashcards for user
        flashcards = self.db.query(Flashcard).filter(
            Flashcard.user_id == user_id
        ).all()
        
        total_cards = len(flashcards)
        mastered_cards = len([f for f in flashcards if f.status == "mastered"])
        learning_cards = len([f for f in flashcards if f.status == "learning"])
        review_cards = len([f for f in flashcards if f.status == "review"])
        new_cards = len([f for f in flashcards if f.status == "new"])
        
        # Calculate average accuracy from all reviews
        all_reviews = self.db.query(ReviewSession).filter(
            ReviewSession.user_id == user_id
        ).all()
        
        if all_reviews:
            average_accuracy = sum(r.response_accuracy for r in all_reviews) / len(all_reviews)
        else:
            average_accuracy = 0.0
        
        # Get last study date
        last_review = self.db.query(ReviewSession).filter(
            ReviewSession.user_id == user_id
        ).order_by(desc(ReviewSession.created_at)).first()
        
        last_study_date = last_review.created_at if last_review else None
        
        # Calculate study streak
        study_streak = self._calculate_study_streak(user_id, all_reviews)
        
        # Generate performance trend
        performance_trend = self._generate_performance_trend(user_id, all_reviews)
        
        return LearningAnalytics(
            user_id=user_id,
            total_cards=total_cards,
            mastered_cards=mastered_cards,
            learning_cards=learning_cards,
            review_cards=review_cards,
            average_accuracy=round(average_accuracy, 2),
            study_streak=study_streak,
            last_study_date=last_study_date,
            performance_trend=performance_trend
        )
    
    def _calculate_study_streak(self, user_id: int, reviews: List[ReviewSession]) -> int:
        """Calculate consecutive study days."""
        if not reviews:
            return 0
        
        # Get unique study dates
        study_dates = {}
        for review in reviews:
            date = review.created_at.date()
            if date not in study_dates:
                study_dates[date] = True
        
        if not study_dates:
            return 0
        
        # Sort dates in descending order
        sorted_dates = sorted(study_dates.keys(), reverse=True)
        
        # Calculate streak
        streak = 0
        expected_date = datetime.now().date()
        
        for study_date in sorted_dates:
            if study_date == expected_date or study_date == expected_date - timedelta(days=1):
                streak += 1
                expected_date = study_date - timedelta(days=1)
            else:
                break
        
        return streak
    
    def _generate_performance_trend(self, user_id: int, reviews: List[ReviewSession]) -> List[float]:
        """Generate 7-day performance trend."""
        if not reviews:
            return [0.0] * 7
        
        # Group reviews by date
        daily_performance = {}
        for review in reviews:
            date = review.created_at.date()
            if date not in daily_performance:
                daily_performance[date] = []
            daily_performance[date].append(review.response_accuracy)
        
        # Calculate daily averages for last 7 days
        trend = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).date()
            if date in daily_performance:
                avg = sum(daily_performance[date]) / len(daily_performance[date])
                trend.append(round(avg, 2))
            else:
                trend.append(0.0)
        
        return trend
