from math import ceil, floor, sqrt

from .project_config import ProjectConfig


class GridSize:
    """
    Represents a grid size configuration for a puzzle.

    This class calculates the number of rows and columns required for a puzzle grid
    based on the given puzzle configuration, the length of the words, and the maximum
    density allowed. It ensures that the grid size respects the constraints defined
    in the puzzle configuration, such as maximum rows and columns.

    :ivar project_config: Configuration of the puzzle, including maximum rows and columns.
    :type project_config: ProjectConfig
    :ivar rows: Number of rows in the grid.
    :type rows: int or None
    :ivar columns: Number of columns in the grid.
    :type columns: int or None
    """

    def __init__(self, project_config: ProjectConfig, len_words: int, max_density: float):
        target_size: int = ceil(len_words / max_density)
        self.project_config: ProjectConfig = project_config
        self.rows = None
        self.columns = None
        self._get_height_and_width(target_size)

    def _get_height_and_width(self, target_size: int) -> None:
        """
        Computes and updates the number of rows and columns for a grid based on the given
        target size while ensuring it adheres to configuration constraints. It adjusts the
        rows and columns to either achieve a square grid when possible or the closest
        rectangular configuration that meets the target size and fits within
        the maximum allowed dimensions.

        :param target_size: The target number of grid cells that need to be allocated.
        :type target_size: int
        :return: None
        """
        if target_size > self.project_config.max_rows * self.project_config.max_columns:
            self.rows = self.project_config.max_rows
            self.columns = self.project_config.max_columns
            return

        target = sqrt(target_size)
        if target.is_integer() and target <= self.project_config.max_columns and target <= self.project_config.max_rows:
            self.rows = int(target)
            self.columns = int(target)
            return

        columns = min(floor(target), self.project_config.max_columns)
        rows = columns
        while columns * rows < target_size:
            rows += 1
            if rows > self.project_config.max_rows:
                self.rows = self.project_config.max_rows
                self.columns = self.project_config.max_columns
                return

        self.rows = rows
        self.columns = columns
