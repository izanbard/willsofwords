from fastapi import APIRouter, status
from pathlib import Path as FilePath
from backend.models import ProjectConfig

ProjectDefaultsRouter = APIRouter(
    prefix="/project-defaults",
    tags=["Settings"],
)


@ProjectDefaultsRouter.get(
    path="/",
    response_model=ProjectConfig,
    summary="Get the project configuration.",
    description="Returns the project configuration.",
    response_description="The project configuration.",
    status_code=status.HTTP_200_OK,
)
async def project_defaults() -> ProjectConfig:
    return ProjectConfig(**ProjectConfig.get_project_settings_defaults())


@ProjectDefaultsRouter.post(
    path="/",
    response_model=ProjectConfig,
    summary="replace entire project defaults with new defaults",
    description="replace entire project defaults with new defaults",
    status_code=status.HTTP_200_OK,
)
async def replace_project_defaults(new_config: ProjectConfig) -> ProjectConfig:
    new_config.save_config(FilePath("backend/project_settings.json"))
    return new_config
