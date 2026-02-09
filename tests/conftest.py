import uuid
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

from app.database import Base, get_db
from app.core.auth import create_access_token, hash_password
# Import ALL models so relationships resolve before create_all
from app.models.session import Session
from app.models.player import Player
from app.models.character import Character
from app.models.user import User
from app.models.item import Item  # noqa: F401
from app.models.spell import Spell  # noqa: F401
from app.models.combat import Combat, CombatParticipant, InitiativeRoll  # noqa: F401
from app.models.map import Map, MapToken  # noqa: F401
from app.models.user_character import UserCharacter  # noqa: F401
from app.models.user_map import UserMap, UserMapToken  # noqa: F401


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    TestSession = sessionmaker(bind=connection)
    session = TestSession()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
async def client(db):
    from app.main import app

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# --- Factory fixtures ---

@pytest.fixture()
def create_session_fixture(db):
    def _create(name="TestGM"):
        token = str(uuid.uuid4())
        code = uuid.uuid4().hex[:6].upper()
        session = Session(code=code, gm_token=token, is_active=True)
        db.add(session)
        db.flush()

        gm_player = Player(
            session_id=session.id,
            name=name,
            token=token,
            is_gm=True,
        )
        db.add(gm_player)
        db.flush()
        return session, gm_player

    return _create


@pytest.fixture()
def create_player_fixture(db):
    def _create(session, name="Player1"):
        token = str(uuid.uuid4())
        player = Player(
            session_id=session.id,
            name=name,
            token=token,
            is_gm=False,
        )
        db.add(player)
        db.flush()
        return player

    return _create


@pytest.fixture()
def create_character_fixture(db):
    def _create(player, name="Hero", **kwargs):
        defaults = dict(
            player_id=player.id,
            name=name,
            class_name="Fighter",
            level=1,
            strength=16,
            dexterity=14,
            constitution=14,
            intelligence=10,
            wisdom=12,
            charisma=8,
            max_hp=12,
            current_hp=12,
        )
        defaults.update(kwargs)
        char = Character(**defaults)
        db.add(char)
        db.flush()
        return char

    return _create


@pytest.fixture()
def create_user_fixture(db):
    counter = {"n": 0}

    def _create(username=None, display_name=None, password="testpass123"):
        counter["n"] += 1
        if username is None:
            username = f"testuser{counter['n']}"
        if display_name is None:
            display_name = f"Test User {counter['n']}"
        user = User(
            username=username,
            display_name=display_name,
            hashed_password=hash_password(password),
            role="player",
        )
        db.add(user)
        db.flush()
        return user

    return _create


# --- Token / header helpers ---

def make_player_headers(player: Player) -> dict:
    token = create_access_token({"sub": player.token})
    return {"Authorization": f"Bearer {token}"}


def make_user_headers(user: User) -> dict:
    token = create_access_token({"sub": f"user:{user.id}"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def gm_headers(create_session_fixture):
    session, gm = create_session_fixture()
    return make_player_headers(gm), session, gm


@pytest.fixture()
def player_headers(create_session_fixture, create_player_fixture):
    session, gm = create_session_fixture()
    player = create_player_fixture(session)
    return make_player_headers(player), session, gm, player


@pytest.fixture()
def user_headers(create_user_fixture):
    user = create_user_fixture()
    return make_user_headers(user), user
