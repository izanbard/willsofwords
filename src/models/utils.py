from abc import ABC


class UtilsAddIn(ABC):
    @staticmethod
    def calculate_density(height: int, width: int, solution_count: int) -> float:
        total_area = height * width
        density = solution_count / total_area
        return density
