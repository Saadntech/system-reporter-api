"""Expose les métriques au format Prometheus."""

from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import psutil

# Métriques système (Gauges = valeurs qui changent)
CPU_GAUGE = Gauge('system_cpu_percent', 'Pourcentage CPU utilisé')
RAM_GAUGE = Gauge('system_memory_percent', 'Pourcentage RAM utilisée')
DISK_GAUGE = Gauge('system_disk_percent', 'Pourcentage Disk utilisé')

# Compteur de scans (Counter = valeur qui augmente)
SCANS_COUNTER = Counter('system_scans_total', 'Nombre total de scans effectués')


def update_metrics():
    """Met à jour les gauges avec les valeurs actuelles."""
    CPU_GAUGE.set(psutil.cpu_percent(interval=1))
    RAM_GAUGE.set(psutil.virtual_memory().percent)
    DISK_GAUGE.set(psutil.disk_usage('/').percent)


def increment_scan_counter():
    """Incrémente le compteur quand on sauvegarde un scan."""
    SCANS_COUNTER.inc()


def get_prometheus_metrics():
    """Génère le texte au format Prometheus."""
    return generate_latest()