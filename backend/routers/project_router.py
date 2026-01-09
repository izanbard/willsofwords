from fastapi import APIRouter

from .command_router import CommandRouter

ProjectRouter = APIRouter(
    prefix="/project/{name}",
    tags=["project"],
)
ProjectRouter.include_router(CommandRouter)
