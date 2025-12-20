from math import ceil, sqrt, floor

from src.models.config import Config


class Size:
    def __init__(self, len_words: int, max_desnity: float):
        target_size: int = ceil(len_words / max_desnity)
        self.height, self.width = None, None
        self._get_height_and_width(target_size)

    def _get_height_and_width(self, target_size: int) -> None:
        if target_size > Config.MAX_PUZZLE_HEIGHT * Config.MAX_PUZZLE_WIDTH:
            self.height, self.width = Config.MAX_PUZZLE_HEIGHT, Config.MAX_PUZZLE_WIDTH
            return

        target = sqrt(target_size)
        if target.is_integer():
            self.height, self.width = int(target), int(target)
            return

        width = min(floor(target), Config.MAX_PUZZLE_WIDTH)
        height = width
        while width * height < target_size:
            height += 1
            if height > Config.MAX_PUZZLE_HEIGHT:
                self.height, self.width = Config.MAX_PUZZLE_HEIGHT, Config.MAX_PUZZLE_WIDTH
                return

        self.height, self.width = height, width
