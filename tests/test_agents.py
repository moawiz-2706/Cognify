"""Tests for AI agents functionality."""

import pytest
from datetime import datetime, timedelta
from app.agents.cognify_agent import CognifyAgent, AgentInput, AgentOutput


class TestCognifyAgent:
    """Test cases for the Cognify Agent."""
    
    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        agent = CognifyAgent()
        assert agent is not None
        assert agent.graph is not None
    
    def test_analyze_performance_high_accuracy(self):
        """Test performance analysis with high accuracy."""
        agent = CognifyAgent()
        
        # Test with high accuracy and good response time
        state = {
            "user_id": "test_user",
            "flashcard_id": "test_card",
            "response_accuracy": 0.9,
            "response_time": 8.0,
            "current_difficulty": 0.5,
            "review_count": 0,
            "correct_count": 0,
            "next_review_time": datetime.now(),
            "difficulty_score": 0.5,
            "recommendation": "",
            "performance_analysis": {}
        }
        
        result = agent.analyze_performance(state)
        
        # Should increase difficulty for high performance
        assert result["difficulty_score"] > state["current_difficulty"]
        assert "performance_analysis" in result
        assert result["performance_analysis"]["performance_score"] > 0.8
    
    def test_analyze_performance_low_accuracy(self):
        """Test performance analysis with low accuracy."""
        agent = CognifyAgent()
        
        # Test with low accuracy
        state = {
            "user_id": "test_user",
            "flashcard_id": "test_card",
            "response_accuracy": 0.3,
            "response_time": 25.0,
            "current_difficulty": 0.5,
            "review_count": 0,
            "correct_count": 0,
            "next_review_time": datetime.now(),
            "difficulty_score": 0.5,
            "recommendation": "",
            "performance_analysis": {}
        }
        
        result = agent.analyze_performance(state)
        
        # Should decrease difficulty for low performance
        assert result["difficulty_score"] < state["current_difficulty"]
        assert result["performance_analysis"]["performance_score"] < 0.5
    
    def test_update_schedule_good_performance(self):
        """Test schedule update for good performance."""
        agent = CognifyAgent()
        
        state = {
            "user_id": "test_user",
            "flashcard_id": "test_card",
            "response_accuracy": 0.8,
            "response_time": 10.0,
            "current_difficulty": 0.5,
            "review_count": 0,
            "correct_count": 0,
            "next_review_time": datetime.now(),
            "difficulty_score": 0.7,
            "recommendation": "",
            "performance_analysis": {
                "performance_score": 0.8,
                "time_score": 0.9,
                "accuracy_score": 0.8,
                "difficulty_change": 0.2
            }
        }
        
        result = agent.update_schedule(state)
        
        # Should schedule next review further in the future
        next_review = result["next_review_time"]
        current_time = datetime.now()
        time_diff = (next_review - current_time).total_seconds() / 3600  # hours
        
        assert time_diff > 24  # Should be more than 24 hours
    
    def test_update_schedule_poor_performance(self):
        """Test schedule update for poor performance."""
        agent = CognifyAgent()
        
        state = {
            "user_id": "test_user",
            "flashcard_id": "test_card",
            "response_accuracy": 0.4,
            "response_time": 30.0,
            "current_difficulty": 0.5,
            "review_count": 0,
            "correct_count": 0,
            "next_review_time": datetime.now(),
            "difficulty_score": 0.3,
            "recommendation": "",
            "performance_analysis": {
                "performance_score": 0.4,
                "time_score": 0.5,
                "accuracy_score": 0.4,
                "difficulty_change": -0.2
            }
        }
        
        result = agent.update_schedule(state)
        
        # Should schedule next review sooner
        next_review = result["next_review_time"]
        current_time = datetime.now()
        time_diff = (next_review - current_time).total_seconds() / 3600  # hours
        
        assert time_diff < 24  # Should be less than 24 hours
    
    def test_generate_recommendation_high_accuracy(self):
        """Test recommendation generation for high accuracy."""
        agent = CognifyAgent()
        
        state = {
            "user_id": "test_user",
            "flashcard_id": "test_card",
            "response_accuracy": 0.9,
            "response_time": 5.0,
            "current_difficulty": 0.5,
            "review_count": 0,
            "correct_count": 0,
            "next_review_time": datetime.now(),
            "difficulty_score": 0.7,
            "recommendation": "",
            "performance_analysis": {
                "performance_score": 0.9,
                "time_score": 1.0,
                "accuracy_score": 0.9,
                "difficulty_change": 0.2
            }
        }
        
        result = agent.generate_recommendation(state)
        
        assert "Excellent" in result["recommendation"] or "mastered" in result["recommendation"].lower()
    
    def test_generate_recommendation_low_accuracy(self):
        """Test recommendation generation for low accuracy."""
        agent = CognifyAgent()
        
        state = {
            "user_id": "test_user",
            "flashcard_id": "test_card",
            "response_accuracy": 0.3,
            "response_time": 35.0,
            "current_difficulty": 0.5,
            "review_count": 0,
            "correct_count": 0,
            "next_review_time": datetime.now(),
            "difficulty_score": 0.3,
            "recommendation": "",
            "performance_analysis": {
                "performance_score": 0.3,
                "time_score": 0.3,
                "accuracy_score": 0.3,
                "difficulty_change": -0.2
            }
        }
        
        result = agent.generate_recommendation(state)
        
        assert "attention" in result["recommendation"].lower() or "fundamentals" in result["recommendation"].lower()
    
    def test_calculate_time_score_optimal(self):
        """Test time score calculation for optimal response time."""
        agent = CognifyAgent()
        
        # Test optimal response time (10 seconds)
        time_score = agent._calculate_time_score(10.0)
        assert time_score == 1.0
    
    def test_calculate_time_score_too_fast(self):
        """Test time score calculation for too fast response."""
        agent = CognifyAgent()
        
        # Test too fast response (2 seconds)
        time_score = agent._calculate_time_score(2.0)
        assert time_score < 1.0
        assert time_score > 0.5
    
    def test_calculate_time_score_too_slow(self):
        """Test time score calculation for too slow response."""
        agent = CognifyAgent()
        
        # Test too slow response (30 seconds)
        time_score = agent._calculate_time_score(30.0)
        assert time_score < 1.0
        assert time_score > 0.0
