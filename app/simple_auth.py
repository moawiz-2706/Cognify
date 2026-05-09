"""Simple authentication system with session storage."""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException, status


class SimpleAuth:
    """Simple in-memory authentication system."""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {
            "admin": {
                "username": "admin",
                "password": "admin123",  # In production, hash this
                "email": "admin@example.com",
                "created_at": datetime.now()
            },
            "student": {
                "username": "student",
                "password": "student123",
                "email": "student@example.com",
                "created_at": datetime.now()
            }
        }
        self.sessions: Dict[str, Dict] = {}  # session_id -> user_data
    
    def register(self, username: str, password: str, email: str = "") -> Dict:
        """Register a new user."""
        if username in self.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        self.users[username] = {
            "username": username,
            "password": password,  # In production, hash this
            "email": email,
            "created_at": datetime.now()
        }
        
        return {
            "username": username,
            "email": email,
            "created_at": self.users[username]["created_at"]
        }
    
    def login(self, username: str, password: str) -> Dict:
        """Login and create session."""
        if username not in self.users:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        user = self.users[username]
        if user["password"] != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=30)  # 30 day session
        self.sessions[session_id] = {
            "username": username,
            "created_at": datetime.now(),
            "expires_at": expires_at
        }
        
        return {
            "session_id": session_id,
            "username": username,
            "email": user.get("email", ""),
            "expires_at": expires_at.isoformat()  # Convert to ISO string for JSON serialization
        }
    
    def get_user_from_session(self, session_id: str) -> Optional[Dict]:
        """Get user from session."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session expired
        if datetime.now() > session["expires_at"]:
            del self.sessions[session_id]
            return None
        
        username = session["username"]
        if username not in self.users:
            return None
        
        user = self.users[username].copy()
        user.pop("password", None)  # Don't return password
        return user
    
    def logout(self, session_id: str) -> bool:
        """Logout and remove session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        if username not in self.users:
            return None
        user = self.users[username].copy()
        user.pop("password", None)
        return user


# Global auth instance
simple_auth = SimpleAuth()

