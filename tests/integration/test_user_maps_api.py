import pytest


async def _register_and_get_headers(client, username="um_user"):
    resp = await client.post("/api/users/register", json={
        "username": username,
        "display_name": "Map User",
        "password": "secret123",
    })
    data = resp.json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data


@pytest.mark.asyncio
class TestUserMapCRUD:
    async def test_create_map(self, client):
        h, _ = await _register_and_get_headers(client, "mapcreator")
        resp = await client.post("/api/me/maps", json={
            "name": "My Map",
            "width": 1920,
            "height": 1080,
        }, headers=h)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "My Map"
        assert data["width"] == 1920

    async def test_list_maps(self, client):
        h, _ = await _register_and_get_headers(client, "maplist")
        await client.post("/api/me/maps", json={"name": "Map1"}, headers=h)
        await client.post("/api/me/maps", json={"name": "Map2"}, headers=h)

        resp = await client.get("/api/me/maps", headers=h)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_map(self, client):
        h, _ = await _register_and_get_headers(client, "mapget")
        create_resp = await client.post("/api/me/maps", json={"name": "GetMe"}, headers=h)
        map_id = create_resp.json()["id"]

        resp = await client.get(f"/api/me/maps/{map_id}", headers=h)
        assert resp.status_code == 200
        assert resp.json()["name"] == "GetMe"

    async def test_delete_map(self, client):
        h, _ = await _register_and_get_headers(client, "mapdel")
        create_resp = await client.post("/api/me/maps", json={"name": "DeleteMe"}, headers=h)
        map_id = create_resp.json()["id"]

        resp = await client.delete(f"/api/me/maps/{map_id}", headers=h)
        assert resp.status_code == 204

    async def test_requires_auth(self, client):
        resp = await client.get("/api/me/maps")
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
class TestUserMapTokenCRUD:
    async def test_create_token(self, client):
        h, _ = await _register_and_get_headers(client, "tokencreator")
        map_resp = await client.post("/api/me/maps", json={"name": "TokenMap"}, headers=h)
        map_id = map_resp.json()["id"]

        resp = await client.post(f"/api/me/maps/{map_id}/tokens", json={
            "type": "monster",
            "x": 100.0,
            "y": 200.0,
            "label": "Goblin",
        }, headers=h)
        assert resp.status_code == 201
        data = resp.json()
        assert data["label"] == "Goblin"
        assert data["x"] == 100.0

    async def test_delete_token(self, client):
        h, _ = await _register_and_get_headers(client, "tokendel")
        map_resp = await client.post("/api/me/maps", json={"name": "TDelMap"}, headers=h)
        map_id = map_resp.json()["id"]

        token_resp = await client.post(f"/api/me/maps/{map_id}/tokens", json={
            "type": "monster", "x": 0.0, "y": 0.0,
        }, headers=h)
        token_id = token_resp.json()["id"]

        resp = await client.delete(f"/api/me/maps/tokens/{token_id}", headers=h)
        assert resp.status_code == 204
