from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"

    # Email Configuration
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    sender_email: str
    sender_name: str = "Pixaro AI Agent"

    # AI Service API Keys
    openai_api_key: Optional[str] = None
    replicate_api_key: Optional[str] = None
    stability_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None  # For Gemini (not Veo 3)
    runway_api_key: Optional[str] = None  # For Runway ML Gen-3 video

    # Video Generation Settings
    use_runway: bool = True  # Use Runway ML for professional videos
    video_fallback: bool = True  # Fallback if video generation fails

    # Storage Configuration
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    max_file_size: int = 10485760  # 10MB

    # Processing Configuration
    video_duration: int = 10
    video_fps: int = 30
    image_max_size: int = 2048

    # Twitter/X OAuth Configuration
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_client_id: Optional[str] = None
    twitter_client_secret: Optional[str] = None
    twitter_redirect_uri: str = "http://localhost:8000/api/auth/twitter/callback"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create directories if they don't exist
def ensure_directories():
    """Ensure upload and output directories exist"""
    settings = Settings()
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    os.makedirs(f"{settings.output_dir}/images", exist_ok=True)
    os.makedirs(f"{settings.output_dir}/videos", exist_ok=True)


settings = Settings()
