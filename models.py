from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class JobStatus(str, Enum):
    """Status of processing job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProductUploadRequest(BaseModel):
    """Request model for product upload"""
    product_name: str
    product_description: str
    email: EmailStr


class ProductUploadResponse(BaseModel):
    """Response model for product upload"""
    job_id: str
    status: JobStatus
    message: str


class JobStatusResponse(BaseModel):
    """Response model for job status check"""
    job_id: str
    status: JobStatus
    message: Optional[str] = None
    enhanced_image_url: Optional[str] = None
    video_url: Optional[str] = None
    email_sent: bool = False
