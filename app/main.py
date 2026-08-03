"""FastAPI application entry point."""

from ast import List

from app.models import SystemReport
from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session


from app.database import engine,Base,get_db
from app import crud,models,schemas,collector, schemas

Base.metadata.create_all(bind=engine)

app=FastAPI(
    title="System Reporter API",
    description="API de monitoring du systeme et des processus",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "message": "System Reporter API",
        "endpoints": ["/save","/history","/metrics"],
    
    }

@app.get("/health")
def health():
    """Endpoint de santé de l'API."""
    return {"status": "ok","database":"connected"}


@app.get("/metrics")

def metrics():
    """Metriques du systeme et des processus."""
    return collector.get_system_info()


@app.post("/save",response_model=schemas.ScanResponse)
def save_scan(db:Session= Depends(get_db)):
    """Scan system and save it in PostgresSQL database."""
    data=collector.get_system_info()
    top=collector.get_top_process()

    scan_data=schemas.ScanCreate(
        cpu_percent=data["cpu"]["usage_percent"],
        memory_percent=data["memory"]["usage_percent"],
        disk_percent=data["disk"]["usage_percent"],
        top_process=top,
    )   
    return crud.create_scan(db=db,scan=scan_data)

@app.get("/history",response_model=list[schemas.ScanResponse])
def history(skip:int=0,limit:int=100,db:Session=Depends(get_db)):
    """Get history of scans from database."""
    return crud.get_scan(db=db,skip=skip,limit=limit)