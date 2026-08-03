"""Model donnes pour l'application."""

from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel #pydantic pour la validation des données
from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base

class PlateformInfo(BaseModel):
    """Classe représentant une plateforme."""
    system: str
    release: str
    machine: str
    processor: str

class CpuInfo(BaseModel):
    """Classe représentant les informations du CPU."""
    cores_physical: int
    cores_logical: int
    usage_percent: float

class DiskInfo(BaseModel):
    """Classe représentant les informations du disque."""
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float


class MemoryInfo(BaseModel):
    total_gb: float
    available_gb: float
    usage_percent: float


class ProcessInfo(BaseModel):
    """Classe représentant les informations d'un processus."""
    pid: int
    name: str
    cpu_percent: float

class SystemReport(BaseModel):
    """Classe représentant un rapport complet du système."""
    timestamp: str
    platform: PlateformInfo
    cpu: CpuInfo
    memory: MemoryInfo
    disk: DiskInfo
    top_processes: List[ProcessInfo]

class Systemscan(Base):
    """Classe représentant un scan du système."""
    __tablename__ = "system_scan"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)
    top_process = Column(String)