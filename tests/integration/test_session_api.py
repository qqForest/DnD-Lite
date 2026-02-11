import pytest
from unittest.mock import patch, AsyncMock


async def register_user(client, username="testgm", display_name="Test GM"):
    resp = await client.post("/api/users/register", json={
        "username": username,
        "display_name": display_name,
        "password": "secret123",
        "role": "gm",
    })
    return resp.json()


async def create_session_with_user(client):
    user_data = await register_user(client)
    user_headers = {"Authorization": f"Bearer {user_data['access_token']}"}
    resp = await client.post("/api/session", headers=user_headers)
    return resp, user_headers, user_data


@pytest.mark.asyncio
class TestCreateSession:
    async def test_creates_session(self, client):
        resp, _, _ = await create_session_with_user(client)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["code"]) == 6
        assert "access_token" in data
        assert "refresh_token" in data
        assert "gm_token" in data

    async def test_code_is_uppercase_alphanumeric(self, client):
        resp, _, _ = await create_session_with_user(client)
        code = resp.json()["code"]
        assert code == code.upper()
        assert code.isalnum()


@pytest.mark.asyncio
class TestJoinSession:
    async def _create_and_get_code(self, client):
        resp, user_headers, _ = await create_session_with_user(client)
        return resp.json()["code"], resp.json(), user_headers

    async def test_join_existing(self, client):
        code, session_data, _ = await self._create_and_get_code(client)
        user2 = await register_user(client, "player1", "Player 1")
        player_h = {"Authorization": f"Bearer {user2['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/session/join",
                json={"code": code, "name": "Player1"},
                headers=player_h)
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_code"] == code
        assert "access_token" in data
        assert "player_id" in data

    async def test_join_nonexistent_code(self, client):
        user = await register_user(client)
        headers = {"Authorization": f"Bearer {user['access_token']}"}
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/session/join",
                json={"code": "ZZZZZZ", "name": "Player1"},
                headers=headers)
        assert resp.status_code == 404

    async def test_join_duplicate_name(self, client):
        code, _, _ = await self._create_and_get_code(client)
        user2 = await register_user(client, "dup1", "Dup1")
        h2 = {"Authorization": f"Bearer {user2['access_token']}"}
        user3 = await register_user(client, "dup2", "Dup2")
        h3 = {"Authorization": f"Bearer {user3['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/session/join",
                json={"code": code, "name": "Duplicate"}, headers=h2)
            resp = await client.post("/api/session/join",
                json={"code": code, "name": "Duplicate"}, headers=h3)
        assert resp.status_code == 400

    async def test_join_case_insensitive_code(self, client):
        code, _, _ = await self._create_and_get_code(client)
        user2 = await register_user(client, "ciuser", "CI User")
        headers = {"Authorization": f"Bearer {user2['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/session/join",
                json={"code": code.lower(), "name": "Player1"},
                headers=headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestGetSessionState:
    async def test_returns_state(self, client):
        resp, _, _ = await create_session_with_user(client)
        session_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {session_token}"}

        resp = await client.get("/api/session", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_gm"] is True
        assert data["is_active"] is True
        assert data["session_started"] is False
        assert data["player_count"] >= 1

    async def test_requires_auth(self, client):
        resp = await client.get("/api/session")
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
class TestStartSession:
    async def test_gm_can_start(self, client):
        resp, _, _ = await create_session_with_user(client)
        session_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {session_token}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/session/start", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["session_started"] is True

    async def test_player_cannot_start(self, client):
        resp, _, _ = await create_session_with_user(client)
        code = resp.json()["code"]

        user2 = await register_user(client, "startplayer", "Start Player")
        h2 = {"Authorization": f"Bearer {user2['access_token']}"}
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            join_resp = await client.post("/api/session/join",
                json={"code": code, "name": "Player1"}, headers=h2)
        player_session_token = join_resp.json()["access_token"]
        player_headers = {"Authorization": f"Bearer {player_session_token}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/session/start", headers=player_headers)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestGetPlayers:
    async def test_returns_players(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        resp = await client.get("/api/session/players", headers=headers)
        assert resp.status_code == 200
        players = resp.json()
        assert len(players) >= 1
        assert players[0]["is_gm"] is True


@pytest.mark.asyncio
class TestPlayerReady:
    async def _join_player(self, client, code):
        user = await register_user(client, f"rdy_{code[:4]}", "Ready Player")
        h = {"Authorization": f"Bearer {user['access_token']}"}
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            join_resp = await client.post("/api/session/join",
                json={"code": code, "name": "ReadyPlayer"}, headers=h)
        return join_resp.json()

    async def test_player_can_set_ready(self, client):
        resp, _, _ = await create_session_with_user(client)
        code = resp.json()["code"]
        join_data = await self._join_player(client, code)
        player_headers = {"Authorization": f"Bearer {join_data['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/session/ready",
                json={"is_ready": True}, headers=player_headers)
        assert resp.status_code == 200
        assert resp.json()["is_ready"] is True

    async def test_gm_cannot_set_ready(self, client):
        resp, _, _ = await create_session_with_user(client)
        gm_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/session/ready",
                json={"is_ready": True}, headers=gm_headers)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestToggleMovement:
    async def _setup(self, client):
        resp, _, _ = await create_session_with_user(client)
        session_data = resp.json()
        gm_headers = {"Authorization": f"Bearer {session_data['access_token']}"}

        user2 = await register_user(client, f"mv_{session_data['code'][:3]}", "Mover")
        h2 = {"Authorization": f"Bearer {user2['access_token']}"}
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            join_resp = await client.post("/api/session/join",
                json={"code": session_data["code"], "name": "Mover"}, headers=h2)
        join_data = join_resp.json()
        return session_data, gm_headers, join_data

    async def test_gm_can_toggle(self, client):
        session_data, gm_headers, join_data = await self._setup(client)
        player_id = join_data["player_id"]

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.patch(f"/api/players/{player_id}/movement",
                headers=gm_headers)
        assert resp.status_code == 200
        assert resp.json()["can_move"] is True

    async def test_player_cannot_toggle(self, client):
        session_data, _, join_data = await self._setup(client)
        player_headers = {"Authorization": f"Bearer {join_data['access_token']}"}
        player_id = join_data["player_id"]

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.patch(f"/api/players/{player_id}/movement",
                headers=player_headers)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestRefreshToken:
    async def test_refresh_access_token(self, client):
        resp, _, _ = await create_session_with_user(client)
        data = resp.json()

        resp = await client.post("/api/auth/refresh", json={
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_type": "bearer",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()


@pytest.mark.asyncio
class TestPlayerDisconnect:
    async def test_player_marked_as_left_on_disconnect(self, client, db):
        """Player.left_at is set when marked as left"""
        from app.models.player import Player
        from datetime import datetime

        # Create session + player
        resp, _, _ = await create_session_with_user(client)
        session_data = resp.json()
        code = session_data["code"]

        user2 = await register_user(client, "player1", "Player 1")
        player_h = {"Authorization": f"Bearer {user2['access_token']}"}
        join_resp = await client.post("/api/session/join",
            json={"code": code, "name": "TestPlayer"}, headers=player_h)
        join_data = join_resp.json()
        player_id = join_data["player_id"]

        # Simulate disconnect by setting left_at
        player = db.query(Player).filter(Player.id == player_id).first()
        player.left_at = datetime.utcnow()
        db.commit()

        # Verify player not in active list
        gm_headers = {"Authorization": f"Bearer {session_data['access_token']}"}
        players_resp = await client.get("/api/session/players", headers=gm_headers)
        players = players_resp.json()
        assert all(p["id"] != player_id for p in players)

    async def test_player_can_reconnect_after_left(self, client, db):
        """Player with left_at can reconnect using same name"""
        from app.models.player import Player
        from datetime import datetime

        # Create session
        resp, _, _ = await create_session_with_user(client)
        session_data = resp.json()
        code = session_data["code"]

        user2 = await register_user(client, "player1", "Player 1")
        player_h = {"Authorization": f"Bearer {user2['access_token']}"}

        # Join first time
        join_resp = await client.post("/api/session/join",
            json={"code": code, "name": "TestPlayer"}, headers=player_h)
        join_data = join_resp.json()
        player_id = join_data["player_id"]

        # Simulate disconnect
        player = db.query(Player).filter(Player.id == player_id).first()
        player.left_at = datetime.utcnow()
        db.commit()

        # Reconnect with same name
        reconnect_resp = await client.post("/api/session/join",
            json={"code": code, "name": "TestPlayer"}, headers=player_h)
        assert reconnect_resp.status_code == 200
        reconnect_data = reconnect_resp.json()

        # Verify same player_id returned
        assert reconnect_data["player_id"] == player_id

        # Verify left_at is cleared
        db.refresh(player)
        assert player.left_at is None


@pytest.mark.asyncio
class TestDeleteSession:
    async def test_gm_can_delete_session(self, client, db):
        """GM deletes session, cascades to all entities"""
        from app.models.session import Session
        from app.models.player import Player
        from app.models.character import Character

        # Create session
        resp, _, _ = await create_session_with_user(client)
        session_data = resp.json()
        code = session_data["code"]
        gm_session_token = session_data["access_token"]  # Use session token, not user token
        gm_headers = {"Authorization": f"Bearer {gm_session_token}"}

        # Add player with character
        user2 = await register_user(client, "player1", "Player 1")
        player_h = {"Authorization": f"Bearer {user2['access_token']}"}
        await client.post("/api/session/join",
            json={"code": code, "name": "TestPlayer"}, headers=player_h)

        # Get session_id
        session = db.query(Session).filter(Session.code == code).first()
        session_id = session.id

        # Delete session
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            delete_resp = await client.delete("/api/session", headers=gm_headers)
        assert delete_resp.status_code == 200

        # Verify session deleted
        session = db.query(Session).filter(Session.id == session_id).first()
        assert session is None

        # Verify cascaded deletion
        players = db.query(Player).filter(Player.session_id == session_id).all()
        assert len(players) == 0

    async def test_player_cannot_delete_session(self, client):
        """Non-GM cannot delete session"""
        # Create session
        resp, _, _ = await create_session_with_user(client)
        session_data = resp.json()
        code = session_data["code"]

        # Join as player
        user2 = await register_user(client, "player1", "Player 1")
        player_h = {"Authorization": f"Bearer {user2['access_token']}"}
        join_resp = await client.post("/api/session/join",
            json={"code": code, "name": "TestPlayer"}, headers=player_h)
        join_data = join_resp.json()
        player_token_header = {"Authorization": f"Bearer {join_data['access_token']}"}

        # Try delete as player → expect 403
        delete_resp = await client.delete("/api/session", headers=player_token_header)
        assert delete_resp.status_code == 403
