"""Operations CRUD for application"""
from sqlalchemy.orm import Session
from . import models,schemas
from sqlalchemy import func
#create a new scan in the database
def create_scan(db:Session, scan:schemas.ScanCreate):
    db_scan=models.Systemscan(**scan.model_dump())
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan

#Scan system data from database
def get_scan(db:Session, skip:int=0, limit:int=100):
    return db.query(models.Systemscan).order_by(models.Systemscan.timestamp.desc()).offset(skip).limit(limit).all()

#latest scan from database
def get_latest_scan(db:Session):
    return db.query(models.Systemscan).order_by(models.Systemscan.timestamp.desc()).first()

def get_stats(db: Session):
    """Calcule les statistiques sur tous les scans."""
    result = db.query(
        func.avg(models.SystemScan.cpu_percent).label("avg_cpu"),
        func.max(models.SystemScan.cpu_percent).label("max_cpu"),
        func.min(models.SystemScan.cpu_percent).label("min_cpu"),
        func.avg(models.SystemScan.memory_percent).label("avg_ram"),
        func.max(models.SystemScan.memory_percent).label("max_ram"),
        func.count(models.SystemScan.id).label("total_scans"),
    ).first()
    
    return {
        "cpu": {
            "average": round(result.avg_cpu or 0, 2),
            "max": round(result.max_cpu or 0, 2),
            "min": round(result.min_cpu or 0, 2),
        },
        "memory": {
            "average": round(result.avg_ram or 0, 2),
            "max": round(result.max_ram or 0, 2),
        },
        "total_scans": result.total_scans or 0,
    }


def delete_scan(db: Session, scan_id: int):
    """Supprime un scan par ID."""
    scan = db.query(models.SystemScan).filter(models.SystemScan.id == scan_id).first()
    if scan:
        db.delete(scan)
        db.commit()
        return True
    return False


def get_scan_by_id(db: Session, scan_id: int):
    """Récupère un scan spécifique."""
    return db.query(models.SystemScan).filter(models.SystemScan.id == scan_id).first()