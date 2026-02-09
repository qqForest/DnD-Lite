import pytest
from unittest.mock import patch, AsyncMock
from tests.integration.test_session_api import register_user, create_session_with_user


@pytest.mark.asyncio
class TestExportSession:
    async def test_gm_can_export(self, client):
        resp, _, _ = await create_session_with_user(client)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        resp = await client.post("/api/session/export", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "data" in data
        assert "session_info" in data["data"]

    async def test_player_cannot_export(self, client):
        resp, _, _ = await create_session_with_user(client)
        code = resp.json()["code"]

        user2 = await register_user(client, "exp_player", "Export Player")
        h2 = {"Authorization": f"Bearer {user2['access_token']}"}
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            join_resp = await client.post("/api/session/join",
                json={"code": code, "name": "ExpPlayer"}, headers=h2)
        player_h = {"Authorization": f"Bearer {join_resp.json()['access_token']}"}

        resp = await client.post("/api/session/export", headers=player_h)
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestImportSession:
    async def test_import_creates_session(self, client):
        # First export
        resp, _, _ = await create_session_with_user(client)
        gm_h = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        # Create a character so export has data
        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/characters", json={
                "name": "ExportHero", "max_hp": 20,
            }, headers=gm_h)

        export_resp = await client.post("/api/session/export", headers=gm_h)
        export_data = export_resp.json()["data"]

        # Import
        import_resp = await client.post("/api/session/import", json={
            "data": export_data,
        })
        assert import_resp.status_code == 200
        data = import_resp.json()
        assert data["success"] is True
        assert data["session_code"] is not None

    async def test_import_with_custom_code(self, client):
        resp, _, _ = await create_session_with_user(client)
        gm_h = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        export_resp = await client.post("/api/session/export", headers=gm_h)
        export_data = export_resp.json()["data"]

        import_resp = await client.post("/api/session/import", json={
            "data": export_data,
            "new_session_code": "CUSTOM",
        })
        assert import_resp.status_code == 200
        data = import_resp.json()
        assert data["success"] is True
        assert data["session_code"] == "CUSTOM"


@pytest.mark.asyncio
class TestValidateSession:
    async def test_valid_data(self, client):
        resp, _, _ = await create_session_with_user(client)
        gm_h = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        export_resp = await client.post("/api/session/export", headers=gm_h)
        export_data = export_resp.json()["data"]

        validate_resp = await client.post("/api/session/validate", json={
            "data": export_data,
        })
        assert validate_resp.status_code == 200
        data = validate_resp.json()
        assert data["is_valid"] is True

    async def test_invalid_data(self, client):
        validate_resp = await client.post("/api/session/validate", json={
            "data": {"garbage": True},
        })
        assert validate_resp.status_code == 200
        data = validate_resp.json()
        assert data["is_valid"] is False


@pytest.mark.asyncio
class TestRoundTrip:
    async def test_export_import_preserves_data(self, client):
        resp, _, _ = await create_session_with_user(client)
        gm_h = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        with patch("app.websocket.manager.manager.broadcast_event", new_callable=AsyncMock):
            await client.post("/api/characters", json={
                "name": "RoundTripHero",
                "class_name": "Barbarian",
                "max_hp": 15,
                "strength": 18,
            }, headers=gm_h)

        # Export
        export_resp = await client.post("/api/session/export", headers=gm_h)
        export_data = export_resp.json()["data"]

        # Import
        import_resp = await client.post("/api/session/import", json={
            "data": export_data,
        })
        import_data = import_resp.json()
        assert import_data["success"] is True

        # Verify the imported session has data
        assert import_data["entity_counts"] is not None
