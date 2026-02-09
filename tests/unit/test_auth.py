import pytest
from jose import jwt

from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.config import get_settings

settings = get_settings()


class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("secret123")
        assert verify_password("secret123", hashed)

    def test_wrong_password(self):
        hashed = hash_password("secret123")
        assert not verify_password("wrong", hashed)

    def test_hash_is_different_each_time(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


class TestAccessToken:
    def test_contains_access_type(self):
        token = create_access_token({"sub": "test"})
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["type"] == "access"
        assert payload["sub"] == "test"

    def test_contains_exp(self):
        token = create_access_token({"sub": "test"})
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        assert "exp" in payload


class TestRefreshToken:
    def test_contains_refresh_type(self):
        token = create_refresh_token({"sub": "test"})
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["type"] == "refresh"
        assert payload["sub"] == "test"

    def test_contains_exp(self):
        token = create_refresh_token({"sub": "test"})
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        assert "exp" in payload


class TestTokenDecode:
    def test_decode_with_wrong_secret(self):
        token = create_access_token({"sub": "test"})
        with pytest.raises(Exception):
            jwt.decode(token, "wrong-secret", algorithms=[settings.jwt_algorithm])

    def test_decode_preserves_data(self):
        token = create_access_token({"sub": "player-uuid-123", "extra": "data"})
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "player-uuid-123"
        assert payload["extra"] == "data"
