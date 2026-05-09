"""Simple in-memory service for flashcards with user support and proper spaced repetition."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import random
from app.simple_models import (
    Flashcard, FlashcardCreate, FlashcardUpdate, 
    ReviewSessionCreate, LearningAnalytics, CardStatus,
    UserPreferences, UserPreferencesUpdate, DegreeProgram
)
from app.curriculum import get_curriculum, get_semester_courses, get_course_by_code
from app.course_flashcards import get_flashcards_for_courses

# Import gemini_service directly to avoid database dependencies
try:
    from app.services.gemini_service import get_gemini_service
except ImportError:
    # Fallback if import fails
    def get_gemini_service():
        return None


class SimpleFlashcardService:
    """Simple in-memory flashcard service with user support and spaced repetition."""
    
    def __init__(self):
        # Store data per user: username -> user_data
        self.user_data: Dict[str, Dict[str, Any]] = {}
    
    def _init_user_data(self, username: str):
        """Initialize data for a user."""
        if username not in self.user_data:
            self.user_data[username] = {
                "flashcards": {},
                "review_sessions": [],
                "next_id": 1,
                "user_preferences": UserPreferences()
            }
    
    def _get_user_data(self, username: str = "default") -> Dict[str, Any]:
        """Get user data, creating if needed."""
        self._init_user_data(username)
        return self.user_data[username]
    
    def generate_flashcards_for_courses(self, course_codes: List[str], username: str = "default") -> int:
        """Generate flashcards for selected courses using Gemini API. Returns count of flashcards created."""
        count = 0
        gemini_service = get_gemini_service()
        user_data = self._get_user_data(username)
        flashcards = user_data["flashcards"]
        next_id = user_data["next_id"]
        
        for course_code in course_codes:
            try:
                # Get course information
                course = get_course_by_code(course_code)
                course_name = course.name
                
                # Try to generate flashcards using Gemini API
                flashcards_data = []
                if gemini_service:
                    try:
                        flashcards_data = gemini_service.generate_flashcards_for_course(
                            course_code=course_code,
                            course_name=course_name,
                            num_flashcards=10
                        )
                        print(f"Generated {len(flashcards_data)} flashcards for {course_code} using Gemini API")
                    except Exception as e:
                        print(f"Error generating flashcards with Gemini for {course_code}: {e}")
                        flashcards_data = get_flashcards_for_courses([course_code])
                else:
                    print(f"Gemini service not available, using hardcoded flashcards for {course_code}")
                    flashcards_data = get_flashcards_for_courses([course_code])
                
                # Create flashcards from generated data
                for card_data in flashcards_data:
                    # Check if flashcard already exists (by front text)
                    existing = any(f.front == card_data["front"] for f in flashcards.values())
                    if not existing:
                        now = datetime.now()
                        flashcard = Flashcard(
                            id=next_id,
                            front=card_data["front"],
                            back=card_data["back"],
                            tags=card_data.get("tags", [course_code.lower()]),
                            difficulty=card_data.get("difficulty", "medium"),
                            subject=course_code,
                            topic=None,
                            created_at=now,
                            updated_at=now,
                            status=CardStatus.NEW,
                            difficulty_score=0.5,
                            next_review_time=None,
                            review_count=0,
                            correct_count=0
                        )
                        flashcards[next_id] = flashcard
                        next_id += 1
                        count += 1
            except Exception as e:
                print(f"Error processing course {course_code}: {e}")
                try:
                    flashcards_data = get_flashcards_for_courses([course_code])
                    for card_data in flashcards_data:
                        existing = any(f.front == card_data["front"] for f in flashcards.values())
                        if not existing:
                            now = datetime.now()
                            flashcard = Flashcard(
                                id=next_id,
                                front=card_data["front"],
                                back=card_data["back"],
                                tags=card_data.get("tags", [course_code.lower()]),
                                difficulty=card_data.get("difficulty", "medium"),
                                subject=course_code,
                                topic=None,
                                created_at=now,
                                updated_at=now,
                                status=CardStatus.NEW,
                                difficulty_score=0.5,
                                next_review_time=None,
                                review_count=0,
                                correct_count=0
                            )
                            flashcards[next_id] = flashcard
                            next_id += 1
                            count += 1
                except Exception as fallback_error:
                    print(f"Error with fallback flashcards for {course_code}: {fallback_error}")
        
        user_data["next_id"] = next_id
        return count
    
    def update_user_preferences(self, preferences_update: UserPreferencesUpdate, username: str = "default") -> UserPreferences:
        """Update user preferences."""
        user_data = self._get_user_data(username)
        prefs = user_data["user_preferences"]
        
        if preferences_update.degree_program is not None:
            prefs.degree_program = preferences_update.degree_program
        if preferences_update.current_semester is not None:
            prefs.current_semester = preferences_update.current_semester
        if preferences_update.selected_courses is not None:
            old_courses = set(prefs.selected_courses)
            new_courses = set(preferences_update.selected_courses)
            added_courses = new_courses - old_courses
            prefs.selected_courses = preferences_update.selected_courses
            
            # Generate flashcards for newly added courses
            if added_courses:
                self.generate_flashcards_for_courses(list(added_courses), username)
        
        return prefs
    
    def get_user_preferences(self, username: str = "default") -> UserPreferences:
        """Get current user preferences."""
        user_data = self._get_user_data(username)
        return user_data["user_preferences"]
    
    def add_course_to_semester(self, course_code: str, username: str = "default") -> bool:
        """Add a course to the current semester selection."""
        user_data = self._get_user_data(username)
        prefs = user_data["user_preferences"]
        
        if course_code not in prefs.selected_courses:
            prefs.selected_courses.append(course_code)
            try:
                count = self.generate_flashcards_for_courses([course_code], username)
                print(f"Generated {count} flashcards for course {course_code}")
            except Exception as e:
                print(f"Error generating flashcards for {course_code}: {e}")
            return True
        return False
    
    def remove_course_from_semester(self, course_code: str, username: str = "default") -> bool:
        """Remove a course from the current semester selection."""
        user_data = self._get_user_data(username)
        prefs = user_data["user_preferences"]
        
        if course_code in prefs.selected_courses:
            prefs.selected_courses.remove(course_code)
            return True
        return False
    
    def create_flashcard(self, flashcard: FlashcardCreate, username: str = "default") -> Flashcard:
        """Create a new flashcard."""
        user_data = self._get_user_data(username)
        flashcards = user_data["flashcards"]
        next_id = user_data["next_id"]
        
        now = datetime.now()
        db_flashcard = Flashcard(
            id=next_id,
            front=flashcard.front,
            back=flashcard.back,
            tags=flashcard.tags or [],
            difficulty=flashcard.difficulty,
            subject=flashcard.subject,
            topic=flashcard.topic,
            created_at=now,
            updated_at=now,
            status=CardStatus.NEW,
            difficulty_score=0.5,
            next_review_time=None,
            review_count=0,
            correct_count=0
        )
        flashcards[next_id] = db_flashcard
        user_data["next_id"] = next_id + 1
        return db_flashcard
    
    def get_flashcard(self, flashcard_id: int, username: str = "default") -> Optional[Flashcard]:
        """Get a flashcard by ID."""
        user_data = self._get_user_data(username)
        return user_data["flashcards"].get(flashcard_id)
    
    def get_flashcards(self, skip: int = 0, limit: int = 100, username: str = "default") -> List[Flashcard]:
        """Get all flashcards."""
        user_data = self._get_user_data(username)
        flashcard_list = list(user_data["flashcards"].values())
        return flashcard_list[skip:skip + limit]
    
    def update_flashcard(self, flashcard_id: int, flashcard_update: FlashcardUpdate, username: str = "default") -> Optional[Flashcard]:
        """Update a flashcard."""
        user_data = self._get_user_data(username)
        flashcards = user_data["flashcards"]
        
        if flashcard_id not in flashcards:
            return None
        
        db_flashcard = flashcards[flashcard_id]
        update_data = flashcard_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_flashcard, field, value)
        
        db_flashcard.updated_at = datetime.now()
        return db_flashcard
    
    def delete_flashcard(self, flashcard_id: int, username: str = "default") -> bool:
        """Delete a flashcard."""
        user_data = self._get_user_data(username)
        flashcards = user_data["flashcards"]
        
        if flashcard_id in flashcards:
            del flashcards[flashcard_id]
            return True
        return False
    
    def get_due_flashcards(self, username: str = "default") -> List[Flashcard]:
        """Get flashcards that are due for review."""
        user_data = self._get_user_data(username)
        flashcards = user_data["flashcards"]
        now = datetime.now()
        due_cards = []
        
        for flashcard in flashcards.values():
            if (flashcard.next_review_time is None or 
                flashcard.next_review_time <= now):
                due_cards.append(flashcard)
        
        return due_cards
    
    def process_review(
        self, 
        review_data: ReviewSessionCreate, 
        user_answer: Optional[str] = None,
        username: str = "default"
    ) -> Dict[str, Any]:
        """Process a review session with detailed explanations and spaced repetition."""
        user_data = self._get_user_data(username)
        flashcards = user_data["flashcards"]
        review_sessions = user_data["review_sessions"]
        
        flashcard = self.get_flashcard(review_data.flashcard_id, username)
        if not flashcard:
            raise ValueError("Flashcard not found")
        
        # Create review session record
        review_session = {
            "id": len(review_sessions) + 1,
            "flashcard_id": review_data.flashcard_id,
            "response_accuracy": review_data.response_accuracy,
            "response_time": review_data.response_time,
            "created_at": datetime.now()
        }
        review_sessions.append(review_session)
        
        # Update flashcard statistics
        flashcard.review_count += 1
        if review_data.response_accuracy >= 0.7:
            flashcard.correct_count += 1
        
        # Generate detailed explanation if answer is incorrect
        detailed_explanation = None
        gemini_service = get_gemini_service()
        if gemini_service and user_answer and review_data.response_accuracy < 0.8:
            try:
                detailed_explanation = gemini_service.generate_detailed_explanation(
                    question=flashcard.front,
                    correct_answer=flashcard.back,
                    user_answer=user_answer,
                    accuracy=review_data.response_accuracy
                )
            except Exception as e:
                print(f"Error generating explanation: {e}")
                detailed_explanation = f"The correct answer is: {flashcard.back}. Review the material to better understand this concept."
        
        # Spaced Repetition Algorithm (SM-2 inspired with long-term/short-term memory)
        agent_output = self._calculate_spaced_repetition(
            accuracy=review_data.response_accuracy,
            response_time=review_data.response_time,
            current_difficulty=flashcard.difficulty_score,
            review_count=flashcard.review_count,
            correct_count=flashcard.correct_count
        )
        
        # Add detailed explanation to agent output
        if detailed_explanation:
            agent_output["detailed_explanation"] = detailed_explanation
        
        # Update flashcard with agent recommendations
        flashcard.difficulty_score = agent_output["difficulty_score"]
        flashcard.next_review_time = agent_output["next_review_time"]
        
        # Update status based on performance (long-term memory indicator)
        if review_data.response_accuracy >= 0.9 and flashcard.review_count >= 3 and flashcard.correct_count >= 2:
            flashcard.status = CardStatus.MASTERED  # Long-term memory
        elif review_data.response_accuracy >= 0.7:
            flashcard.status = CardStatus.LEARNING  # Short-term memory
        else:
            flashcard.status = CardStatus.NEW
        
        return {
            "review_session": review_session,
            "agent_output": agent_output,
            "updated_flashcard": flashcard
        }
    
    def _calculate_spaced_repetition(
        self, 
        accuracy: float, 
        response_time: float,
        current_difficulty: float,
        review_count: int,
        correct_count: int
    ) -> Dict[str, Any]:
        """
        Spaced Repetition Algorithm with Long-term and Short-term Memory.
        
        Based on SM-2 algorithm with modifications for adaptive learning.
        """
        # Calculate ease factor (EF) - determines interval multiplier
        if review_count == 0:
            # First review
            ease_factor = 2.5
        else:
            # Adjust ease factor based on performance
            if accuracy >= 0.9:
                ease_factor = min(2.5, current_difficulty + 0.15)  # Increase ease
            elif accuracy >= 0.7:
                ease_factor = current_difficulty  # Maintain ease
            elif accuracy >= 0.5:
                ease_factor = max(1.3, current_difficulty - 0.2)  # Decrease ease
            else:
                ease_factor = max(1.3, current_difficulty - 0.3)  # Significant decrease
        
        # Calculate interval based on review count and performance
        if review_count == 0:
            # First review - short-term memory (1 day)
            interval_days = 1
        elif review_count == 1:
            # Second review - short-term memory (3 days)
            interval_days = 3
        elif review_count >= 2 and accuracy >= 0.8:
            # Long-term memory - exponential spacing
            previous_interval = 3 * (ease_factor ** (review_count - 2))
            interval_days = int(previous_interval * ease_factor)
            # Cap at 365 days for very well-known cards
            interval_days = min(interval_days, 365)
        else:
            # Still in short-term memory - shorter intervals
            interval_days = max(1, int(3 * ease_factor))
        
        # Adjust based on response time
        if response_time < 3.0 and accuracy >= 0.8:
            # Very fast and correct - can extend interval
            interval_days = int(interval_days * 1.2)
        elif response_time > 20.0 and accuracy < 0.7:
            # Slow and incorrect - reduce interval
            interval_days = max(1, int(interval_days * 0.7))
        
        next_review_time = datetime.now() + timedelta(days=interval_days)
        
        # Update difficulty score
        if accuracy >= 0.9:
            difficulty_score = min(1.0, current_difficulty + 0.1)
        elif accuracy >= 0.7:
            difficulty_score = min(0.9, current_difficulty + 0.05)
        elif accuracy >= 0.5:
            difficulty_score = max(0.2, current_difficulty - 0.05)
        else:
            difficulty_score = max(0.1, current_difficulty - 0.1)
        
        # Generate recommendation
        if accuracy >= 0.9 and review_count >= 3:
            recommendation = "🌟 Excellent! This is in your long-term memory. Great job!"
        elif accuracy >= 0.8:
            recommendation = "✅ Very good! You're building strong memory of this concept."
        elif accuracy >= 0.7:
            recommendation = "👍 Good progress! This is moving to short-term memory."
        elif accuracy >= 0.5:
            recommendation = "🟡 Keep practicing. Review the fundamentals to strengthen memory."
        else:
            recommendation = "📚 This needs more attention. Focus on understanding the basics."
        
        return {
            "next_review_time": next_review_time,
            "difficulty_score": difficulty_score,
            "recommendation": recommendation,
            "interval_days": interval_days,
            "ease_factor": ease_factor,
            "memory_type": "long-term" if review_count >= 2 and accuracy >= 0.8 else "short-term"
        }
    
    def get_learning_analytics(self, username: str = "default") -> LearningAnalytics:
        """Get comprehensive learning analytics."""
        user_data = self._get_user_data(username)
        flashcards = list(user_data["flashcards"].values())
        review_sessions = user_data["review_sessions"]
        
        total_cards = len(flashcards)
        mastered_cards = len([f for f in flashcards if f.status == CardStatus.MASTERED])
        learning_cards = len([f for f in flashcards if f.status == CardStatus.LEARNING])
        review_cards = len([f for f in flashcards if f.status == CardStatus.REVIEW])
        
        # Calculate average accuracy from ALL reviews
        if review_sessions:
            average_accuracy = sum(r["response_accuracy"] for r in review_sessions) / len(review_sessions)
            average_accuracy = round(average_accuracy, 2)
        else:
            average_accuracy = 0.0
        
        # Calculate study streak - consecutive days with reviews
        study_streak = 0
        if review_sessions:
            study_dates = set()
            for session in review_sessions:
                study_date = session["created_at"].date()
                study_dates.add(study_date)
            
            sorted_dates = sorted(study_dates, reverse=True)
            current_date = datetime.now().date()
            streak = 0
            expected_date = current_date
            
            for study_date in sorted_dates:
                if study_date == expected_date or study_date == expected_date - timedelta(days=1):
                    streak += 1
                    expected_date = study_date - timedelta(days=1)
                else:
                    break
            
            study_streak = streak
        
        # Get last study date
        last_study_date = None
        if review_sessions:
            last_session = max(review_sessions, key=lambda x: x["created_at"])
            last_study_date = last_session["created_at"]
        
        # Generate performance trend (last 7 days)
        performance_trend = []
        if review_sessions:
            daily_performance = {}
            for session in review_sessions:
                day = session["created_at"].date()
                if day not in daily_performance:
                    daily_performance[day] = []
                daily_performance[day].append(session["response_accuracy"])
            
            for i in range(6, -1, -1):
                date = (datetime.now() - timedelta(days=i)).date()
                if date in daily_performance:
                    avg_accuracy = sum(daily_performance[date]) / len(daily_performance[date])
                    performance_trend.append(round(avg_accuracy, 2))
                else:
                    performance_trend.append(0.0)
        else:
            performance_trend = [0.0] * 7
        
        return LearningAnalytics(
            total_cards=total_cards,
            mastered_cards=mastered_cards,
            learning_cards=learning_cards,
            review_cards=review_cards,
            average_accuracy=average_accuracy,
            study_streak=study_streak,
            last_study_date=last_study_date,
            performance_trend=performance_trend
        )


# Global service instance
flashcard_service = SimpleFlashcardService()

