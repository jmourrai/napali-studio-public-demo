import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(db_path=str(tmp_path / "api.sqlite"), seed=False)) as c:
        yield c


def test_health_and_readiness(client):
    assert client.get("/healthz").json()["status"] == "ok"
    assert client.get("/readyz").json()["status"] == "ready"


def test_create_list_and_metrics(client):
    created = client.post("/api/work-items", json={"title": "  Synthetic story  ",
                                                    "priority": "medium"})
    assert created.status_code == 201
    assert created.json()["title"] == "Synthetic story"
    assert len(client.get("/api/work-items").json()) == 1
    assert client.get("/api/metrics").json()["total"] == 1


def test_bad_input_rejected(client):
    assert client.post("/api/work-items", json={"title": "   "}).status_code == 422
    assert client.post("/api/work-items", json={"title": "Valid title",
                                                       "priority": "urgent"}).status_code == 422


def test_transition_audit_conflict_and_not_found(client):
    item = client.post("/api/work-items", json={"title": "Synthetic story"}).json()
    path = f"/api/work-items/{item['id']}"
    result = client.post(path + "/transition", json={"to_status": "review",
                                                     "expected_version": 1, "note": "Review"})
    assert result.status_code == 200
    assert result.json()["version"] == 2
    assert client.post(path + "/transition", json={"to_status": "published",
                                                     "expected_version": 2}).status_code == 409
    assert client.post(path + "/transition", json={"to_status": "in_progress",
                                                     "expected_version": 1}).status_code == 409
    assert len(client.get(path + "/events").json()) == 2
    assert client.get("/api/work-items/not-here").status_code == 404


def test_workflow_contract(client):
    data = client.get("/api/workflow").json()["allowed_transitions"]
    assert data["intake"] == ["review"]
    assert data["published"] == []


def test_serves_local_frontend(client):
    assert "synthetic records" in client.get("/").text
    assert client.get("/static/app.js").status_code == 200
