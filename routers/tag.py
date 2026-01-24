from crud.tag import create_tags
from fastapi import APIRouter,HTTPException,status,Depends
from schemas.tag_schemas import TagCreate,TagResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from utils.auth import get_current_user


router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)

@router.post("/",response_model=TagResponse)
async def create_new_category(tag:TagCreate,db:AsyncSession = Depends(get_db),user = Depends(get_current_user)):
    try:
        new_tag = await create_tags(db,tag)
        return new_tag
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"error occured:{e}")