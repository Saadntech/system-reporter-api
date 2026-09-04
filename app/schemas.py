"""Shema pydantic for API"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScanCreate(BaseModel):
    """Schema for creating a new scan."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    top_process: str


class ScanResponse(ScanCreate):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str
