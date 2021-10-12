from typing import List
from fastapi import APIRouter
from fastapi.param_functions import Depends
from app.db import get_session
from app.db.actions import create_post, get_user_by_name
from app.exceptions import InvalidUserName

from app.models.posts import PostCreate, PostResponse
from app.security import manager

router = APIRouter(prefix='/posts')


@router.post('/create', response_model=PostResponse)
def create(post: PostCreate, user=Depends(manager), db=Depends(get_session)) -> PostResponse:
    post = create_post(post.text, user, db)
    return PostResponse.from_orm(post)


@router.get('/list')
def list_posts(user=Depends(manager)) -> List[PostResponse]:
    """ Lists all posts of the current user """
    return [PostResponse.from_orm(p) for p in user.posts]


@router.get('/list/{username}')
def list_posts_for_user(username: str, _=Depends(manager), db=Depends(get_session)) -> List[PostResponse]:
    """ Lists all posts of the given user """
    user = get_user_by_name(username, db)

    if user is None:
        raise InvalidUserName

    return [PostResponse.from_orm(p) for p in user.posts]
