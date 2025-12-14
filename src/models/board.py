import random
import string

from .cell import Cell
from .direction import DirectionEnum


class Board:
    def __init__(self, height: int, width: int) -> None:
        self.height: int = height
        self.width: int = width
        self.cells: list[list[Cell]] = [[Cell() for _ in range(width)] for _ in range(height)]

    def place_a_word(self, word: str) -> bool:
        orientation = random.randint(0, 3)
        if random.choice([True, False]):
            word = word[::-1]
        match orientation:
            case 0:
                direction = DirectionEnum.EW
                row = random.randint(0, self.height - 1)
                col = random.randint(0, self.width - len(word))
                space_available = all(
                    (
                        not self.cells[row][c].is_answer
                        or (self.cells[row][c].value == word[i] and self.cells[row][c].direction != direction)
                    )
                    for i, c in enumerate(range(col, col + len(word)))
                )
                if space_available:
                    for i, c in enumerate(range(col, col + len(word))):
                        self.cells[row][c].value = word[i]
                        self.cells[row][c].direction = direction
                        self.cells[row][c].is_answer = True
                    return True
            case 1:
                direction = DirectionEnum.NWSE
                row = random.randint(0, self.height - len(word))
                col = random.randint(0, self.width - len(word))

                space_available = all(
                    (
                        not self.cells[r][c].is_answer
                        or (self.cells[r][c].value == word[i] and self.cells[r][c].direction != direction)
                    )
                    for i, (r, c) in enumerate(zip(range(row, row + len(word)), range(col, col + len(word))))
                )
                if space_available:
                    for i, (r, c) in enumerate(zip(range(row, row + len(word)), range(col, col + len(word)))):
                        self.cells[r][c].value = word[i]
                        self.cells[r][c].direction = direction
                        self.cells[r][c].is_answer = True
                    return True
            case 2:
                direction = DirectionEnum.NS
                row = random.randint(0, self.height - len(word))
                col = random.randint(0, self.width - 1)
                space_available = all(
                    (
                        not self.cells[r][col].is_answer
                        or (self.cells[r][col].value == word[i] and self.cells[r][col].direction != direction)
                    )
                    for i, r in enumerate(range(row, row + len(word)))
                )
                if space_available:
                    for i, r in enumerate(range(row, row + len(word))):
                        self.cells[r][col].value = word[i]
                        self.cells[r][col].direction = direction
                        self.cells[r][col].is_answer = True
                    return True
            case 3:
                direction = DirectionEnum.NESW
                row = random.randint(len(word) - 1, self.height - 1)
                col = random.randint(0, self.width - len(word))
                space_available = all(
                    (
                        not self.cells[r][c].is_answer
                        or (self.cells[r][c].value == word[i] and self.cells[r][c].direction != direction)
                    )
                    for i, (r, c) in enumerate(zip(range(row, row - len(word), -1), range(col, col + len(word))))
                )
                if space_available:
                    for i, (r, c) in enumerate(zip(range(row, row - len(word), -1), range(col, col + len(word)))):
                        self.cells[r][c].value = word[i]
                        self.cells[r][c].direction = direction
                        self.cells[r][c].is_answer = True
                    return True
        return False

    def display_board(self):
        for row in self.cells:
            print(" ".join(str(cell) for cell in row))

    def display_solution(self):
        for row in self.cells:
            print(" ".join(cell.direction_to_char() for cell in row))

    def fill_empty_cells(self):
        for row in self.cells:
            for cell in row:
                if not cell.is_answer:
                    cell.value = random.choice(string.ascii_uppercase)
