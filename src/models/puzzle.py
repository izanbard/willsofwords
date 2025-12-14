import bisect
import random

from .board import Board


class Puzzle:
    def __init__(self, height: int, width: int, target_volume: int) -> None:
        self.height: int = height
        self.width: int = width
        self.target_volume: int = target_volume
        self.board = Board(height, width)
        self.word_list: list[str] = []

    def populate_puzzle(self, master_word_list: list[str]):
        attempts = 0
        while attempts < 10000 and len(self.word_list) < self.target_volume:
            word = random.choice(master_word_list)
            if word in self.word_list:
                continue
            if self.board.place_a_word(word):
                bisect.insort_left(self.word_list, word)
            attempts += 1
        self.board.fill_empty_cells()

    def display_puzzle(self):
        print("The Puzzle")
        self.board.display_board()
        print()
        print("The Solution")
        self.board.display_solution()
        print()
        print("The Word List")
        print(", ".join(self.word_list))
