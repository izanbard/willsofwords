import string
from pathlib import Path

from pydantic import BaseModel, Field

from .enums import LayoutEnum
from .grid_size import GridSize
from .puzzle import Puzzle
from .wordlist import Wordlist, Category
from .project_config import ProjectConfig
from backend.utils import Logger


class PuzzleBaseData(BaseModel):
    title: str = Field(..., description="Title of the book")
    puzzle_list: list[str] = Field(..., description="List of puzzle names")


class PuzzleData(BaseModel):
    project_config: ProjectConfig = Field(..., description="Configuration for puzzle generation")
    book_title: str = Field(..., description="Title of the book")
    wordlist: Wordlist = Field(..., description="List of words provided from LLM")
    puzzles: list[Puzzle] = Field(default_factory=list, description="List of created Puzzles")

    def create_and_save_data(self, filename: Path) -> None:
        self.create_puzzles(filename=filename)
        self.save_data(filename)

    def create_puzzles(self, filename: Path) -> None:
        Logger.get_logger().info("Creating puzzles")
        base = len(self.wordlist.category_list)
        count = 0
        for category in self.wordlist.category_list:
            self._add_a_puzzle(category)
            count += 1
            percentage = int(count / base * 90)
            self.set_marker_file(filename, percentage)
        self._check_fix_puzzle_order()
        self.set_marker_file(filename, 95)
        self.add_puzzle_display_name()
        self.set_marker_file(filename, 99)
        Logger.get_logger().info("Completed creating puzzles")

    @staticmethod
    def set_marker_file(filename: Path, percentage: int):
        PuzzleData.clear_marker_file(filename)
        (filename.parent / f"{filename.name}.{percentage:02d}.marker").touch()

    @staticmethod
    def clear_marker_file(filename: Path):
        for p in filename.parent.glob(f"{filename.name}.*.marker"):
            p.unlink()

    def save_data(self, filename: Path) -> None:
        Logger.get_logger().info(f"Saving puzzles to {filename}")
        with open(filename, "w") as fd:
            fd.write(self.model_dump_json(indent=2))
        self.clear_marker_file(filename)

        Logger.get_logger().info(f"Done saving puzzles to {filename}")

    def _add_a_puzzle(self, category: Category) -> None:
        Logger.get_logger().debug(f"Creating puzzle: {category.category}")
        len_words = sum(len(word) for word in category.word_list)
        size = GridSize(self.project_config, len_words, self.project_config.max_density)
        Logger.get_logger().debug(f"Puzzle Target Size: {size.columns}x{size.rows}")
        puzzle = Puzzle(
            project_config=self.project_config,
            puzzle_id=category.category.strip()
            .upper()
            .translate({ord(c): None for c in string.whitespace + string.digits + string.punctuation}),
            puzzle_title=category.category,
            input_word_list=category.word_list,
            long_fact=category.long_fact,
            short_fact=category.short_fact,
            columns=size.columns,
            rows=size.rows,
        )
        puzzle.populate_puzzle()
        count = 1
        while puzzle.density < self.project_config.min_density:
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
        if self.project_config.enable_profanity_filter:
            puzzle.check_for_inadvertent_profanity()
        if len(puzzle.profanity) > 0:
            for row, words in puzzle.profanity.items():
                Logger.get_logger().warn(f"Profanity found in row {row}, words: {words}")
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

    def get_puzzle_ids(self) -> list[str]:
        return [puzzle.puzzle_id for puzzle in self.puzzles]

    def get_puzzle_by_id(self, puzzle_id: str) -> Puzzle | None:
        for puzzle in self.puzzles:
            if puzzle.puzzle_id == puzzle_id:
                return puzzle
        return None
