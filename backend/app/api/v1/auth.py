from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new student user and return JWT tokens."""
    service = AuthService(db)
    return await service.register(user_in)


@router.post("/login", response_model=Token)
async def login(login_in: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate student user using email & password."""
    service = AuthService(db)
    return await service.login(login_in)


@router.post("/refresh", response_model=Token)
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    service = AuthService(db)
    return await service.refresh_tokens(req.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get the currently logged-in user profile details."""
    return UserResponse.model_validate(current_user)


@router.get("/github/url")
async def get_github_oauth_url():
    """Returns the GitHub OAuth login URL."""
    if not settings.GITHUB_CLIENT_ID:
        return {
            "enabled": False,
            "message": "GitHub OAuth is not configured in environment variables. Use email/password for local dev."
        }
    redirect_uri = settings.GITHUB_REDIRECT_URI or "http://localhost:3000/auth/callback"
    url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&scope=user:email,read:user&redirect_uri={redirect_uri}"
    return {"enabled": True, "url": url}
