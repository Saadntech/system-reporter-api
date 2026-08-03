"""Operations CRUD for application"""
from sqlalchemy.orm import Session
from . import models,schemas

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
