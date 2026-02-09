import pytest
from unittest.mock import patch, AsyncMock
from tests.integration.test_session_api import create_session_with_user


@pytest.mark.asyncio
class TestDiceRoll:
    async def test_normal_roll(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/dice/roll", json={
                "dice": "2d6+3",
                "reason": "Attack",
                "roll_type": "normal",
            }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["dice"] == "2d6+3"
        assert len(data["rolls"]) == 2
        assert data["modifier"] == 3
        assert data["all_rolls"] is None

    async def test_advantage_roll(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/dice/roll", json={
                "dice": "1d20",
                "roll_type": "advantage",
            }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["roll_type"] == "advantage"
        assert data["all_rolls"] is not None
        assert len(data["all_rolls"]) == 2

    async def test_disadvantage_roll(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/dice/roll", json={
                "dice": "1d20",
                "roll_type": "disadvantage",
            }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["roll_type"] == "disadvantage"

    async def test_invalid_notation(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/dice/roll", json={
                "dice": "invalid",
            }, headers=headers)
        assert resp.status_code == 400

    async def test_requires_auth(self, client):
        resp = await client.post("/api/dice/roll", json={"dice": "1d20"})
        assert resp.status_code in (401, 403)
