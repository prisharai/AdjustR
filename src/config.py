from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "AdjustR"
    debug: bool = True

    # Database
    database_url: str = "postgresql://adjustr:adjustr@postgres:5432/adjustr"

    # AWS S3
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "adjustr-uploads-dev"

    # File Upload
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: list = [".mp4", ".mov", ".jpg", ".jpeg", ".png"]

    # ML Model
    locate_anything_model: str = "nvidia/LocateAnything-3B"
    keyframe_interval: float = 2.0

    class Config:
        env_file = ".env"


settings = Settings()
