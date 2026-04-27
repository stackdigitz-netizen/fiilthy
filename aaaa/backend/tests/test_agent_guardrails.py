from fastapi import FastAPI
from fastapi.testclient import TestClient

from ai_services.auth_utils import require_auth
from core.routes_agents import router


class DummyOrchestrator:
    async def get_metrics(self):
        return {"active_divisions": 6}

    async def approve_campaign(self, campaign_id: str):
        return {"success": True, "campaign_id": campaign_id, "status": "active"}


def build_client():
    app = FastAPI()
    app.include_router(router)
    return app


def test_agents_metrics_requires_auth():
    client = TestClient(build_client())
    response = client.get("/api/agents/metrics")
    assert response.status_code == 401


def test_approve_requires_operator_access(monkeypatch):
    app = build_client()
    app.dependency_overrides[require_auth] = lambda: {"sub": "user-1", "email": "user@example.com"}
    monkeypatch.setattr("core.routes_agents._orch", lambda: DummyOrchestrator())

    client = TestClient(app)
    response = client.post("/api/agents/approvals/campaign-1/approve")
    assert response.status_code == 403


def test_approve_allows_admin(monkeypatch):
    app = build_client()
    app.dependency_overrides[require_auth] = lambda: {"sub": "admin-1", "email": "owner@example.com", "is_admin": True}
    monkeypatch.setattr("core.routes_agents._orch", lambda: DummyOrchestrator())

    client = TestClient(app)
    response = client.post("/api/agents/approvals/campaign-1/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "active"