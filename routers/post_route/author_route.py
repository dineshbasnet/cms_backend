from crud.post import get_all_author_posts,get_author_single_post
from fastapi import HTTPException,status, Depends, APIRouter
from schemas.posts_schemas import PostResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.user_schemas import Roles
from models.models import User
from db import get_db
from uuid import UUID
from utils.auth import get_current_active_user


router = APIRouter(
    prefix="/posts",
    tags=["author-posts"]
)


@router.get("/author",response_model=List[PostResponse])
async def get_all_author_posts_route(
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    if current_user.role != Roles.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only author can access this post"
        )
    
    posts = await get_all_author_posts(db,current_user)
    
    return posts


@router.get("/author/{post_id}",response_model=PostResponse)
async def get_single_author_post_route(
    post_id:UUID,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    if current_user.role != Roles.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only author can access this post"
        )
    
    post = await get_author_single_post(db,post_id,current_user)
    
    return post

