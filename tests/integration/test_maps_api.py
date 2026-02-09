import pytest
from unittest.mock import patch, AsyncMock
from tests.integration.test_session_api import register_user, create_session_with_user


async def _setup_map_session(client):
    """Create session with GM, join player, create a map."""
    resp, _, _ = await create_session_with_user(client)
    session_data = resp.json()
    gm_h = {"Authorization": f"Bearer {session_data['access_token']}"}

    # Join player
    user2 = await register_user(client, f"mp_{session_data['code'][:3]}", "Map Player")
    h2 = {"Authorization": f"Bearer {user2['access_token']}"}
    with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
        join_resp = await client.post("/api/session/join",
            json={"code": session_data["code"], "name": "MapPlayer"}, headers=h2)
    join_data = join_resp.json()
    player_session_h = {"Authorization": f"Bearer {join_data['access_token']}"}

    return session_data, gm_h, join_data, player_session_h


@pytest.mark.asyncio
class TestCreateMap:
    async def test_gm_creates_map(self, client):
        _, gm_h, _, _ = await _setup_map_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/session/maps", json={
                "name": "Battle Map",
                "width": 1920,
                "height": 1080,
                "grid_scale": 50,
            }, headers=gm_h)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Battle Map"
        assert data["is_active"] is False

    async def test_player_cannot_create(self, client):
        _, _, _, player_h = await _setup_map_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/session/maps", json={
                "name": "Sneaky Map",
            }, headers=player_h)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestGetMaps:
    async def test_returns_list(self, client):
        _, gm_h, _, _ = await _setup_map_session(client)

        resp = await client.get("/api/session/maps", headers=gm_h)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestSetActiveMap:
    async def test_gm_activates(self, client):
        _, gm_h, _, _ = await _setup_map_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/session/maps", json={
                "name": "Map1",
            }, headers=gm_h)
            map_id = create_resp.json()["id"]

            resp = await client.put(f"/api/maps/{map_id}/active", headers=gm_h)
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True

    async def test_player_cannot_activate(self, client):
        _, gm_h, _, player_h = await _setup_map_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/session/maps", json={
                "name": "Map2",
            }, headers=gm_h)
            map_id = create_resp.json()["id"]

        resp = await client.put(f"/api/maps/{map_id}/active", headers=player_h)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestAddToken:
    async def test_gm_adds_token(self, client):
        _, gm_h, _, _ = await _setup_map_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/session/maps", json={
                "name": "TokenMap",
            }, headers=gm_h)
            map_id = create_resp.json()["id"]

            resp = await client.post(f"/api/maps/{map_id}/tokens", json={
                "x": 100.0,
                "y": 200.0,
                "type": "monster",
                "label": "Goblin",
                "color": "#ff0000",
            }, headers=gm_h)
        assert resp.status_code == 200
        data = resp.json()
        assert data["x"] == 100.0
        assert data["label"] == "Goblin"

    async def test_player_cannot_add_token(self, client):
        _, gm_h, _, player_h = await _setup_map_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/session/maps", json={
                "name": "NoPlayerTokens",
            }, headers=gm_h)
            map_id = create_resp.json()["id"]

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post(f"/api/maps/{map_id}/tokens", json={
                "x": 0.0, "y": 0.0,
            }, headers=player_h)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestUpdateToken:
    async def test_gm_moves_any_token(self, client):
        _, gm_h, _, _ = await _setup_map_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/session/maps", json={
                "name": "MoveMap",
            }, headers=gm_h)
            map_id = create_resp.json()["id"]

            token_resp = await client.post(f"/api/maps/{map_id}/tokens", json={
                "x": 0.0, "y": 0.0, "type": "monster", "label": "Orc",
            }, headers=gm_h)
            token_id = token_resp.json()["id"]

            resp = await client.patch(f"/api/tokens/{token_id}", json={
                "x": 50.0, "y": 75.0,
            }, headers=gm_h)
        assert resp.status_code == 200
        assert resp.json()["x"] == 50.0
        assert resp.json()["y"] == 75.0

    async def test_player_cannot_move_monster(self, client):
        _, gm_h, _, player_h = await _setup_map_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/session/maps", json={
                "name": "ForbidMap",
            }, headers=gm_h)
            map_id = create_resp.json()["id"]

            token_resp = await client.post(f"/api/maps/{map_id}/tokens", json={
                "x": 0.0, "y": 0.0, "type": "monster",
            }, headers=gm_h)
            token_id = token_resp.json()["id"]

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.patch(f"/api/tokens/{token_id}", json={
                "x": 999.0,
            }, headers=player_h)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestDeleteToken:
    async def test_gm_deletes(self, client):
        _, gm_h, _, _ = await _setup_map_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/session/maps", json={
                "name": "DelMap",
            }, headers=gm_h)
            map_id = create_resp.json()["id"]

            token_resp = await client.post(f"/api/maps/{map_id}/tokens", json={
                "x": 0.0, "y": 0.0,
            }, headers=gm_h)
            token_id = token_resp.json()["id"]

            resp = await client.delete(f"/api/tokens/{token_id}", headers=gm_h)
        assert resp.status_code == 200

    async def test_player_cannot_delete(self, client):
        _, gm_h, _, player_h = await _setup_map_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/session/maps", json={
                "name": "NoDelMap",
            }, headers=gm_h)
            map_id = create_resp.json()["id"]

            token_resp = await client.post(f"/api/maps/{map_id}/tokens", json={
                "x": 0.0, "y": 0.0,
            }, headers=gm_h)
            token_id = token_resp.json()["id"]

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.delete(f"/api/tokens/{token_id}", headers=player_h)
        assert resp.status_code == 403
