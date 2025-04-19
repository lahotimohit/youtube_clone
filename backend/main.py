from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import auth, upload, video

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(upload.router, prefix="/upload/video")
app.include_router(video.router, prefix="/videos")

@app.get("/")
def root():
    return "Ram Ram"