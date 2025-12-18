from pydantic import BaseModel, Field

from src.models import UtilsAddIn, SizeEnum, Size, Puzzle, Wordlist
from src.models.config import Config


class BookData(BaseModel, UtilsAddIn):
    book_title: str = Field(..., description="Title of the book")
    wordlist: Wordlist = Field(..., description="List of words provided from LLM")
    puzzles: list[Puzzle] = Field(default_factory=list, description="List of created Puzzles")

    def create_puzzles(self) -> None:
        for category in self.wordlist.category_list:
            len_words = sum(len(word) for word in category.word_list)
            size = Size(SizeEnum.LARGE)
            try:
                while (
                    self.calculate_density(Config.SIZES[size.size][0], Config.SIZES[size.size][1], len_words)
                    < Config.MIN_PUZZLE_DENSITY
                ):
                    size.downsize()
            except ValueError:
                size.size = SizeEnum.SMALL
            puzzle = Puzzle(
                puzzle_title=category.category,
                input_word_list=category.word_list,
                width=Config.SIZES[size.size][0],
                height=Config.SIZES[size.size][1],
            )
            puzzle.populate_puzzle()
            self.puzzles.append(puzzle)
