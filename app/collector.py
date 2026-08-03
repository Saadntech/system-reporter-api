"""Collecte des métriques."""

import psutil
import platform
import time
from datetime import datetime


def get_system_info():
    return {
        "timestamp": datetime.now().isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
        },
        "cpu": {
            "usage_percent": psutil.cpu_percent(interval=1),
        },
        "memory": {
            "usage_percent": psutil.virtual_memory().percent,
        },
        "disk": {
            "usage_percent": psutil.disk_usage('/').percent,
        },
    }


def get_top_process():
    """Retourne le processus le plus gourmand en CPU."""
    # ÉTAPE 1 : Initialiser le compteur
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # ÉTAPE 2 : Attendre 0.5 seconde (plus sûr que 0.2)
    time.sleep(0.5)
    
    # ÉTAPE 3 : Relire les vraies valeurs
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            cpu = proc.cpu_percent(interval=None)
            if cpu > 0:
                processes.append({
                    "name": proc.name(),
                    "cpu": cpu,
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not processes:
        return "unknown"
    
    processes.sort(key=lambda x: x['cpu'], reverse=True)
    return processes[0]["name"]