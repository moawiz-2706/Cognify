"""Analytics service for learning progress tracking."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, or_
from app.database import Flashcard, ReviewSession, User
from app.models import LearningAnalytics


class AnalyticsService:
    """Service for learning analytics with comprehensive data."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_learning_analytics(self, user_id: int) -> LearningAnalytics:
        """Get comprehensive learning analytics for a user."""
        # Get basic card statistics
        total_cards = self.db.query(Flashcard).filter(Flashcard.user_id == user_id).count()
        mastered_cards = self.db.query(Flashcard).filter(
            and_(Flashcard.user_id == user_id, Flashcard.status == "mastered")
        ).count()
        learning_cards = self.db.query(Flashcard).filter(
            and_(Flashcard.user_id == user_id, Flashcard.status == "learning")
        ).count()
        review_cards = self.db.query(Flashcard).filter(
            and_(Flashcard.user_id == user_id, Flashcard.status == "review")
        ).count()
        
        # Calculate average accuracy from ALL reviews
        all_reviews = self.db.query(ReviewSession).filter(
            ReviewSession.user_id == user_id
        ).all()
        
        if all_reviews:
            average_accuracy = sum(r.response_accuracy for r in all_reviews) / len(all_reviews)
            average_accuracy = round(average_accuracy, 2)
        else:
            average_accuracy = 0.0
        
        # Calculate study streak
        study_streak = self._calculate_study_streak(user_id)
        
        # Get last study date
        last_review = self.db.query(ReviewSession).filter(
            ReviewSession.user_id == user_id
        ).order_by(desc(ReviewSession.created_at)).first()
        
        last_study_date = last_review.created_at if last_review else None
        
        # Generate performance trend (7-day)
        performance_trend = self._generate_performance_trend(user_id)
        
        return LearningAnalytics(
            user_id=user_id,
            total_cards=total_cards,
            mastered_cards=mastered_cards,
            learning_cards=learning_cards,
            review_cards=review_cards,
            average_accuracy=average_accuracy,
            study_streak=study_streak,
            last_study_date=last_study_date,
            performance_trend=performance_trend
        )
    
    def _calculate_study_streak(self, user_id: int) -> int:
        """Calculate consecutive study days."""
        # Get all unique study dates for this user
        study_dates_query = self.db.query(
            func.date(ReviewSession.created_at).label('study_date')
        ).filter(
            ReviewSession.user_id == user_id
        ).distinct().order_by(desc('study_date')).all()
        
        if not study_dates_query:
            return 0
        
        study_dates = [row.study_date for row in study_dates_query]
        
        # Calculate streak from today backwards
        streak = 0
        current_date = datetime.now().date()
        
        for study_date in study_dates:
            # Check if study_date is today or consecutive day before
            if study_date == current_date or study_date == current_date - timedelta(days=1):
                streak += 1
                current_date = study_date - timedelta(days=1)
            else:
                break
        
        return streak
    
    def _generate_performance_trend(self, user_id: int) -> List[float]:
        """Generate 7-day performance trend data."""
        # Get reviews from the last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        
        reviews = self.db.query(ReviewSession).filter(
            and_(
                ReviewSession.user_id == user_id,
                ReviewSession.created_at >= week_ago
            )
        ).all()
        
        if not reviews:
            return [0.0] * 7
        
        # Group by day and calculate average accuracy
        daily_performance = {}
        for review in reviews:
            day = review.created_at.date()
            if day not in daily_performance:
                daily_performance[day] = []
            daily_performance[day].append(review.response_accuracy)
        
        # Calculate daily averages for each of the last 7 days
        trend = []
        for i in range(6, -1, -1):  # 6 days ago to today
            date = (datetime.now() - timedelta(days=i)).date()
            if date in daily_performance:
                avg_accuracy = sum(daily_performance[date]) / len(daily_performance[date])
                trend.append(round(avg_accuracy, 2))
            else:
                trend.append(0.0)
        
        return trend
    
    def get_detailed_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get detailed analytics with charts data."""
        # Get basic analytics
        analytics = self.get_learning_analytics(user_id)
        
        # Get all flashcards and reviews for this user
        flashcards = self.db.query(Flashcard).filter(
            Flashcard.user_id == user_id
        ).all()
        
        reviews = self.db.query(ReviewSession).filter(
            ReviewSession.user_id == user_id
        ).all()
        
        # 1. Card status distribution
        status_dist = {
            "new": len([f for f in flashcards if f.status == "new"]),
            "learning": len([f for f in flashcards if f.status == "learning"]),
            "review": len([f for f in flashcards if f.status == "review"]),
            "mastered": len([f for f in flashcards if f.status == "mastered"])
        }
        
        # 2. Difficulty distribution
        difficulty_dist = {}
        for flashcard in flashcards:
            diff = flashcard.difficulty if flashcard.difficulty else "medium"
            if diff not in difficulty_dist:
                difficulty_dist[diff] = 0
            difficulty_dist[diff] += 1
        
        # 3. Review count distribution
        review_count_dist = self._get_review_count_distribution(flashcards)
        
        # 4. Accuracy by difficulty
        accuracy_by_difficulty = self._get_accuracy_by_difficulty(reviews, flashcards)
        
        # 5. Recent activity (last 10 reviews)
        recent_activity = self._get_recent_activity(reviews)
        
        # 6. Study time analysis (average time per day)
        daily_study_time = self._get_daily_study_time(reviews)
        
        # 7. Cumulative mastery over time
        mastery_timeline = self._get_mastery_timeline(reviews, flashcards)
        
        return {
            "basic_analytics": analytics.dict(),
            "status_distribution": status_dist,
            "difficulty_distribution": difficulty_dist,
            "review_count_distribution": review_count_dist,
            "accuracy_by_difficulty": accuracy_by_difficulty,
            "daily_study_time": daily_study_time,
            "mastery_timeline": mastery_timeline,
            "recent_activity": recent_activity,
            "total_reviews": len(reviews),
            "average_reviews_per_card": len(reviews) / len(flashcards) if flashcards else 0,
            "total_study_time_minutes": sum(r.response_time for r in reviews) / 60
        }
    
    def _get_review_count_distribution(self, flashcards: List[Flashcard]) -> Dict[str, int]:
        """Get distribution of review counts."""
        ranges = {
            "0": 0,
            "1-3": 0,
            "4-6": 0,
            "7-10": 0,
            "10+": 0
        }
        
        for flashcard in flashcards:
            count = flashcard.review_count
            if count == 0:
                ranges["0"] += 1
            elif count <= 3:
                ranges["1-3"] += 1
            elif count <= 6:
                ranges["4-6"] += 1
            elif count <= 10:
                ranges["7-10"] += 1
            else:
                ranges["10+"] += 1
        
        return ranges
    
    def _get_accuracy_by_difficulty(self, reviews: List[ReviewSession], flashcards: List[Flashcard]) -> Dict[str, float]:
        """Get average accuracy grouped by difficulty level."""
        accuracy_data = {}
        
        for flashcard in flashcards:
            difficulty = flashcard.difficulty if flashcard.difficulty else "medium"
            if difficulty not in accuracy_data:
                accuracy_data[difficulty] = []
        
        for review in reviews:
            flashcard = next((f for f in flashcards if f.id == review.flashcard_id), None)
            if flashcard:
                difficulty = flashcard.difficulty if flashcard.difficulty else "medium"
                if difficulty in accuracy_data:
                    accuracy_data[difficulty].append(review.response_accuracy)
        
        # Calculate averages
        averages = {}
        for difficulty, accuracies in accuracy_data.items():
            if accuracies:
                averages[difficulty] = round(sum(accuracies) / len(accuracies), 2)
            else:
                averages[difficulty] = 0.0
        
        return averages
    
    def _get_recent_activity(self, reviews: List[ReviewSession], limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent study activity."""
        recent = sorted(reviews, key=lambda r: r.created_at, reverse=True)[:limit]
        
        activity = []
        for review in recent:
            activity.append({
                "date": review.created_at.isoformat(),
                "accuracy": review.response_accuracy,
                "response_time": round(review.response_time, 2),
                "flashcard_id": review.flashcard_id
            })
        
        return activity
    
    def _get_daily_study_time(self, reviews: List[ReviewSession]) -> List[Dict[str, Any]]:
        """Get study time by day for last 7 days."""
        daily_data = {}
        
        for review in reviews:
            day = review.created_at.date()
            if day not in daily_data:
                daily_data[day] = {"count": 0, "total_time": 0.0}
            daily_data[day]["count"] += 1
            daily_data[day]["total_time"] += review.response_time
        
        # Generate for last 7 days
        result = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).date()
            if date in daily_data:
                result.append({
                    "date": date.isoformat(),
                    "reviews": daily_data[date]["count"],
                    "total_time_minutes": round(daily_data[date]["total_time"] / 60, 2),
                    "average_time_seconds": round(daily_data[date]["total_time"] / daily_data[date]["count"], 2)
                })
            else:
                result.append({
                    "date": date.isoformat(),
                    "reviews": 0,
                    "total_time_minutes": 0.0,
                    "average_time_seconds": 0.0
                })
        
        return result
    
    def _get_mastery_timeline(self, reviews: List[ReviewSession], flashcards: List[Flashcard]) -> List[Dict[str, Any]]:
        """Get mastery progress over time."""
        # Sort reviews by date
        sorted_reviews = sorted(reviews, key=lambda r: r.created_at)
        
        if not sorted_reviews:
            return []
        
        # Track mastery count over time
        timeline = []
        mastered_count = 0
        current_date = None
        
        for review in sorted_reviews:
            day = review.created_at.date()
            
            # Get the flashcard at that time
            flashcard = next((f for f in flashcards if f.id == review.flashcard_id), None)
            if flashcard:
                # Check if it should be considered mastered
                if review.response_accuracy >= 0.9:
                    if current_date != day:
                        mastered_count += 1
                        current_date = day
                        timeline.append({
                            "date": day.isoformat(),
                            "mastered_cards": mastered_count
                        })
        
        # Fill gaps in timeline for last 7 days
        last_mastered = mastered_count
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).date()
            if not timeline or timeline[-1]["date"] < date.isoformat():
                timeline.append({
                    "date": date.isoformat(),
                    "mastered_cards": last_mastered
                })
        
        return timeline
    
    def get_quick_stats(self, user_id: int) -> Dict[str, Any]:
        """Get quick stats for dashboard."""
        analytics = self.get_learning_analytics(user_id)
        
        total_cards = analytics.total_cards
        mastered = analytics.mastered_cards
        
        return {
            "total_cards": total_cards,
            "mastered": mastered,
            "mastery_percentage": round((mastered / total_cards * 100) if total_cards > 0 else 0, 1),
            "average_accuracy": analytics.average_accuracy,
            "study_streak": analytics.study_streak,
            "last_study": analytics.last_study_date.isoformat() if analytics.last_study_date else None,
            "due_cards": self._get_due_card_count(user_id),
            "performance_trend": analytics.performance_trend
        }
    
    def _get_due_card_count(self, user_id: int) -> int:
        """Get count of cards due for review."""
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
        ).count()
