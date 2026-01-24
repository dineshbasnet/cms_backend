import uuid
from db import Base
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Table,Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from schemas.user_schemas import Roles,AccountStatusEnum

#user model for cms system
class User(Base):
    __tablename__="users"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    username = Column(String,nullable=False)
    email = Column(String,nullable=False)
    phone = Column(String,nullable=True)
    hash_password = Column(String,nullable=False)
    role = Column(Enum(Roles),default=Roles.user)
    image_url = Column(String)
    status = Column(Enum(AccountStatusEnum), default = AccountStatusEnum.active)
    posts = relationship('Post',back_populates='author')
    comments = relationship('Comment',back_populates='user')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)




#category model for cms system
class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name = Column(String,nullable=False)
    description = Column(String,nullable=True)
    image_url = Column(String,nullable=True)
    posts = relationship('Post',back_populates='category')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
#tags model for cms system
class Tag(Base):
    __tablename__="tags"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name = Column(String,nullable=False)
    description = Column(String,nullable=True)
    posts = relationship('Post',secondary='post_tags',back_populates='tags')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
     

#post model for cms system
class Post(Base):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    title = Column(String,nullable=False)
    description = Column(String,nullable=True)
    content = Column(String,nullable=False)
    image_url = Column(String)
    author_id = Column(UUID(as_uuid=True),ForeignKey('users.id'),nullable=False)
    category_id = Column(UUID(as_uuid=True),ForeignKey('categories.id'),nullable=False)
    author = relationship('User',back_populates='posts')
    category = relationship('Category',back_populates='posts')
    comments = relationship('Comment',back_populates='posts')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = relationship('Tag',secondary='post_tags',back_populates='posts')
    
    
  
class Comment(Base):
    __tablename__="comments"
    id = Column(Integer,primary_key=True)
    post_id = Column(UUID(as_uuid=True),ForeignKey('posts.id'),nullable=False)
    user_id = Column(UUID(as_uuid=True),ForeignKey('users.id'),nullable=False)
    message = Column(String,nullable=False)
    posts = relationship('Post',back_populates='comments')
    user = relationship('User',back_populates='comments')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id',UUID(as_uuid=True),ForeignKey('posts.id'),primary_key=True),
    Column('tag_id',UUID(as_uuid=True),ForeignKey('tags.id'),primary_key = True)
    
)

        