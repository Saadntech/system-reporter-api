"""Model donnes pour l'application."""

from pydantic import BaseModel #pydantic pour la validation des données
from typing import List, Optional #typing pour les types de données

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