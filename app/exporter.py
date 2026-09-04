"""Export de données en CSV."""

import csv
import io
from sqlalchemy.orm import Session
from app import crud


def export_history_csv(db: Session):
    """Génère un CSV de l'historique."""
    scans = crud.get_scan(db, limit=1000)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["ID", "Timestamp", "CPU %", "RAM %", "Disk %", "Top Process"])
    
    # Data
    for scan in scans:
        writer.writerow([
            scan.id,
            scan.timestamp.isoformat() if scan.timestamp else "",
            scan.cpu_percent,
            scan.memory_percent,
            scan.disk_percent,
            scan.top_process,
        ])
    
    return output.getvalue()