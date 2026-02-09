import pytest
from unittest.mock import patch, AsyncMock
from tests.integration.test_session_api import create_session_with_user


@pytest.mark.asyncio
class TestListTemplates:
    async def test_returns_12(self, client):
        resp = await client.get("/api/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 12

    async def test_no_auth_required(self, client):
        resp = await client.get("/api/templates")
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestGetTemplate:
    async def test_existing(self, client):
        resp = await client.get("/api/templates/fighter")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "fighter"
        assert data["name"] == "Fighter"
        assert "starting_items" in data
        assert "recommended_hp" in data

    async def test_recommended_ac(self, client):
        resp = await client.get("/api/templates/fighter")
        data = resp.json()
        assert "recommended_ac" in data
        assert data["recommended_ac"] == 16

    async def test_nonexistent(self, client):
        resp = await client.get("/api/templates/nonexistent")
        assert resp.status_code == 404

    async def test_wizard_has_spells(self, client):
        resp = await client.get("/api/templates/wizard")
        data = resp.json()
        assert len(data["starting_spells"]) > 0

    async def test_fighter_has_no_spells(self, client):
        resp = await client.get("/api/templates/fighter")
        data = resp.json()
        assert len(data["starting_spells"]) == 0


@pytest.mark.asyncio
class TestCreateFromTemplate:
    async def test_create_fighter(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/templates/create", json={
                "template_id": "fighter",
                "name": "Sir Lancelot",
                "level": 1,
                "include_items": True,
                "include_spells": True,
            }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Sir Lancelot"
        assert data["class_name"] == "Fighter"
        assert data["max_hp"] == 12  # d10 + con_mod(14)=2

    async def test_hp_calculation_level5(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/templates/create", json={
                "template_id": "fighter",
                "name": "Veteran",
                "level": 5,
            }, headers=headers)
        data = resp.json()
        # d10, con=14→mod=2; hp = 10+2 + 4*(6+2) = 44
        assert data["max_hp"] == 44
        assert data["current_hp"] == 44

    async def test_nonexistent_template(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/templates/create", json={
                "template_id": "nonexistent",
                "name": "Nobody",
            }, headers=headers)
        assert resp.status_code == 404
