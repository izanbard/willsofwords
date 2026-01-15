from fastapi import APIRouter

from .settings_routes.proafanity_router import ProfanityRouter
from .settings_routes.project_defaults_router import ProjectDefaultsRouter
from .settings_routes.app_config_router import AppConfigRouter

SettingsRouter = APIRouter(
    prefix="/settings",
    tags=["settings"],
)

SettingsRouter.include_router(ProfanityRouter)
SettingsRouter.include_router(ProjectDefaultsRouter)
SettingsRouter.include_router(AppConfigRouter)
