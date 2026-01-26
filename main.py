from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import user,post,category,auth,tag
from routers.post_route import author_route,admin_route,user_route
from config import settings
from fastapi.middleware.cors import CORSMiddleware
from db import async_session
from utils.seed import seed_admin


app = FastAPI()

origins = [
    "http://localhost:5173"
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount(
    settings.MEDIA_URL,
    StaticFiles(directory=settings.MEDIA_ROOT),
    name="media"
)

@app.on_event("startup")
async def startup():
    async with async_session() as db:
        await seed_admin(db)

app.include_router(user.router)
app.include_router(post.router)
app.include_router(category.router)
app.include_router(auth.router)
app.include_router(tag.router)
app.include_router(author_route.router)
app.include_router(admin_route.router)
app.include_router(user_route.router)

