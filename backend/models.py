from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from pydantic import EmailStr
import uuid
import pytz

def kolkata_time():
    return datetime.now(pytz.timezone("Asia/Kolkata")).replace(tzinfo=None)

class Users(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(nullable=False)
    email: EmailStr = Field(nullable=False, unique=True, index=True)
    password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=kolkata_time, nullable=False)