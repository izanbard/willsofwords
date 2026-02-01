from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent

from backend.models import PuzzleInput
from backend.models.wordlist import WordlistInput


class AIAgent:
    def __init__(self, topic_agent: Agent, puzzle_input_agent: Agent):
        self.topic_agent: Agent = topic_agent
        self.puzzle_input_agent: Agent = puzzle_input_agent

    async def get_sub_topics(self, main_topic: str, number_of_puzzles: int) -> WordlistInput:
        response = await self.topic_agent.run(
            user_prompt=f"Create {number_of_puzzles} subtopics for the main topic of '{main_topic}'.",
            output_type=WordlistInput,
        )
        return response.output

    async def get_puzzle_input(self, subtopic: str, entries_per_puzzle: int) -> PuzzleInput:
        response = await self.puzzle_input_agent.run(
            user_prompt=f"Please create the puzzle input for '{subtopic}' with {entries_per_puzzle} entries in the wordlist",
            output_type=PuzzleInput,
        )
        return response.output


class AICommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: str = Field(..., description="the command to be executed by the AI")
    main_topic: str = Field("", description="the main topic of the puzzle")
    number_of_puzzles: int = Field(1, description="the number of puzzles to be generated")
    entries_per_puzzle: int = Field(1, description="the number of entries per puzzle")
    subtopic_list: list[str] = Field([], description="the list of subtopics to be used for the puzzle")


class AIResponse(BaseModel):
    response: str = Field(..., description="the response from the AI")
    payload: dict = {}
