"""Recuper les metrique du systeme et les informations sur les processus."""

import psutil
import platform
from datetime import datetime
from typing import List, Dict,Any 


def get_system_info() -> Dict[str, Any]:
    """Recuper information """
    return{
        "timestamp": datetime.now().isoformat(),
        "platform":{
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor()
        },
        "cpu":{
            "cores_physical": psutil.cpu_count(logical=False) or 0 ,
            "cores_logical": psutil.cpu_count(logical=True)or 0,
            "usage_percent": psutil.cpu_percent(interval=1)

        },
        "memory":{
            "total_gb": round(psutil.virtual_memory().total / (1024 **3), 2),
            "available_gb": round(psutil.virtual_memory().available / (1024 **3), 2),
            "usage_percent": psutil.virtual_memory().percent

        },
        "disk":{
            "total_gb": round(psutil.disk_usage('/').total / (1024 **3), 2),
            "used_gb": round(psutil.disk_usage('/').used / (1024 **3), 2),
            "free_gb": round(psutil.disk_usage('/').free / (1024 **3), 2),
            "usage_percent": psutil.disk_usage('/').percent

        },

    }
def get_top_processes(n: int = 5) -> List[Dict[str, Any]]:
    """Retourne les N processus les plus gourmands en CPU."""
    import time
    
    # ÉTAPE 1 : Initialiser le compteur CPU sur tous les processus
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(interval=None)  # Premier appel = initialisation
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # ÉTAPE 2 : Attendre que le système calcule (0.5 seconde)
    time.sleep(0.5)
    
    # ÉTAPE 3 : Relire les vraies valeurs
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            cpu = proc.cpu_percent(interval=None)  # Deuxième appel = vraie valeur
            if cpu > 0:
                processes.append({
                    "pid": proc.pid,
                    "name": proc.name(),
                    "cpu_percent": round(cpu, 2),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return processes[:n]