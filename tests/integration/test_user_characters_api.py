import pytest


async def _register_and_get_headers(client, username="uc_user"):
    resp = await client.post("/api/users/register", json={
        "username": username,
        "display_name": "UC User",
        "password": "secret123",
    })
    data = resp.json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data


@pytest.mark.asyncio
class TestCreateUserCharacter:
    async def test_create(self, client):
        h, _ = await _register_and_get_headers(client)
        resp = await client.post("/api/me/characters", json={
            "name": "My Hero",
            "class_name": "Wizard",
            "max_hp": 8,
            "current_hp": 8,
        }, headers=h)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "My Hero"
        assert data["is_npc"] is False

    async def test_create_npc(self, client):
        h, _ = await _register_and_get_headers(client, "npc_user")
        resp = await client.post("/api/me/characters", json={
            "name": "Goblin",
            "is_npc": True,
            "max_hp": 5,
            "current_hp": 5,
        }, headers=h)
        assert resp.status_code == 201
        assert resp.json()["is_npc"] is True


@pytest.mark.asyncio
class TestListUserCharacters:
    async def test_list_all(self, client):
        h, _ = await _register_and_get_headers(client, "list_user")
        await client.post("/api/me/characters", json={"name": "Hero1", "max_hp": 10, "current_hp": 10}, headers=h)
        await client.post("/api/me/characters", json={"name": "NPC1", "is_npc": True, "max_hp": 5, "current_hp": 5}, headers=h)

        resp = await client.get("/api/me/characters", headers=h)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_filter_npc(self, client):
        h, _ = await _register_and_get_headers(client, "filter_user")
        await client.post("/api/me/characters", json={"name": "Hero", "max_hp": 10, "current_hp": 10}, headers=h)
        await client.post("/api/me/characters", json={"name": "NPC", "is_npc": True, "max_hp": 5, "current_hp": 5}, headers=h)

        resp = await client.get("/api/me/characters?is_npc=true", headers=h)
        assert resp.status_code == 200
        chars = resp.json()
        assert len(chars) == 1
        assert chars[0]["is_npc"] is True

    async def test_requires_auth(self, client):
        resp = await client.get("/api/me/characters")
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
class TestGetUserCharacter:
    async def test_own_character(self, client):
        h, _ = await _register_and_get_headers(client, "get_user")
        create_resp = await client.post("/api/me/characters", json={"name": "Mine", "max_hp": 10, "current_hp": 10}, headers=h)
        char_id = create_resp.json()["id"]

        resp = await client.get(f"/api/me/characters/{char_id}", headers=h)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Mine"

    async def test_other_user_404(self, client):
        h1, _ = await _register_and_get_headers(client, "owner1")
        create_resp = await client.post("/api/me/characters", json={"name": "Private", "max_hp": 10, "current_hp": 10}, headers=h1)
        char_id = create_resp.json()["id"]

        h2, _ = await _register_and_get_headers(client, "intruder1")
        resp = await client.get(f"/api/me/characters/{char_id}", headers=h2)
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestUpdateUserCharacter:
    async def test_update(self, client):
        h, _ = await _register_and_get_headers(client, "upd_user")
        create_resp = await client.post("/api/me/characters", json={"name": "Old", "max_hp": 10, "current_hp": 10}, headers=h)
        char_id = create_resp.json()["id"]

        resp = await client.patch(f"/api/me/characters/{char_id}", json={"name": "New"}, headers=h)
        assert resp.status_code == 200
        assert resp.json()["name"] == "New"


@pytest.mark.asyncio
class TestDeleteUserCharacter:
    async def test_delete(self, client):
        h, _ = await _register_and_get_headers(client, "del_user")
        create_resp = await client.post("/api/me/characters", json={"name": "Doomed", "max_hp": 10, "current_hp": 10}, headers=h)
        char_id = create_resp.json()["id"]

        resp = await client.delete(f"/api/me/characters/{char_id}", headers=h)
        assert resp.status_code == 204

        resp = await client.get(f"/api/me/characters/{char_id}", headers=h)
        assert resp.status_code == 404
