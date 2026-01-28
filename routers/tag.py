from crud.tag import create_tags,get_all_tags,get_single_tag,delete_tags
from fastapi import APIRouter,HTTPException,status,Depends,Path
from schemas.tag_schemas import TagCreate,TagResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from schemas.user_schemas import Roles
from typing import List
from uuid import UUID
from utils.auth import get_current_active_user


router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)

@router.post("/",response_model=TagResponse)
async def create_new_tag(tag:TagCreate,db:AsyncSession = Depends(get_db),current_user = Depends(get_current_active_user)):
    try:
        new_tag = await create_tags(db,tag,current_user)
        return new_tag
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"error occured:{e}")
    
    
@router.get("/",response_model=List[TagResponse])
async def get_all_tags_route(
    db:AsyncSession = Depends(get_db)):
    
    return await get_all_tags(db)


@router.get("/{tag_id}",response_model=TagResponse)
async def get_single_tag_route(
    tag_id:UUID,
    db:AsyncSession = Depends(get_db)
    
):
    tag = await get_single_tag(db,tag_id)
    
    return tag


@router.delete("/{tag_id}",status_code=status.HTTP_200_OK)
async def delete_tag_route(
    tag_id:UUID = Path(...,title="Id of the tag to delete"),
    db:AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
    
):
    if current_user.role != Roles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete tags"
        )

    return await delete_tags(db, tag_id)