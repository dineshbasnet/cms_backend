from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token:str
    token_type:str = "bearer"


class LoginRequest(BaseModel):
    email:str
    password:str
    
class TokenData(BaseModel):
    email:Optional[str] = None
    
    