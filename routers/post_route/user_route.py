from crud.post import get_all_published_posts, get_single_published_post
from fastapi import HTTPException,status, Depends, APIRouter
from schemas.posts_schemas import PostResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from models.models import User
from db import get_db
from uuid import UUID
from utils.auth import get_current_active_user


router = APIRouter(
    prefix="/posts",
    tags=["user-posts"]
)


@router.get("/user",response_model=List[PostResponse])
async def get_all_author_posts_route(
    db:AsyncSession = Depends(get_db)
):
    
    posts = await get_all_published_posts(db)
    
    return posts


@router.get("/user/{post_id}",response_model=PostResponse)
async def get_single_author_post_route(
    post_id:UUID,
    db:AsyncSession = Depends(get_db)
):

    post = await get_single_published_post(db,post_id)
    
    return post

