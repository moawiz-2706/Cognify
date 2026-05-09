"""Analytics routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.models import LearningAnalytics
from app.services.analytics_service import AnalyticsService
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/learning", response_model=LearningAnalytics)
async def get_learning_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learning analytics for the current user."""
    service = AnalyticsService(db)
    return service.get_learning_analytics(current_user.id)


@router.get("/detailed")
async def get_detailed_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed analytics with charts data."""
    service = AnalyticsService(db)
    return service.get_detailed_analytics(current_user.id)


@router.get("/quick-stats")
async def get_quick_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quick stats for dashboard."""
    service = AnalyticsService(db)
    return service.get_quick_stats(current_user.id)


@router.get("/activity")
async def get_recent_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent study activity."""
    service = AnalyticsService(db)
    analytics = service.get_detailed_analytics(current_user.id)
    return {"recent_activity": analytics["recent_activity"]}


@router.get("/streak")
async def get_study_streak(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current study streak."""
    service = AnalyticsService(db)
    analytics = service.get_learning_analytics(current_user.id)
    return {
        "study_streak": analytics.study_streak,
        "last_study_date": analytics.last_study_date
    }


@router.get("/trend")
async def get_performance_trend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get 7-day performance trend."""
    service = AnalyticsService(db)
    analytics = service.get_learning_analytics(current_user.id)
    return {"performance_trend": analytics.performance_trend}


@router.get("/status-distribution")
async def get_status_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get card status distribution."""
    service = AnalyticsService(db)
    analytics = service.get_detailed_analytics(current_user.id)
    return {"status_distribution": analytics["status_distribution"]}


@router.get("/difficulty-distribution")
async def get_difficulty_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get difficulty distribution."""
    service = AnalyticsService(db)
    analytics = service.get_detailed_analytics(current_user.id)
    return {"difficulty_distribution": analytics["difficulty_distribution"]}


@router.get("/accuracy-by-difficulty")
async def get_accuracy_by_difficulty(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get accuracy grouped by difficulty."""
    service = AnalyticsService(db)
    analytics = service.get_detailed_analytics(current_user.id)
    return {"accuracy_by_difficulty": analytics["accuracy_by_difficulty"]}


@router.get("/daily-study-time")
async def get_daily_study_time(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily study time for last 7 days."""
    service = AnalyticsService(db)
    analytics = service.get_detailed_analytics(current_user.id)
    return {"daily_study_time": analytics["daily_study_time"]}


@router.get("/mastery-timeline")
async def get_mastery_timeline(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mastery progress over time."""
    service = AnalyticsService(db)
    analytics = service.get_detailed_analytics(current_user.id)
    return {"mastery_timeline": analytics["mastery_timeline"]}

