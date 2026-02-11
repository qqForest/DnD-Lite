import pytest
from unittest.mock import patch, AsyncMock
from tests.integration.test_session_api import register_user, create_session_with_user


async def _join_player(client, code):
    user = await register_user(client, f"cp_{code[:4]}", "Char Player")
    h = {"Authorization": f"Bearer {user['access_token']}"}
    with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
        join_resp = await client.post("/api/session/join",
            json={"code": code, "name": "CharPlayer"}, headers=h)
    return join_resp.json()


@pytest.mark.asyncio
class TestListCharacters:
    async def test_requires_auth(self, client):
        resp = await client.get("/api/characters")
        assert resp.status_code in (401, 403)

    async def test_returns_list(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        resp = await client.get("/api/characters", headers=headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestCreateCharacter:
    async def test_create_success(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/characters", json={
                "name": "TestHero",
                "class_name": "Fighter",
                "max_hp": 12,
            }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "TestHero"
        assert data["current_hp"] == 12  # defaults to max_hp

    async def test_current_hp_defaults_to_max(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/characters", json={
                "name": "Hero2",
                "max_hp": 25,
            }, headers=headers)
        assert resp.json()["current_hp"] == 25


@pytest.mark.asyncio
class TestCharacterArmorClass:
    async def test_default_ac(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/characters", json={
                "name": "DefaultAC",
                "max_hp": 10,
            }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["armor_class"] == 10

    async def test_explicit_ac(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/characters", json={
                "name": "Knight",
                "max_hp": 12,
                "armor_class": 16,
            }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["armor_class"] == 16

    async def test_update_ac(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/characters", json={
                "name": "ACUpdate", "max_hp": 10,
            }, headers=headers)
            char_id = create_resp.json()["id"]

            resp = await client.patch(f"/api/characters/{char_id}", json={
                "armor_class": 18,
            }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["armor_class"] == 18


@pytest.mark.asyncio
class TestGetCharacter:
    async def test_get_existing(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/characters", json={
                "name": "Hero3", "max_hp": 10,
            }, headers=headers)
        char_id = create_resp.json()["id"]

        resp = await client.get(f"/api/characters/{char_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Hero3"

    async def test_404_nonexistent(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        resp = await client.get("/api/characters/99999", headers=headers)
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestUpdateCharacter:
    async def test_owner_can_update(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/characters", json={
                "name": "Updatable", "max_hp": 10,
            }, headers=headers)
            char_id = create_resp.json()["id"]

            resp = await client.patch(f"/api/characters/{char_id}", json={
                "name": "Updated",
            }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"

    async def test_other_player_cannot_update(self, client):
        resp, _, _ = await create_session_with_user(client)
        session_data = resp.json()
        gm_headers = {"Authorization": f"Bearer {session_data['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/characters", json={
                "name": "GMChar", "max_hp": 10,
            }, headers=gm_headers)
            char_id = create_resp.json()["id"]

        join_data = await _join_player(client, session_data["code"])
        player_headers = {"Authorization": f"Bearer {join_data['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.patch(f"/api/characters/{char_id}", json={
                "name": "Hacked",
            }, headers=player_headers)
        assert resp.status_code == 403

    async def test_gm_can_update_any(self, client):
        resp, _, _ = await create_session_with_user(client)
        session_data = resp.json()
        gm_headers = {"Authorization": f"Bearer {session_data['access_token']}"}

        join_data = await _join_player(client, session_data["code"])
        player_session_headers = {"Authorization": f"Bearer {join_data['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/characters", json={
                "name": "PlayerChar", "max_hp": 10,
            }, headers=player_session_headers)
            char_id = create_resp.json()["id"]

            resp = await client.patch(f"/api/characters/{char_id}", json={
                "current_hp": 5,
            }, headers=gm_headers)
        assert resp.status_code == 200
        assert resp.json()["current_hp"] == 5


@pytest.mark.asyncio
class TestDeleteCharacter:
    async def test_owner_can_delete(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/characters", json={
                "name": "Deletable", "max_hp": 10,
            }, headers=headers)
            char_id = create_resp.json()["id"]

            resp = await client.delete(f"/api/characters/{char_id}", headers=headers)
        assert resp.status_code == 200

    async def test_other_player_cannot_delete(self, client):
        resp, _, _ = await create_session_with_user(client)
        session_data = resp.json()
        gm_headers = {"Authorization": f"Bearer {session_data['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            create_resp = await client.post("/api/characters", json={
                "name": "Protected", "max_hp": 10,
            }, headers=gm_headers)
            char_id = create_resp.json()["id"]

        join_data = await _join_player(client, session_data["code"])
        player_headers = {"Authorization": f"Bearer {join_data['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.delete(f"/api/characters/{char_id}", headers=player_headers)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestCharacterAvatar:
    async def test_avatar_url_preserved_on_create(self, client):
        """Test that avatar_url is saved when creating a character."""
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        avatar_url = "/uploads/avatars/test-avatar.jpg"
        appearance = "A brave warrior"
        
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            resp = await client.post("/api/characters", json={
                "name": "TestNPC",
                "class_name": "Wizard",
                "max_hp": 10,
                "avatar_url": avatar_url,
                "appearance": appearance,
            }, headers=headers)
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "TestNPC"
        assert data["avatar_url"] == avatar_url
        assert data["appearance"] == appearance
