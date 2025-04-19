from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UploadMetaData(BaseModel):
    title: str
    desciption: str
    video_id: str
    video_s3_key: str
    visibility: str