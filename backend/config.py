from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    aws_region_name: str
    aws_raw_videos_bucket: str
    aws_thumbnail_bucket: str

    class Config:
        env_file=".env"

settings=Settings()