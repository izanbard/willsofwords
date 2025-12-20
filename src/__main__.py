from pathlib import Path

from src.models import BookData, Wordlist
from src.utils import Logger
from src.models.config import Config

# with open(Path("testbook_out.json")) as fd:
#     Logger.get_logger().debug("loading previously compiled book from file")
#     book = BookData.model_validate_json(fd.read())

with open(Path("testbook.json")) as fd:
    Logger.get_logger().debug("loading wordlist input")
    wordlist = Wordlist.model_validate_json(fd.read())
Logger.get_logger().debug("creating book data object")
book = BookData(book_title=wordlist.title, wordlist=wordlist)

book.create_puzzles()

for stats in [
    (
        f"{b.puzzle_title}, {len(b.puzzle_word_list)} words out of {len(b.input_word_list)}, "
        f"size {b.width}x{b.height} with a density of {b.density}"
    )
    for b in book.puzzles
]:
    print(stats)

print(book.puzzles[0].profanity)

book.puzzles[0].create_board_image(Config.PIXELS_WIDTH, "puzzle").show()
book.puzzles[0].create_board_image(Config.PIXELS_WIDTH, "solution").show()
