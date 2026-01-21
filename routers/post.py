from db import get_db
from schemas.posts_schemas import PostCreate,PostResponse,PostUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,HTTPException,status
from crud.post import create_post,get_all_posts,get_post

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.post("/",response_model=PostResponse)
async def create_new_post(post:PostCreate,db:AsyncSession = Depends(get_db)):
    try:
        new_post = await create_post(db,post)
        return new_post
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"errors occurs {e}")
    
    

@router.get("/",response_model=list[PostResponse])
async def get_all_posts_route(db:AsyncSession = Depends(get_db)):
    return await get_all_posts(db)



@router.get("/{post_id}",response_model=PostResponse)
async def get_single_post(post_id:int,db:AsyncSession = Depends(get_db)):
    return await get_post(db,post_id)