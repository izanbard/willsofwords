from fastapi import APIRouter

from .settings_routes.proafanity_router import ProfanityRouter
from .settings_routes.project_defaults_router import ProjectDefaultsRouter

SettingsRouter = APIRouter(
    prefix="/settings",
    tags=["settings"],
)

SettingsRouter.include_router(ProfanityRouter)
SettingsRouter.include_router(ProjectDefaultsRouter)
