"""FastAPI application entry point."""

from ast import List

from app.models import SystemReport
from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session

from app.metrics_export import (
    update_metrics, 
    increment_scan_counter, 
    get_prometheus_metrics,
    CONTENT_TYPE_LATEST
)
from app.database import engine,Base,get_db
from app import crud,models,schemas,collector, schemas
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.exporter import export_history_csv
from app.collector import get_processes_list
from app.auth import authenticate, create_access_token, require_user
Base.metadata.create_all(bind=engine)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI(
    title="System Reporter API",
    description="API de monitoring du systeme et des processus",
    version="1.0.0",
)
# AJOUTE APRÈS app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, mets ton vrai domaine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.post("/auth/token")
def login(credentials: schemas.LoginRequest):
    if not authenticate(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "access_token": create_access_token(credentials.username),
        "token_type": "bearer",
    }

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
def metrics_prometheus():
    """Endpoint pour Prometheus (format OpenMetrics)."""
    update_metrics()
    from fastapi import Response
    return Response(
        content=get_prometheus_metrics(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/current")
def current_metrics():
    """Return current system metrics as JSON for the web dashboard."""
    data = collector.get_system_info()
    return {
        "timestamp": data["timestamp"],
        "cpu": data["cpu"],
        "memory": data["memory"],
        "disk": data["disk"],
        "top_process": collector.get_top_process(),
    }


@app.post("/save", response_model=schemas.ScanResponse)
def save_scan(db: Session = Depends(get_db), _: str = Depends(require_user)):
    data = collector.get_system_info()
    top = collector.get_top_process()
    
    scan_data = schemas.ScanCreate(
        cpu_percent=data["cpu"]["usage_percent"],
        memory_percent=data["memory"]["usage_percent"],
        disk_percent=data["disk"]["usage_percent"],
        top_process=top,
    )
    
    # INCRÉMENTE LE COMPTEUR PROMETHEUS
    increment_scan_counter()
    
    return crud.create_scan(db=db, scan=scan_data)

@app.get("/history",response_model=list[schemas.ScanResponse])
def history(skip:int=0,limit:int=100,db:Session=Depends(get_db)):
    """Get history of scans from database."""
    return crud.get_scan(db=db,skip=skip,limit=limit)
@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    """Statistiques agrégées sur tous les scans."""
    return crud.get_stats(db)


@app.get("/export/csv", response_class=PlainTextResponse)
def export_csv(db: Session = Depends(get_db)):
    """Télécharge l'historique en CSV."""
    csv_data = export_history_csv(db)
    return PlainTextResponse(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=history.csv"}
    )


@app.get("/alerts")
def alerts(
    cpu_threshold: float = Query(80.0, description="Seuil CPU en %"),
    ram_threshold: float = Query(80.0, description="Seuil RAM en %"),
    db: Session = Depends(get_db)
):
    """Vérifie si les dernières métriques dépassent les seuils."""
    latest = crud.get_latest_scan(db)
    if not latest:
        return {"status": "no_data", "alerts": []}
    
    alerts_list = []
    
    if latest.cpu_percent > cpu_threshold:
        alerts_list.append({
            "type": "cpu",
            "level": "warning" if latest.cpu_percent < 95 else "critical",
            "message": f"CPU à {latest.cpu_percent}% (seuil: {cpu_threshold}%)",
            "value": latest.cpu_percent,
        })
    
    if latest.memory_percent > ram_threshold:
        alerts_list.append({
            "type": "memory",
            "level": "warning" if latest.memory_percent < 95 else "critical",
            "message": f"RAM à {latest.memory_percent}% (seuil: {ram_threshold}%)",
            "value": latest.memory_percent,
        })
    
    return {
        "status": "critical" if any(a["level"] == "critical" for a in alerts_list) else 
                  "warning" if alerts_list else "ok",
        "alerts": alerts_list,
        "latest_scan": {
            "id": latest.id,
            "cpu": latest.cpu_percent,
            "ram": latest.memory_percent,
            "disk": latest.disk_percent,
            "timestamp": latest.timestamp,
        }
    }


@app.get("/processes")
def processes(n: int = Query(10, ge=1, le=50)):
    """Liste les processus les plus gourmands (CPU + RAM)."""
    return {
        "count": n,
        "processes": get_processes_list(n)
    }


@app.delete("/history/{scan_id}")
def delete_scan(scan_id: int, db: Session = Depends(get_db), _: str = Depends(require_user)):
    """Supprime un scan spécifique."""
    deleted = crud.delete_scan(db, scan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"message": f"Scan {scan_id} supprimé"}


@app.get("/reports/summary")
def summary(db: Session = Depends(get_db)):
    """Génère un rapport textuel auto."""
    stats = crud.get_stats(db)
    latest = crud.get_latest_scan(db)
    
    if not latest:
        return {"report": "Aucune donnée disponible."}
    
    report = f"""
╔══════════════════════════════════════╗
║     SYSTEM REPORTER - RAPPORT      ║
╠══════════════════════════════════════╣
  Date: {latest.timestamp.strftime('%Y-%m-%d %H:%M') if latest.timestamp else 'N/A'}
  
  📊 MÉTRIQUES ACTUELLES
  ├── CPU:  {latest.cpu_percent}%
  ├── RAM:  {latest.memory_percent}%
  └── Disk: {latest.disk_percent}%
  
  📈 STATISTIQUES GLOBALES
  ├── Scans totaux: {stats['total_scans']}
  ├── CPU moyen:    {stats['cpu']['average']}%
  ├── CPU max:      {stats['cpu']['max']}%
  └── RAM moyenne:  {stats['memory']['average']}%
  
  🔥 Top Process: {latest.top_process}
  
  Statut: {'⚠️ ALERTE' if latest.cpu_percent > 80 or latest.memory_percent > 80 else '✅ OK'}
╚══════════════════════════════════════╝
"""
    return {"report": report.strip()}