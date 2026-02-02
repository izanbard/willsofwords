from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext

from backend.models import PuzzleInput
from backend.models.wordlist import WordlistInput


class AIAgent:
    def __init__(self, topic_agent: Agent, puzzle_input_agent: Agent):
        self.topic_agent: Agent = topic_agent
        self.puzzle_input_agent: Agent = puzzle_input_agent

    @staticmethod
    def extra_instructions(ctx: RunContext[WordlistInput]) -> str:
        return (
            f"The provided sub topic was derived from '{ctx.deps.topic}' and has an introductory paragraph "
            f"of '{ctx.deps.front_page_introduction}'. Please ensure that the 'word list', 'introduction' and 'did you "
            f"know' for this subtopic are relevant to the overall topic."
        )

    async def get_sub_topics(self, main_topic: str, number_of_puzzles: int) -> WordlistInput:
        response = await self.topic_agent.run(
            user_prompt=f"Create {number_of_puzzles} subtopics for the main topic of '{main_topic}'.",
            output_type=WordlistInput,
        )
        return response.output

    async def get_puzzle_input(self, subtopic: str, entries_per_puzzle: int, base_data: WordlistInput) -> PuzzleInput:
        response = await self.puzzle_input_agent.run(
            user_prompt=f"Please create the puzzle input for '{subtopic}' with {entries_per_puzzle} entries in the wordlist",
            output_type=PuzzleInput,
            instructions=self.extra_instructions,
            deps=base_data,
        )
        return response.output


class AICommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: str = Field(..., description="the command to be executed by the AI")
    main_topic: str = Field("", description="the main topic of the puzzle")
    number_of_puzzles: int = Field(1, description="the number of puzzles to be generated")
    entries_per_puzzle: int = Field(1, description="the number of entries per puzzle")
    wordlist_input: WordlistInput = Field(None, description="the input data for the wordlist")


class AIResponse(BaseModel):
    response: str = Field(..., description="the response from the AI")
    payload: dict = {}
