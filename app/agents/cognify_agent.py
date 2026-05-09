"""Cognify Agent - Adaptive Learning Assistant using LangGraph."""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, TypedDict
import numpy as np
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from app.models import AgentInput, AgentOutput, DifficultyLevel, CardStatus
from app.config import settings


class AgentState(TypedDict):
    """State for the Cognify Agent."""
    user_id: str
    flashcard_id: str
    response_accuracy: float
    response_time: float
    current_difficulty: float
    review_count: int
    correct_count: int
    next_review_time: datetime
    difficulty_score: float
    recommendation: str
    performance_analysis: Dict[str, Any]


class CognifyAgent:
    """Adaptive Learning Assistant Agent."""
    
    def __init__(self):
        """Initialize the Cognify Agent."""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=settings.google_api_key,
            temperature=0.1
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_performance", self.analyze_performance)
        workflow.add_node("update_schedule", self.update_schedule)
        workflow.add_node("generate_recommendation", self.generate_recommendation)
        workflow.add_node("share_learning_data", self.share_learning_data)
        
        # Add edges
        workflow.set_entry_point("analyze_performance")
        workflow.add_edge("analyze_performance", "update_schedule")
        workflow.add_edge("update_schedule", "generate_recommendation")
        workflow.add_edge("generate_recommendation", "share_learning_data")
        workflow.add_edge("share_learning_data", END)
        
        return workflow.compile()
    
    def analyze_performance(self, state: AgentState) -> AgentState:
        """Analyze user performance and update state."""
        accuracy = state["response_accuracy"]
        response_time = state["response_time"]
        
        # Calculate performance metrics
        time_score = self._calculate_time_score(response_time)
        accuracy_score = accuracy
        
        # Weighted performance score
        performance_score = (accuracy_score * 0.7) + (time_score * 0.3)
        
        # Update difficulty based on performance
        if performance_score >= 0.8:
            new_difficulty = min(state["current_difficulty"] + 0.1, 1.0)
        elif performance_score <= 0.4:
            new_difficulty = max(state["current_difficulty"] - 0.1, 0.0)
        else:
            new_difficulty = state["current_difficulty"]
        
        state["difficulty_score"] = new_difficulty
        state["performance_analysis"] = {
            "performance_score": performance_score,
            "time_score": time_score,
            "accuracy_score": accuracy_score,
            "difficulty_change": new_difficulty - state["current_difficulty"]
        }
        
        return state
    
    def update_schedule(self, state: AgentState) -> AgentState:
        """Update the review schedule based on performance."""
        performance_score = state["performance_analysis"]["performance_score"]
        difficulty = state["difficulty_score"]
        
        # Calculate next review time using spaced repetition algorithm
        if performance_score >= 0.8:
            # Good performance - increase interval
            interval_multiplier = 2.0 + (difficulty * 0.5)
            next_interval = max(1, int(24 * interval_multiplier))  # hours
        elif performance_score >= 0.6:
            # Moderate performance - maintain interval
            next_interval = 24  # 24 hours
        else:
            # Poor performance - decrease interval
            next_interval = max(1, int(6 / (1 + difficulty)))  # hours
        
        state["next_review_time"] = datetime.now() + timedelta(hours=next_interval)
        
        return state
    
    def generate_recommendation(self, state: AgentState) -> AgentState:
        """Generate personalized learning recommendations."""
        performance = state["performance_analysis"]
        accuracy = state["response_accuracy"]
        response_time = state["response_time"]
        
        # Create recommendation based on performance
        if accuracy >= 0.9 and response_time < 5.0:
            recommendation = "Excellent! You've mastered this concept. Consider moving to more challenging material."
        elif accuracy >= 0.7:
            recommendation = "Good progress! Keep practicing to solidify your understanding."
        elif accuracy >= 0.5:
            recommendation = "You're making progress. Try breaking down the concept into smaller parts."
        else:
            recommendation = "This concept needs more attention. Consider reviewing the fundamentals and practicing more."
        
        # Add specific suggestions based on response time
        if response_time > 30.0:
            recommendation += " Take your time to think through the problem thoroughly."
        elif response_time < 2.0:
            recommendation += " You're responding quickly - make sure you're not rushing."
        
        state["recommendation"] = recommendation
        return state
    
    def share_learning_data(self, state: AgentState) -> AgentState:
        """Share learning data with supervisor agent (placeholder for future implementation)."""
        # This would communicate with a supervisor agent for broader analysis
        # For now, we'll just log the data
        learning_data = {
            "user_id": state["user_id"],
            "flashcard_id": state["flashcard_id"],
            "performance_metrics": state["performance_analysis"],
            "next_review_time": state["next_review_time"],
            "difficulty_score": state["difficulty_score"]
        }
        
        # In a real implementation, this would send data to a supervisor agent
        print(f"Learning data shared: {learning_data}")
        
        return state
    
    def _calculate_time_score(self, response_time: float) -> float:
        """Calculate time-based performance score."""
        # Optimal response time is between 5-15 seconds
        if 5 <= response_time <= 15:
            return 1.0
        elif response_time < 5:
            # Too fast might indicate guessing
            return max(0.5, 1.0 - (5 - response_time) * 0.1)
        else:
            # Too slow indicates difficulty
            return max(0.1, 1.0 - (response_time - 15) * 0.05)
    
    async def process_review(self, input_data: AgentInput) -> AgentOutput:
        """Process a review session and return recommendations."""
        # Initialize state
        initial_state = AgentState(
            user_id=input_data.user_id,
            flashcard_id=input_data.flashcard_id,
            response_accuracy=input_data.response_accuracy,
            response_time=input_data.response_time,
            current_difficulty=0.5,  # Default difficulty
            review_count=0,
            correct_count=0,
            next_review_time=datetime.now(),
            difficulty_score=0.5,
            recommendation="",
            performance_analysis={}
        )
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state)
        
        return AgentOutput(
            next_review_time=result["next_review_time"],
            difficulty_score=result["difficulty_score"],
            recommendation=result["recommendation"]
        )


# Global agent instance
cognify_agent = CognifyAgent()
