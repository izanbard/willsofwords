from fastapi import APIRouter

CommandRouter = APIRouter(
    prefix="/command",
    tags=["Command"],
)


@CommandRouter.get("/{command}")
async def get_command(name: str, command: str):
    return {"message": f"Command endpoint for project {name} and command {command}"}
