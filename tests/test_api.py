from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_save_and_history():
    # Sauvegarde un scan
    save_resp = client.post("/save")
    assert save_resp.status_code == 200
    data = save_resp.json()
    assert "id" in data
    assert "top_process" in data

    # Vérifie l'historique
    hist_resp = client.get("/history")
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert len(history) > 0
    assert history[0]["id"] == data["id"]