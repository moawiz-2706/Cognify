"""MongoDB-based authentication system."""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException, status
from app.mongodb import get_database

# Try to use bcrypt, fallback to simple hashing
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    USE_BCRYPT = True
except Exception as e:
    print(f"Warning: bcrypt not available, using simple hashing: {e}")
    USE_BCRYPT = False
    import hashlib


class MongoDBAuth:
    """MongoDB-based authentication system."""
    
    def __init__(self):
        try:
            self.db = get_database()
            self.users_collection = self.db.users
            self.sessions_collection = self.db.sessions
            
            # Create indexes
            try:
                self.users_collection.create_index("username", unique=True)
                self.sessions_collection.create_index("session_id", unique=True)
                # TTL index for automatic session expiration
                self.sessions_collection.create_index("expires_at", expireAfterSeconds=0)
            except Exception as e:
                print(f"Warning: Could not create indexes: {e}")
            
            # Initialize default users if they don't exist
            self._initialize_default_users()
        except Exception as e:
            print(f"Error initializing MongoDB auth: {e}")
            raise
    
    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        if USE_BCRYPT:
            return pwd_context.hash(password)
        else:
            # Simple SHA256 hashing (not secure, but works)
            return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against a hash."""
        if USE_BCRYPT:
            try:
                return pwd_context.verify(password, hashed)
            except Exception:
                return False
        else:
            # Simple SHA256 verification
            return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    def _initialize_default_users(self):
        """Initialize default admin and student users if they don't exist."""
        default_users = [
            {
                "username": "admin",
                "password": self._hash_password("admin123"),
                "email": "admin@example.com",
                "created_at": datetime.now()
            },
            {
                "username": "student",
                "password": self._hash_password("student123"),
                "email": "student@example.com",
                "created_at": datetime.now()
            }
        ]
        
        for user_data in default_users:
            if not self.users_collection.find_one({"username": user_data["username"]}):
                self.users_collection.insert_one(user_data)
                print(f"Created default user: {user_data['username']}")
    
    def register(self, username: str, password: str, email: str = "") -> Dict:
        """Register a new user."""
        # Check if user exists
        if self.users_collection.find_one({"username": username}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Hash password
        hashed_password = self._hash_password(password)
        
        # Create user document
        user_doc = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "created_at": datetime.now()
        }
        
        # Insert user
        result = self.users_collection.insert_one(user_doc)
        
        return {
            "username": username,
            "email": email,
            "created_at": user_doc["created_at"].isoformat()
        }
    
    def login(self, username: str, password: str) -> Dict:
        """Login and create session."""
        # Find user
        user = self.users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not self._verify_password(password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=30)  # 30 day session
        
        session_doc = {
            "session_id": session_id,
            "username": username,
            "created_at": datetime.now(),
            "expires_at": expires_at
        }
        
        self.sessions_collection.insert_one(session_doc)
        
        return {
            "session_id": session_id,
            "username": username,
            "email": user.get("email", ""),
            "expires_at": expires_at.isoformat()
        }
    
    def get_user_from_session(self, session_id: str) -> Optional[Dict]:
        """Get user from session."""
        session = self.sessions_collection.find_one({"session_id": session_id})
        if not session:
            return None
        
        # Check if session expired
        if datetime.now() > session["expires_at"]:
            self.sessions_collection.delete_one({"session_id": session_id})
            return None
        
        # Get user
        username = session["username"]
        user = self.users_collection.find_one({"username": username})
        if not user:
            return None
        
        # Return user without password
        return {
            "username": user["username"],
            "email": user.get("email", ""),
            "created_at": user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else user["created_at"]
        }
    
    def logout(self, session_id: str) -> bool:
        """Logout and remove session."""
        result = self.sessions_collection.delete_one({"session_id": session_id})
        return result.deleted_count > 0
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        user = self.users_collection.find_one({"username": username})
        if not user:
            return None
        
        return {
            "username": user["username"],
            "email": user.get("email", ""),
            "created_at": user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else user["created_at"]
        }


# Global auth instance
mongodb_auth = MongoDBAuth()

