from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sync_create():
    response = client.post("/v1/sync/", json={
        "operation": "create",
        "record_id": "abc123",
        "data": {"name": "John"},
        "crm": "salesforce"
    })
    assert response.status_code == 202

def test_override_config():
    response = client.post("/v1/sync/config-override", json={
        "crm": "salesforce",
        "batch_size": 100,
        "flush_interval": 30,
        "rate_limit_per_minute": 600
    })
    assert response.status_code == 200
