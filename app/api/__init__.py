from fastapi import APIRouter
from app.api import session, characters, combat, dice, persistence, templates, maps, users
from app.api import user_characters, user_maps

api_router = APIRouter(prefix="/api")

api_router.include_router(session.router, tags=["session"])
api_router.include_router(characters.router, prefix="/characters", tags=["characters"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(combat.router, prefix="/combat", tags=["combat"])
api_router.include_router(dice.router, prefix="/dice", tags=["dice"])
api_router.include_router(persistence.router, tags=["persistence"])
api_router.include_router(maps.router, tags=["maps"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(user_characters.router, prefix="/me/characters", tags=["user-characters"])
api_router.include_router(user_maps.router, prefix="/me/maps", tags=["user-maps"])
