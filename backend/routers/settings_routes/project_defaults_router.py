from fastapi import APIRouter, status

from backend.models import ProjectConfig, ProjectConfigUpdate
from backend.utils import get_project_settings_defaults, save_project_settings

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
    return ProjectConfig(**get_project_settings_defaults())


@ProjectDefaultsRouter.patch(
    path="/",
    response_model=ProjectConfig,
    summary="Patch the project configuration.",
    description="Patch the project configuration.",
    response_description="The updated project configuration.",
    status_code=status.HTTP_200_OK,
)
async def patch_project_defaults(config: ProjectConfigUpdate) -> ProjectConfig:
    old_config = ProjectConfig(**get_project_settings_defaults())
    updates = config.model_dump(exclude_unset=True)
    new_config = old_config.model_copy(update=updates)
    save_project_settings(new_config.model_dump())
    return new_config


@ProjectDefaultsRouter.post(
    path="/",
    response_model=ProjectConfig,
    summary="replace entire project defaults with new defaults",
    description="replace entire project defaults with new defaults",
    status_code=status.HTTP_200_OK,
)
async def replace_project_defaults(new_config: ProjectConfig) -> ProjectConfig:
    save_project_settings(new_config.model_dump())
    return new_config
