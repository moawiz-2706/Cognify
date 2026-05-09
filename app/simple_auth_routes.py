"""Authentication routes with MongoDB support."""

from fastapi import APIRouter, HTTPException, status, Cookie
from typing import Optional
from pydantic import BaseModel

# Try to use MongoDB auth, fallback to simple auth
try:
    from app.mongodb_auth import mongodb_auth
    auth = mongodb_auth
    print("Using MongoDB authentication")
except Exception as e:
    print(f"MongoDB not available, using in-memory auth: {e}")
    from app.simple_auth import simple_auth
    auth = simple_auth

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """Register request model."""
    username: str
    password: str
    email: str = ""


@router.post("/register")
async def register(data: RegisterRequest):
    """Register a new user."""
    try:
        # Validate input
        if not data.username or len(data.username.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is required"
            )
        if not data.password or len(data.password) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 3 characters"
            )
        
        user = auth.register(data.username.strip(), data.password, data.email.strip() if data.email else "")
        return {"message": "User registered successfully", "user": user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
async def login(data: LoginRequest):
    """Login and get session."""
    try:
        result = auth.login(data.username, data.password)
        
        # Create response with session cookie
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=result)
        response.set_cookie(
            key="session_id",
            value=result["session_id"],
            max_age=30 * 24 * 60 * 60,  # 30 days
            httponly=True,
            samesite="lax",
            path="/"
        )
        return response
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout")
async def logout(session_id: Optional[str] = Cookie(None)):
    """Logout and remove session."""
    from fastapi.responses import JSONResponse
    response = JSONResponse(content={"message": "Logged out successfully"})
    
    if session_id:
        auth.logout(session_id)
    
    response.delete_cookie(key="session_id", path="/")
    return response


@router.get("/me")
async def get_current_user(session_id: Optional[str] = Cookie(None)):
    """Get current user from session."""
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = auth.get_user_from_session(session_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return user
