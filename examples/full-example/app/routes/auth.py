from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy.orm import Session

from app.db import get_session
from app.db.actions import get_user_by_name
from app.models.auth import Token
from app.security import verify_password, manager

router = APIRouter(
    prefix="/auth"
)


@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm, db: Session = Depends(get_session)) -> Token:
    """
    Logs in the user provided by form_data.username and form_data.password
    """
    user = get_user_by_name(form_data.username)
    if user is None:
        raise InvalidCredentialsException

    if not verify_password(form_data.password, user.password):
        raise InvalidCredentialsException

    token = manager.create_access_token(data={'sub': user.username})
    return {'token': f"Bearer {token}"}
