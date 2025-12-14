from src.models.puzzle import Puzzle


words = ["ADVENTURE", "DESTINATION", "PASSPORT", "EXPLORE", "TOURIST", "JOURNEY", "FLIGHT", "CRUISE", "LUGGAGE", "TICKET"]
my_puzzle = Puzzle(13, 13, 10)
my_puzzle.populate_puzzle(words)
my_puzzle.display_puzzle()
