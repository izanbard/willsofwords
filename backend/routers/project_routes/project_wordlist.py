from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic_ai import Agent
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from backend.models import Wordlist
from backend.models.aiagent import AIAgent, AICommand, AIResponse
from backend.routers import (
    check_wordlist_exists,
    get_wordlist_path,
    load_wordlist,
    validate_word_lists,
    get_topic_agent,
    get_puzzle_input_agent,
)
from backend.utils import Logger

ProjectWordlistRouter = APIRouter(
    prefix="/wordlist",
    tags=["Project"],
)


@ProjectWordlistRouter.get(
    "/",
    summary="Get the named project wordlist",
    description="Returns the project wordlist",
    response_description="The project wordlist.",
    status_code=status.HTTP_200_OK,
)
async def get_wordlist(wordlist: Annotated[Wordlist, Depends(load_wordlist)]) -> Wordlist:
    return wordlist


@ProjectWordlistRouter.post(
    "/",
    summary="Update the named project wordlist",
    description="Updates the project wordlist",
    status_code=status.HTTP_200_OK,
    response_description="The updated project wordlist.",
)
async def update_wordlist(new_wordlist: Wordlist, wordlist_path: Annotated[FilePath, Depends(get_wordlist_path)]) -> Wordlist:
    new_wordlist = validate_word_lists(new_wordlist)
    new_wordlist.save_wordlist(wordlist_path)
    load_wordlist.cache_clear()
    return new_wordlist


@ProjectWordlistRouter.delete(
    "/",
    summary="Delete the named project wordlist",
    description="Deletes the project wordlist",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_wordlist(wordlist_path: Annotated[FilePath, Depends(check_wordlist_exists)]) -> None:
    wordlist_path.unlink()
    load_wordlist.cache_clear()
    return None


@ProjectWordlistRouter.websocket(
    "/ws",
)
async def create_wordlist(
    websocket: WebSocket,
    topic_agent: Annotated[Agent, Depends(get_topic_agent)],
    puzzle_input_agent: Annotated[Agent, Depends(get_puzzle_input_agent)],
):
    await websocket.accept()
    ai_agent = AIAgent(topic_agent=topic_agent, puzzle_input_agent=puzzle_input_agent)

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json(
                    AIResponse(response="error", payload={"message": f"Invalid message: {e}"}).model_dump()
                )
                continue

            try:
                instructions = AICommand(**data)
                Logger.get_logger().info(f"Received command: {instructions.command}")
            except Exception as e:
                await websocket.send_json(
                    AIResponse(response="error", payload={"message": f"Invalid command payload: {e}"}).model_dump()
                )
                continue

            match instructions.command:
                case "ping":
                    await websocket.send_json(AIResponse(response="pong").model_dump())

                case "create":
                    try:
                        await websocket.send_json(AIResponse(response="thinking").model_dump())
                        sub_topics = await ai_agent.get_sub_topics(instructions.main_topic, instructions.number_of_puzzles)
                        await websocket.send_json(
                            AIResponse(response="topic_list", payload={"base_data": sub_topics}).model_dump()
                        )
                        Logger.get_logger().info(f"Created topic list for {instructions.main_topic}")
                        await websocket.send_json(AIResponse(response="not_thinking").model_dump())
                    except Exception as e:
                        await websocket.send_json(AIResponse(response="error", payload={"message": str(e)}).model_dump())

                case "puzzles":
                    try:
                        await websocket.send_json(AIResponse(response="thinking").model_dump())
                        puzzle_list = instructions.subtopic_list or []
                        for puzzle_topic in puzzle_list:
                            puzzle = await ai_agent.get_puzzle_input(puzzle_topic, instructions.entries_per_puzzle)
                            await websocket.send_json(AIResponse(response="puzzle", payload={"puzzle": puzzle}).model_dump())
                            Logger.get_logger().info(f"Created puzzle for {puzzle_topic}")
                        await websocket.send_json(AIResponse(response="not_thinking").model_dump())
                    except Exception as e:
                        await websocket.send_json(AIResponse(response="error", payload={"message": str(e)}).model_dump())

                case _:
                    await websocket.send_json(
                        AIResponse(response="error", payload={"message": "Unknown command"}).model_dump()
                    )
                    Logger.get_logger().warn(f"Received unknown command: {instructions.command}")
    finally:
        await websocket.close()
