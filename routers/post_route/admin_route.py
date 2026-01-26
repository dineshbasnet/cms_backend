from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from models.models import User
from schemas.user_schemas import Roles
from schemas.posts_schemas import PostResponse, PostStatusUpdate
from crud.post import get_all_posts,get_post
from utils.auth import get_current_active_user
from uuid import UUID


router = APIRouter(
    prefix="/posts",
    tags=["admin-posts"]
)

#Admin routes
@router.get("/admin",response_model=list[PostResponse])
async def get_all_posts_route(
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    
    return await get_all_posts(db,current_user)

@router.get("/admin/{post_id}",response_model=PostResponse)
async def get_single_post(post_id:UUID,db:AsyncSession = Depends(get_db)):
    return await get_post(db,post_id)

#post status verification route
@router.patch("/admin/{post_id}/status",response_model=PostResponse)
async def update_post_status(
    post_id:UUID,
    status_update:PostStatusUpdate,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
    
):
    post = await get_post(db,post_id)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    if current_user.role != Roles.admin:
        raise HTTPException(
            status_code=403,
            detail="Only admins can update post status"
        )
        
    post.status = status_update.status
    
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    return post