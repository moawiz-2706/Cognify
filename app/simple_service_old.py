"""Simple in-memory service for flashcards."""

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
    """Simple in-memory flashcard service with user support."""
    
    def __init__(self):
        # Store data per user: username -> user_data
        self.user_data: Dict[str, Dict[str, Any]] = {}
        # Default user for backward compatibility
        self._init_user_data("default")
    
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
                        # Fallback to hardcoded flashcards
                        flashcards_data = get_flashcards_for_courses([course_code])
                else:
                    # Fallback to hardcoded flashcards if Gemini is not available
                    print(f"Gemini service not available, using hardcoded flashcards for {course_code}")
                    flashcards_data = get_flashcards_for_courses([course_code])
                
                # Create flashcards from generated data
                for card_data in flashcards_data:
                    # Check if flashcard already exists (by front text)
                    existing = any(f.front == card_data["front"] for f in self.flashcards.values())
                    if not existing:
                        now = datetime.now()
                        flashcard = Flashcard(
                            id=self.next_id,
                            front=card_data["front"],
                            back=card_data["back"],
                            tags=card_data.get("tags", [course_code.lower()]),
                            difficulty=card_data.get("difficulty", "medium"),
                            subject=course_code,  # Set from course
                            topic=None,
                            created_at=now,
                            updated_at=now,
                            status=CardStatus.NEW,
                            difficulty_score=0.5,
                            next_review_time=None,
                            review_count=0,
                            correct_count=0
                        )
                        self.flashcards[self.next_id] = flashcard
                        self.next_id += 1
                        count += 1
            except Exception as e:
                print(f"Error processing course {course_code}: {e}")
                # Fallback to hardcoded flashcards
                try:
                    flashcards_data = get_flashcards_for_courses([course_code])
                    for card_data in flashcards_data:
                        existing = any(f.front == card_data["front"] for f in self.flashcards.values())
                        if not existing:
                            now = datetime.now()
                            flashcard = Flashcard(
                                id=self.next_id,
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
                            self.flashcards[self.next_id] = flashcard
                            self.next_id += 1
                            count += 1
                except Exception as fallback_error:
                    print(f"Error with fallback flashcards for {course_code}: {fallback_error}")
        
        return count
    
    def update_user_preferences(self, preferences_update: UserPreferencesUpdate) -> UserPreferences:
        """Update user preferences."""
        if preferences_update.degree_program is not None:
            self.user_preferences.degree_program = preferences_update.degree_program
        if preferences_update.current_semester is not None:
            self.user_preferences.current_semester = preferences_update.current_semester
        if preferences_update.selected_courses is not None:
            # When courses are updated, generate flashcards for new courses
            old_courses = set(self.user_preferences.selected_courses)
            new_courses = set(preferences_update.selected_courses)
            added_courses = new_courses - old_courses
            self.user_preferences.selected_courses = preferences_update.selected_courses
            
            # Generate flashcards for newly added courses
            if added_courses:
                self.generate_flashcards_for_courses(list(added_courses))
        
        return self.user_preferences
    
    def get_user_preferences(self) -> UserPreferences:
        """Get current user preferences."""
        return self.user_preferences
    
    def add_course_to_semester(self, course_code: str) -> bool:
        """Add a course to the current semester selection."""
        if course_code not in self.user_preferences.selected_courses:
            self.user_preferences.selected_courses.append(course_code)
            # Generate flashcards for this course
            try:
                count = self.generate_flashcards_for_courses([course_code])
                print(f"Generated {count} flashcards for course {course_code}")
            except Exception as e:
                print(f"Error generating flashcards for {course_code}: {e}")
                # Continue even if flashcard generation fails
            return True
        return False
    
    def remove_course_from_semester(self, course_code: str) -> bool:
        """Remove a course from the current semester selection."""
        if course_code in self.user_preferences.selected_courses:
            self.user_preferences.selected_courses.remove(course_code)
            # Optionally remove flashcards related to this course
            # For now, we'll keep them but could filter them out
            return True
        return False
    
    def create_flashcard(self, flashcard: FlashcardCreate) -> Flashcard:
        """Create a new flashcard."""
        now = datetime.now()
        db_flashcard = Flashcard(
            id=self.next_id,
            front=flashcard.front,
            back=flashcard.back,
            tags=flashcard.tags or [],
            difficulty=flashcard.difficulty,
            subject=flashcard.subject,
            topic=flashcard.topic,
            created_at=now,
            updated_at=now
        )
        self.flashcards[self.next_id] = db_flashcard
        self.next_id += 1
        return db_flashcard
    
    def get_flashcard(self, flashcard_id: int) -> Optional[Flashcard]:
        """Get a flashcard by ID."""
        return self.flashcards.get(flashcard_id)
    
    def get_flashcards(self, skip: int = 0, limit: int = 100) -> List[Flashcard]:
        """Get all flashcards."""
        flashcard_list = list(self.flashcards.values())
        return flashcard_list[skip:skip + limit]
    
    def update_flashcard(self, flashcard_id: int, flashcard_update: FlashcardUpdate) -> Optional[Flashcard]:
        """Update a flashcard."""
        if flashcard_id not in self.flashcards:
            return None
        
        db_flashcard = self.flashcards[flashcard_id]
        update_data = flashcard_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_flashcard, field, value)
        
        db_flashcard.updated_at = datetime.now()
        return db_flashcard
    
    def delete_flashcard(self, flashcard_id: int) -> bool:
        """Delete a flashcard."""
        if flashcard_id in self.flashcards:
            del self.flashcards[flashcard_id]
            return True
        return False
    
    def get_due_flashcards(self) -> List[Flashcard]:
        """Get flashcards that are due for review."""
        now = datetime.now()
        due_cards = []
        
        for flashcard in self.flashcards.values():
            if (flashcard.next_review_time is None or 
                flashcard.next_review_time <= now):
                due_cards.append(flashcard)
        
        return due_cards
    
    def process_review(
        self, 
        review_data: ReviewSessionCreate, 
        user_answer: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a review session with detailed explanations for incorrect answers."""
        flashcard = self.get_flashcard(review_data.flashcard_id)
        if not flashcard:
            raise ValueError("Flashcard not found")
        
        # Create review session record
        review_session = {
            "id": len(self.review_sessions) + 1,
            "flashcard_id": review_data.flashcard_id,
            "response_accuracy": review_data.response_accuracy,
            "response_time": review_data.response_time,
            "created_at": datetime.now()
        }
        self.review_sessions.append(review_session)
        
        # Update flashcard statistics
        flashcard.review_count += 1
        if review_data.response_accuracy >= 0.7:  # Consider 70% as correct
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
                # Fallback explanation
                detailed_explanation = f"The correct answer is: {flashcard.back}. Review the material to better understand this concept."
        
        # Simple adaptive algorithm
        agent_output = self._simulate_agent_response(review_data)
        
        # Add detailed explanation to agent output
        if detailed_explanation:
            agent_output["detailed_explanation"] = detailed_explanation
        
        # Update flashcard with agent recommendations
        flashcard.difficulty_score = agent_output["difficulty_score"]
        flashcard.next_review_time = agent_output["next_review_time"]
        
        # Update status based on performance
        if review_data.response_accuracy >= 0.9 and flashcard.review_count >= 3:
            flashcard.status = CardStatus.MASTERED
        elif review_data.response_accuracy >= 0.7:
            flashcard.status = CardStatus.LEARNING
        else:
            flashcard.status = CardStatus.NEW
        
        return {
            "review_session": review_session,
            "agent_output": agent_output,
            "updated_flashcard": flashcard
        }
    
    def _simulate_agent_response(self, review_data: ReviewSessionCreate) -> Dict[str, Any]:
        """Simulate agent response with simple algorithm."""
        accuracy = review_data.response_accuracy
        response_time = review_data.response_time
        
        # Simple spaced repetition algorithm
        if accuracy >= 0.8:
            next_review_hours = 24 * 2  # 2 days
            difficulty_score = min(1.0, 0.5 + accuracy * 0.5)
        elif accuracy >= 0.6:
            next_review_hours = 24  # 1 day
            difficulty_score = 0.5
        else:
            next_review_hours = 6  # 6 hours
            difficulty_score = max(0.0, 0.5 - (0.6 - accuracy) * 0.5)
        
        next_review_time = datetime.now() + timedelta(hours=next_review_hours)
        
        # Generate recommendation
        if accuracy >= 0.9:
            recommendation = "Excellent! You've mastered this concept."
        elif accuracy >= 0.7:
            recommendation = "Good progress! Keep practicing."
        elif accuracy >= 0.5:
            recommendation = "You're making progress. Review the fundamentals."
        else:
            recommendation = "This needs more attention. Consider breaking it down."
        
        return {
            "next_review_time": next_review_time,
            "difficulty_score": difficulty_score,
            "recommendation": recommendation
        }
    
    def get_learning_analytics(self) -> LearningAnalytics:
        """Get comprehensive learning analytics."""
        flashcards = list(self.flashcards.values())
        
        total_cards = len(flashcards)
        mastered_cards = len([f for f in flashcards if f.status == CardStatus.MASTERED])
        learning_cards = len([f for f in flashcards if f.status == CardStatus.LEARNING])
        review_cards = len([f for f in flashcards if f.status == CardStatus.REVIEW])
        
        # Calculate average accuracy from ALL reviews (not just recent)
        if self.review_sessions:
            average_accuracy = sum(r["response_accuracy"] for r in self.review_sessions) / len(self.review_sessions)
            average_accuracy = round(average_accuracy, 2)
        else:
            average_accuracy = 0.0
        
        # Calculate study streak - consecutive days with reviews
        study_streak = 0
        if self.review_sessions:
            # Get unique study dates
            study_dates = set()
            for session in self.review_sessions:
                study_date = session["created_at"].date()
                study_dates.add(study_date)
            
            # Sort dates descending
            sorted_dates = sorted(study_dates, reverse=True)
            
            # Calculate streak from today backwards
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
        if self.review_sessions:
            last_session = max(self.review_sessions, key=lambda x: x["created_at"])
            last_study_date = last_session["created_at"]
        
        # Generate performance trend (last 7 days)
        performance_trend = []
        if self.review_sessions:
            # Group reviews by date
            daily_performance = {}
            for session in self.review_sessions:
                day = session["created_at"].date()
                if day not in daily_performance:
                    daily_performance[day] = []
                daily_performance[day].append(session["response_accuracy"])
            
            # Calculate daily averages for last 7 days
            for i in range(6, -1, -1):  # 6 days ago to today
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
