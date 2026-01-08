from math import ceil, sqrt, floor

from backend.utils import PuzzleConfig


class GridSize:
    def __init__(self, puzzle_config: PuzzleConfig, len_words: int, max_density: float):
        target_size: int = ceil(len_words / max_density)
        self.puzzle_config: PuzzleConfig = puzzle_config
        self.rows = None
        self.columns = None
        self._get_height_and_width(target_size)

    def _get_height_and_width(self, target_size: int) -> None:
        if target_size > self.puzzle_config.max_rows * self.puzzle_config.max_columns:
            self.rows = self.puzzle_config.max_rows
            self.columns = self.puzzle_config.max_columns
            return

        target = sqrt(target_size)
        if target.is_integer() and target <= self.puzzle_config.max_columns and target <= self.puzzle_config.max_rows:
            self.rows = int(target)
            self.columns = int(target)
            return

        columns = min(floor(target), self.puzzle_config.max_columns)
        rows = columns
        while columns * rows < target_size:
            rows += 1
            if rows > self.puzzle_config.max_rows:
                self.rows = self.puzzle_config.max_rows
                self.columns = self.puzzle_config.max_columns
                return

        self.rows = rows
        self.columns = columns
