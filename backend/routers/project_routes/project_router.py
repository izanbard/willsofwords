import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request

from .command_router import CommandRouter
from backend.models import ProjectFolder, ProjectConfigUpdate, ProjectConfig, Wordlist
from . import get_project_files
from backend.utils import get_project_settings_defaults, save_project_settings

ProjectRouter = APIRouter(
    prefix="/project/{name}",
    tags=["Project"],
)


@ProjectRouter.get(
    "/",
    response_model=ProjectFolder,
    summary="Get the named project ",
    description="Returns the project folder contents",
    response_description="The project folder.",
    status_code=200,
)
async def get_project(name: str, req: Request) -> ProjectFolder:
    data_dir = Path(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Project {name} not found")
    project_folder = get_project_files(data_dir)
    return project_folder


@ProjectRouter.get(
    "/settings",
    response_model=ProjectConfig,
    summary="Get the named project settings",
    description="Returns the project settings",
    response_description="The project settings.",
    status_code=200,
)
async def get_settings(name: str, req: Request) -> ProjectConfig:
    data_dir = Path(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Project {name} settings not found")
    if (data_dir / req.state.config.app.project_settings).exists():
        with open(data_dir / req.state.config.app.project_settings, "r") as f:
            return ProjectConfig(**json.load(f))
    raise HTTPException(status_code=404, detail=f"Project {name} settings not found")


@ProjectRouter.put(
    "/settings",
    summary="Update the named project settings",
    description="Updates the project settings",
    status_code=status.HTTP_200_OK,
    response_description="The updated project settings.",
    response_model=ProjectConfig,
)
async def update_settings(name: str, req: Request, settings: ProjectConfigUpdate) -> ProjectConfig:
    data_dir = Path(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Project {name} not found")
    default_config = ProjectConfig(**get_project_settings_defaults())
    updates = settings.model_dump(exclude_unset=True)
    new_config = default_config.model_copy(update=updates)
    save_project_settings(new_config.model_dump(), data_dir / req.state.config.app.project_settings)
    return new_config


@ProjectRouter.get(
    "/wordlist",
    summary="Get the named project wordlist",
    description="Returns the project wordlist",
    response_description="The project wordlist.",
    status_code=200,
)
async def get_wordlist(name: str, req: Request) -> Wordlist:
    data_dir = Path(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Project {name} not found")
    wordlist_path = data_dir / req.state.config.app.input_filename
    if not wordlist_path.exists():
        raise HTTPException(status_code=404, detail=f"Project {name} wordlist not found")
    with open(wordlist_path, "r") as fd:
        return Wordlist(**json.load(fd))


@ProjectRouter.post(
    "/wordlist",
    summary="Update the named project wordlist",
    description="Updates the project wordlist",
    status_code=status.HTTP_200_OK,
    response_description="The updated project wordlist.",
)
async def update_wordlist(name: str, wordlist: Wordlist, req: Request) -> Wordlist:
    data_dir = Path(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Project {name} not found")
    validation_dict = wordlist.validate_word_lists()
    if validation_dict["profanity"] or validation_dict["illegal_chars"]:
        raise HTTPException(
            status_code=400,
            detail=f"Wordlist contains invalid words. Profanity: {validation_dict['profanity']}, Illegal Chars: {validation_dict['illegal_chars']}",
        )
    wordlist_path = data_dir / req.state.config.app.input_filename
    with open(wordlist_path, "w") as fd:
        json.dump(wordlist.model_dump(), fd, indent=2)
    return wordlist


ProjectRouter.include_router(CommandRouter)
