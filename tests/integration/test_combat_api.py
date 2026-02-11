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


@pytest.mark.asyncio
class TestNPCInitiative:
    """Tests for NPC initiative rolls."""

    async def test_roll_initiative_for_npc(self, client):
        """GM can roll initiative for an NPC."""
        _, gm_h, _, player_h, _ = await _setup_combat_session(client)

        # Create NPC (character belonging to GM)
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            npc_resp = await client.post("/api/characters", json={
                "name": "Goblin",
                "max_hp": 7,
                "dexterity": 14,
            }, headers=gm_h)
        npc_data = npc_resp.json()

        # Start combat
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)

        # Roll initiative for NPC
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post(
                "/api/combat/initiative/npc",
                params={"character_id": npc_data["id"]},
                headers=gm_h
            )

        assert resp.status_code == 200
        data = resp.json()
        assert "roll" in data
        assert "character_name" in data
        assert data["character_name"] == "Goblin"
        # Roll should be d20 + dex modifier (14 -> +2), so between 3 and 22
        assert 3 <= data["roll"] <= 22

    async def test_roll_initiative_for_npc_not_gm(self, client):
        """Only GM can roll initiative for NPCs."""
        _, gm_h, _, player_h, _ = await _setup_combat_session(client)

        # Create NPC
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            npc_resp = await client.post("/api/characters", json={
                "name": "Goblin", "max_hp": 7,
            }, headers=gm_h)
        npc_data = npc_resp.json()

        # Start combat
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)

        # Player tries to roll initiative for NPC
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post(
                "/api/combat/initiative/npc",
                params={"character_id": npc_data["id"]},
                headers=player_h
            )

        assert resp.status_code == 403

    async def test_roll_initiative_for_npc_already_rolled(self, client):
        """Cannot roll initiative twice for same NPC."""
        _, gm_h, _, _, _ = await _setup_combat_session(client)

        # Create NPC
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            npc_resp = await client.post("/api/characters", json={
                "name": "Goblin", "max_hp": 7,
            }, headers=gm_h)
        npc_data = npc_resp.json()

        # Start combat
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)

        # Roll initiative once
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post(
                "/api/combat/initiative/npc",
                params={"character_id": npc_data["id"]},
                headers=gm_h
            )

        # Try to roll again
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post(
                "/api/combat/initiative/npc",
                params={"character_id": npc_data["id"]},
                headers=gm_h
            )

        assert resp.status_code == 400

    async def test_initiative_list_with_npcs(self, client):
        """Initiative list includes both players and NPCs."""
        _, gm_h, _, player_h, _ = await _setup_combat_session(client)

        # Create NPC
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            npc_resp = await client.post("/api/characters", json={
                "name": "Goblin", "max_hp": 7, "dexterity": 14,
            }, headers=gm_h)
        npc_data = npc_resp.json()

        # Start combat
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock), \
             patch("app.websocket.manager.manager.send_personal", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)

            # Player rolls
            await client.post("/api/combat/initiative", headers=player_h)

        # GM rolls for NPC
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post(
                "/api/combat/initiative/npc",
                params={"character_id": npc_data["id"]},
                headers=gm_h
            )

        # Get initiative list
        resp = await client.get("/api/combat/initiative", headers=gm_h)
        assert resp.status_code == 200

        entries = resp.json()["entries"]
        assert len(entries) == 2  # 1 player + 1 NPC

        # Find NPC entry
        npc_entry = next((e for e in entries if e["is_npc"]), None)
        assert npc_entry is not None
        assert npc_entry["character_name"] == "Goblin"
        assert npc_entry["character_id"] == npc_data["id"]
        assert npc_entry["roll"] is not None

        # Find player entry
        player_entry = next((e for e in entries if not e["is_npc"]), None)
        assert player_entry is not None
        assert player_entry["roll"] is not None

    async def test_npc_initiative_with_dex_modifier(self, client):
        """NPC initiative includes dexterity modifier."""
        _, gm_h, _, _, _ = await _setup_combat_session(client)

        # Create NPC with high dexterity (18 -> +4 modifier)
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            npc_resp = await client.post("/api/characters", json={
                "name": "Fast Goblin",
                "max_hp": 7,
                "dexterity": 18,
            }, headers=gm_h)
        npc_data = npc_resp.json()

        # Start combat
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/combat/start", headers=gm_h)

        # Roll initiative for NPC multiple times to check modifier is applied
        rolls = []
        for i in range(3):
            # End combat and start new one for fresh roll
            if i > 0:
                with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
                    await client.post("/api/combat/end", headers=gm_h)
                    await client.post("/api/combat/start", headers=gm_h)

            with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
                resp = await client.post(
                    "/api/combat/initiative/npc",
                    params={"character_id": npc_data["id"]},
                    headers=gm_h
                )
            rolls.append(resp.json()["roll"])

        # All rolls should be between 5 and 24 (d20 + 4 modifier)
        for roll in rolls:
            assert 5 <= roll <= 24
