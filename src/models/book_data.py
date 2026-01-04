from pathlib import Path

from pydantic import BaseModel, Field

from src.models.config import Config
from .enums import LayoutEnum
from .grid_size import GridSize
from .puzzle import Puzzle
from .wordlist import Wordlist, Category
from src.utils import Logger


class BookData(BaseModel):
    book_title: str = Field(..., description="Title of the book")
    wordlist: Wordlist = Field(..., description="List of words provided from LLM")
    puzzles: list[Puzzle] = Field(default_factory=list, description="List of created Puzzles")

    def create_puzzles(self) -> None:
        Logger.get_logger().info("Creating puzzles")
        for category in self.wordlist.category_list:
            self._add_a_puzzle(category)
        self._check_fix_puzzle_order()
        self.add_puzzle_display_name()
        Logger.get_logger().info("Completed creating puzzles")

    def save_data(self, filename: Path) -> None:
        Logger.get_logger().info(f"Saving puzzles to {filename}")
        with open(filename, "w") as fd:
            fd.write(self.model_dump_json(indent=2))
        Logger.get_logger().info(f"Done saving puzzles to {filename}")

    def _add_a_puzzle(self, category: Category) -> None:
        Logger.get_logger().debug(f"Creating puzzle: {category.category}")
        len_words = sum(len(word) for word in category.word_list)
        size = GridSize(len_words, Config.PUZZLE_MAX_DENSITY)
        Logger.get_logger().debug(f"Puzzle Target Size: {size.columns}x{size.rows}")
        puzzle = Puzzle(
            puzzle_title=category.category,
            input_word_list=category.word_list,
            long_fact=category.long_fact,
            short_fact=category.short_fact,
            columns=size.columns,
            rows=size.rows,
        )
        puzzle.populate_puzzle()
        count = 1
        while puzzle.density < Config.PUZZLE_MIN_DENSITY:
            Logger.get_logger().debug(f"Puzzle failed density check, trying again, actual density: {puzzle.density}")
            if count % 5 == 0:
                Logger.get_logger().debug("Reducing size of Puzzle before retry")
                if puzzle.rows > puzzle.columns:
                    puzzle.change_puzzle_size(puzzle.rows - 1, puzzle.columns)
                else:
                    puzzle.change_puzzle_size(puzzle.rows, puzzle.columns - 1)
            else:
                puzzle.puzzle_reset()
            puzzle.populate_puzzle()
            count += 1
        Logger.get_logger().info(
            f"{puzzle.puzzle_title:<25} -> {len(puzzle.puzzle_search_list):02g} words out "
            f"of {len(puzzle.input_word_list):02g}, size {puzzle.columns:02g}x{puzzle.rows:02g} with "
            f"a density of {puzzle.density:.2%}"
        )
        self.puzzles.append(puzzle)

    def _check_fix_puzzle_order(self) -> None:
        length = len(self.puzzles)
        single_count = 0
        index = 0
        while index < length:
            layout = self.puzzles[index].get_puzzle_layout()
            if layout == LayoutEnum.SINGLE:
                single_count += 1
                index += 1
            elif layout == LayoutEnum.DOUBLE:
                if single_count % 2 != 0:
                    self.puzzles[index], self.puzzles[index - 1] = (
                        self.puzzles[index - 1],
                        self.puzzles[index],
                    )
                    single_count -= 1
                else:
                    index += 1

    def add_puzzle_display_name(self):
        for puzzle_number, puzzle in enumerate(self.puzzles, 1):
            puzzle.display_title = str(puzzle_number) + ". " + puzzle.puzzle_title
