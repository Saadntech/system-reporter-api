"""Tests de l'API avec pytest."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "System Reporter API"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    
    data = response.json()
    
    # Vérifie que toutes les clés sont présentes
    assert "timestamp" in data
    assert "platform" in data
    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data
    assert "top_processes" in data
    
    # Vérifie les types
    assert isinstance(data["top_processes"], list)
    assert len(data["top_processes"]) <= 5
    
    # Vérifie CPU
    assert 0 <= data["cpu"]["usage_percent"] <= 100