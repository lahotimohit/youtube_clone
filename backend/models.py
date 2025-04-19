from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import ForeignKey, Column, Enum
from datetime import datetime
from pydantic import EmailStr
import uuid
import pytz
import enum

def kolkata_time():
    return datetime.now(pytz.timezone("Asia/Kolkata")).replace(tzinfo=None)

class VideoVisibility(enum.Enum):
    PRIVATE="PRIVATE"
    PUBLIC="PUBLIC"
    UNLISTED="UNLISTED"

class VideoProcessing(enum.Enum):
    IN_PROGRESS="IN_PROGRESS"
    COMPLETED="COMPLETED"
    FAILED="FAILED"

class Users(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(nullable=False)
    email: EmailStr = Field(nullable=False, unique=True, index=True)
    password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=kolkata_time, nullable=False)

    videos: list["Video"] = Relationship(back_populates="user")

class Video(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    user_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id"), nullable=False)
    )
    video_s3_key: str= Field()
    visibility: VideoVisibility = Field(sa_column=Column(Enum(VideoVisibility), default=VideoVisibility.PRIVATE))
    is_processing: VideoProcessing = Field(sa_column=Column(Enum(VideoProcessing)), default=VideoProcessing.IN_PROGRESS)

    user: Users = Relationship(back_populates="videos")
