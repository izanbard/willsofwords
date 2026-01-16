from fastapi import APIRouter

from .command_router import CommandRouter

ProjectRouter = APIRouter(
    prefix="/project/{name}",
    tags=["Project"],
)
ProjectRouter.include_router(CommandRouter)
