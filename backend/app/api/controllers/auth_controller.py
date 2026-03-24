from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.core.database import get_db
from shared.core.logging_config import get_logger
from shared.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    TokenRefreshRequest
)
from shared.schemas.common import DataResponse
from shared.models.user import User
from app.services.auth_service import AuthService, get_auth_service
from app.dependencies.auth import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)


@router.post("/register", response_model=DataResponse[dict], status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.

    Returns user data and authentication tokens.
    """
    try:
        user, tokens = await auth_service.register(
            db=db,
            email=user_data.email,
            password=user_data.password
        )
        return DataResponse(data={
            "user": user.model_dump(),
            "tokens": tokens.model_dump()
        })
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=DataResponse[dict])
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return tokens.
    """
    try:
        user, tokens = await auth_service.login(
            db=db,
            email=credentials.email,
            password=credentials.password
        )
        return DataResponse(data={
            "user": user.model_dump(),
            "tokens": tokens.model_dump()
        })
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=DataResponse[TokenResponse])
async def refresh_token(
    token_request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token.
    """
    try:
        tokens = await auth_service.refresh_access_token(
            db=db,
            refresh_token=token_request.refresh_token
        )
        return DataResponse(data=tokens)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=DataResponse[UserResponse])
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user info.

    Requires valid access token in Authorization header.
    """
    return DataResponse(data=UserResponse.model_validate(current_user))
