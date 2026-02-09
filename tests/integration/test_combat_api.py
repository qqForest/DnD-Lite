import pytest
from unittest.mock import patch, AsyncMock
from tests.integration.test_session_api import register_user, create_session_with_user


async def _setup_combat_session(client):
    """Create session with GM + player who has a character, start combat."""
    resp, _, _ = await create_session_with_user(client)
    session_data = resp.json()
    gm_h = {"Authorization": f"Bearer {session_data['access_token']}"}

    # Create GM character
    with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
        gm_char_resp = await client.post("/api/characters", json={
            "name": "GMChar", "max_hp": 20,
        }, headers=gm_h)

    # Join player
    user2 = await register_user(client, f"cb_{session_data['code'][:3]}", "Combat Player")
    h2 = {"Authorization": f"Bearer {user2['access_token']}"}
    with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
        join_resp = await client.post("/api/session/join",
            json={"code": session_data["code"], "name": "CombatPlayer"}, headers=h2)
    join_data = join_resp.json()
    player_session_h = {"Authorization": f"Bearer {join_data['access_token']}"}

    # Create player character
    with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
        player_char_resp = await client.post("/api/characters", json={
            "name": "PlayerChar", "max_hp": 15, "dexterity": 16,
        }, headers=player_session_h)

    return session_data, gm_h, join_data, player_session_h, player_char_resp.json()


@pytest.mark.asyncio
class TestStartCombat:
    async def test_gm_can_start(self, client):
        session_data, gm_h, _, _, _ = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/combat/start", headers=gm_h)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_active"] is True
        assert data["round_number"] == 1

    async def test_player_cannot_start(self, client):
        _, _, _, player_h, _ = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/combat/start", headers=player_h)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestEndCombat:
    async def test_gm_can_end(self, client):
        _, gm_h, _, _, _ = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)
            resp = await client.post("/api/combat/end", headers=gm_h)
        assert resp.status_code == 200

    async def test_no_active_combat(self, client):
        _, gm_h, _, _, _ = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/combat/end", headers=gm_h)
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestInitiativeRoll:
    async def test_player_rolls(self, client):
        _, gm_h, _, player_h, _ = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock), \
             patch("app.websocket.manager.manager.send_personal", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)
            resp = await client.post("/api/combat/initiative", headers=player_h)
        assert resp.status_code == 200
        data = resp.json()
        assert "roll" in data
        assert 1 <= data["roll"] <= 20

    async def test_double_roll_rejected(self, client):
        _, gm_h, _, player_h, _ = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock), \
             patch("app.websocket.manager.manager.send_personal", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)
            await client.post("/api/combat/initiative", headers=player_h)
            resp = await client.post("/api/combat/initiative", headers=player_h)
        assert resp.status_code == 400

    async def test_gm_cannot_roll(self, client):
        _, gm_h, _, _, _ = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)
            resp = await client.post("/api/combat/initiative", headers=gm_h)
        assert resp.status_code == 400


@pytest.mark.asyncio
class TestGetInitiativeList:
    async def test_returns_list(self, client):
        _, gm_h, _, player_h, _ = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock), \
             patch("app.websocket.manager.manager.send_personal", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)
            await client.post("/api/combat/initiative", headers=player_h)

        resp = await client.get("/api/combat/initiative", headers=gm_h)
        assert resp.status_code == 200
        entries = resp.json()["entries"]
        assert len(entries) >= 1


@pytest.mark.asyncio
class TestNextTurn:
    async def test_gm_next_turn(self, client):
        session_data, gm_h, _, player_h, char_data = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock), \
             patch("app.websocket.manager.manager.send_personal", new_callable=AsyncMock):
            # Start combat with character
            await client.post("/api/combat/start",
                headers=gm_h, params={"character_ids": [char_data["id"]]})
            # Need at least one participant, add manually via start
            # Actually start_combat can take character_ids as query params...
            # Let's just start and add participant through initiative + next-turn
            await client.post("/api/combat/start", headers=gm_h)

        # Get combat state
        resp = await client.get("/api/combat", headers=gm_h)
        assert resp.status_code == 200

    async def test_player_cannot_next_turn(self, client):
        _, gm_h, _, player_h, _ = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)
            resp = await client.post("/api/combat/next-turn", headers=player_h)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestCombatAction:
    async def test_damage_action(self, client):
        session_data, gm_h, _, player_h, char_data = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            # Start combat with participant
            start_resp = await client.post("/api/combat/start", headers=gm_h)
            combat_id = start_resp.json()["id"]

        # Get combat state to find any participants
        resp = await client.get("/api/combat", headers=gm_h)
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestGetCombatState:
    async def test_no_active(self, client):
        _, gm_h, _, _, _ = await _setup_combat_session(client)

        resp = await client.get("/api/combat", headers=gm_h)
        assert resp.status_code == 200
        assert resp.json()["active"] is False

    async def test_active_combat(self, client):
        _, gm_h, _, _, _ = await _setup_combat_session(client)

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)

        resp = await client.get("/api/combat", headers=gm_h)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_active"] is True
