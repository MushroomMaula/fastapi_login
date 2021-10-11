from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError

from app.db import get_session
from app.exceptions import InvalidPermissions, UsernameAlreadyTaken
from app.models.user import UserCreate, UserReponse
from app.db.actions import create_user, get_user_by_name
from app.security import manager


router = APIRouter(
    prefix="/user"
)


@router.post('/register', response_model=UserReponse, status_code=201)
def register(user: UserCreate, db=Depends(get_session)) -> UserReponse:
    """
    Registers a new user
    """
    try:
        user = create_user(user.username, user.password, db)
        return user
    except IntegrityError:
        raise UsernameAlreadyTaken


@router.get('/{username}')
def read_user(username, active_user=Depends(manager), db=Depends(get_session)) -> UserReponse:
    """
    Shows information about the user
    """
    user = get_user_by_name(username, db)
    # Only allow admins and oneself to access this information
    if user.username != active_user.username and not active_user.is_admin:
        raise InvalidPermissions
    
    return user
    