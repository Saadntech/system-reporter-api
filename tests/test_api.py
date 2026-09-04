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


def test_stats_and_summary():
    client.post("/save")

    stats_resp = client.get("/stats")
    assert stats_resp.status_code == 200
    assert stats_resp.json()["total_scans"] > 0

    summary_resp = client.get("/reports/summary")
    assert summary_resp.status_code == 200
    assert "report" in summary_resp.json()


def test_export_and_delete():
    save_resp = client.post("/save")
    scan_id = save_resp.json()["id"]

    export_resp = client.get("/export/csv")
    assert export_resp.status_code == 200
    assert "ID,Timestamp,CPU %,RAM %,Disk %,Top Process" in export_resp.text

    delete_resp = client.delete(f"/history/{scan_id}")
    assert delete_resp.status_code == 200