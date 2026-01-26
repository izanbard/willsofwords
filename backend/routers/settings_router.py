from fastapi import APIRouter

from .settings_routes.app_config_router import AppConfigRouter
from .settings_routes.proafanity_router import ProfanityRouter
from .settings_routes.project_defaults_router import ProjectDefaultsRouter

SettingsRouter = APIRouter(
    prefix="/settings",
    tags=["Settings"],
)

SettingsRouter.include_router(ProfanityRouter)
SettingsRouter.include_router(ProjectDefaultsRouter)
SettingsRouter.include_router(AppConfigRouter)
