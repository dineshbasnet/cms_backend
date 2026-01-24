from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import user,post,category,auth
from config import settings
from fastapi.middleware.cors import CORSMiddleware


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

app.include_router(user.router)
app.include_router(post.router)
app.include_router(category.router)
app.include_router(auth.router)
