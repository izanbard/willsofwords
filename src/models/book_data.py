from pydantic import BaseModel, Field

from src.models import Size, Puzzle, Wordlist, Category
from src.models.config import Config
from src.utils import Logger


class BookData(BaseModel):
    book_title: str = Field(..., description="Title of the book")
    wordlist: Wordlist = Field(..., description="List of words provided from LLM")
    puzzles: list[Puzzle] = Field(default_factory=list, description="List of created Puzzles")

    def create_puzzles(self) -> None:
        Logger.get_logger().info("Creating puzzles")
        for category in self.wordlist.category_list:
            self._add_a_puzzle(category)
        Logger.get_logger().info("Completed creating puzzles")

    def _add_a_puzzle(self, category: Category) -> None:
        Logger.get_logger().debug(f"Creating puzzle: {category.category}")
        len_words = sum(len(word) for word in category.word_list)
        size = Size(len_words, Config.MAX_PUZZLE_DENSITY)
        Logger.get_logger().debug(f"Puzzle Target Size: {size.width}x{size.height}")
        puzzle = Puzzle(
            puzzle_title=category.category,
            input_word_list=category.word_list,
            width=size.width,
            height=size.height,
        )
        puzzle.populate_puzzle()
        count = 1
        while puzzle.density < Config.MIN_PUZZLE_DENSITY:
            Logger.get_logger().debug(f"Puzzle failed density check, trying again, actual density: {puzzle.density}")
            if count % 5 == 0:
                Logger.get_logger().debug("Reducing size of Puzzle before retry")
                if puzzle.height > puzzle.width:
                    puzzle.change_puzzle_size(puzzle.height - 1, puzzle.width)
                else:
                    puzzle.change_puzzle_size(puzzle.height, puzzle.width - 1)
            else:
                puzzle.puzzle_reset()
            puzzle.populate_puzzle()
            count += 1
        Logger.get_logger().debug(f"Completed puzzle: {category.category}")
        self.puzzles.append(puzzle)
