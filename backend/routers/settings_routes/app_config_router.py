from fastapi import APIRouter, status, Request


from backend.utils import Config

AppConfigRouter = APIRouter(
    prefix="/app-config",
    tags=["Settings"],
)


@AppConfigRouter.get(
    path="/",
    response_model=Config,
    summary="Get the app configuration.",
    description="Returns the app configuration.",
    response_description="The app configuration.",
    status_code=status.HTTP_200_OK,
)
async def app_config(req: Request) -> Config:
    return req.state.config
