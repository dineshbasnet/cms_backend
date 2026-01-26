from db import get_db
from schemas.posts_schemas import PostCreate,PostResponse,PostUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,HTTPException,status
from crud.post import create_post,get_post,update_post,delete_post
from models.models import User
from uuid import UUID
from schemas.user_schemas import Roles
from utils.auth import get_current_active_user

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


#Post management routes (common for admin and author)
@router.post("/",response_model=PostResponse)
async def create_new_post(post:PostCreate,db:AsyncSession = Depends(get_db),current_user:User = Depends(get_current_active_user)):
    if current_user.role not in [Roles.admin,Roles.author]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
        
    try:
        new_post = await create_post(db,current_user,post)
        return new_post
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"errors occurs {e}")
    

@router.patch("/{post_id}",response_model=PostResponse)
async def update_posts(
    post_id:UUID,
    post_data:PostUpdate,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
 
    updated_post = await update_post(db,post_id,current_user,post_data)

    return updated_post


@router.delete("/{post_id}",response_model=PostResponse)
async def delete_post_route(
    post_id:UUID,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    """Only admins or authors can delete"""
    deleted_post =await delete_post(db,post_id,current_user)
    
    return deleted_post
