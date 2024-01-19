from app.db import get_session
from app.db.actions import create_user, get_user_by_name
from app.exceptions import InvalidPermissions, InvalidUserName, UsernameAlreadyTaken
from app.models.user import UserCreate, UserResponse
from app.security import manager
from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/user")


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db=Depends(get_session)) -> UserResponse:
    """
    Registers a new user
    """
    try:
        user = create_user(user.username, user.password, db)
        return UserResponse.from_orm(user)
    except IntegrityError:
        raise UsernameAlreadyTaken


@router.get("/{username}")
def read_user(
    username, active_user=Depends(manager), db=Depends(get_session)
) -> UserResponse:
    """
    Shows information about the user
    """
    user = get_user_by_name(username, db)

    if user is None:
        raise InvalidUserName

    # Only allow admins and oneself to access this information
    if user.username != active_user.username and not active_user.is_admin:
        raise InvalidPermissions

    return UserResponse.from_orm(user)
