from fastapi import APIRouter
from app.api import session, characters, combat, dice, persistence, templates

api_router = APIRouter(prefix="/api")

api_router.include_router(session.router, tags=["session"])
api_router.include_router(characters.router, prefix="/characters", tags=["characters"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(combat.router, prefix="/combat", tags=["combat"])
api_router.include_router(dice.router, prefix="/dice", tags=["dice"])
api_router.include_router(persistence.router, tags=["persistence"])
