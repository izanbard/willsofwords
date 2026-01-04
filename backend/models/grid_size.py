from math import ceil, sqrt, floor

from backend.models.config import Config


class GridSize:
    def __init__(self, len_words: int, max_desnity: float):
        target_size: int = ceil(len_words / max_desnity)
        self.rows = None
        self.columns = None
        self._get_height_and_width(target_size)

    def _get_height_and_width(self, target_size: int) -> None:
        if target_size > Config.PUZZLE_MAX_ROWS * Config.PUZZLE_MAX_COLUMNS:
            self.rows = Config.PUZZLE_MAX_ROWS
            self.columns = Config.PUZZLE_MAX_COLUMNS
            return

        target = sqrt(target_size)
        if target.is_integer() and target <= Config.PUZZLE_MAX_COLUMNS and target <= Config.PUZZLE_MAX_ROWS:
            self.rows = int(target)
            self.columns = int(target)
            return

        columns = min(floor(target), Config.PUZZLE_MAX_COLUMNS)
        rows = columns
        while columns * rows < target_size:
            rows += 1
            if rows > Config.PUZZLE_MAX_ROWS:
                self.rows = Config.PUZZLE_MAX_ROWS
                self.columns = Config.PUZZLE_MAX_COLUMNS
                return

        self.rows = rows
        self.columns = columns
