import pytest


@pytest.mark.asyncio
class TestRegister:
    async def test_success(self, client):
        resp = await client.post("/api/users/register", json={
            "username": "newuser",
            "display_name": "New User",
            "password": "secret123",
            "role": "player",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["user"]["username"] == "newuser"
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_duplicate_username(self, client):
        await client.post("/api/users/register", json={
            "username": "duplicate",
            "display_name": "First",
            "password": "secret123",
        })
        resp = await client.post("/api/users/register", json={
            "username": "duplicate",
            "display_name": "Second",
            "password": "secret123",
        })
        assert resp.status_code == 400

    async def test_short_password(self, client):
        resp = await client.post("/api/users/register", json={
            "username": "weakuser",
            "display_name": "Weak",
            "password": "12345",
        })
        assert resp.status_code == 422

    async def test_short_username(self, client):
        resp = await client.post("/api/users/register", json={
            "username": "ab",
            "display_name": "Short",
            "password": "secret123",
        })
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    async def test_valid_creds(self, client):
        await client.post("/api/users/register", json={
            "username": "loginuser",
            "display_name": "Login User",
            "password": "mypassword",
        })
        resp = await client.post("/api/users/login", json={
            "username": "loginuser",
            "password": "mypassword",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["username"] == "loginuser"
        assert "access_token" in data

    async def test_wrong_password(self, client):
        await client.post("/api/users/register", json={
            "username": "loginuser2",
            "display_name": "Login User 2",
            "password": "mypassword",
        })
        resp = await client.post("/api/users/login", json={
            "username": "loginuser2",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    async def test_nonexistent_user(self, client):
        resp = await client.post("/api/users/login", json={
            "username": "noone",
            "password": "anything",
        })
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestGetMe:
    async def test_authenticated(self, client):
        reg_resp = await client.post("/api/users/register", json={
            "username": "meuser",
            "display_name": "Me User",
            "password": "secret123",
        })
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/api/users/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "meuser"

    async def test_unauthenticated(self, client):
        resp = await client.get("/api/users/me")
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
class TestGetMyStats:
    async def test_returns_stats(self, client):
        reg_resp = await client.post("/api/users/register", json={
            "username": "statsuser",
            "display_name": "Stats User",
            "password": "secret123",
        })
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/api/users/me/stats", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_characters" in data
        assert "total_npcs" in data
        assert "total_sessions" in data
        assert data["total_characters"] == 0

    async def test_unauthenticated(self, client):
        resp = await client.get("/api/users/me/stats")
        assert resp.status_code in (401, 403)
