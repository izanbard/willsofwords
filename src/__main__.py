from pathlib import Path

from src.models import BookData, Wordlist
from src.utils import Logger


# with open(Path("testbook_out.json")) as fd:
#     Logger.get_logger().debug("loading previously compiled book from file")
#     book = BookData.model_validate_json(fd.read())

with open(Path("testbook.json")) as fd:
    Logger.get_logger().debug("loading wordlist input")
    wordlist = Wordlist.model_validate_json(fd.read())
Logger.get_logger().debug("creating book data object")
book = BookData(book_title=wordlist.title, wordlist=wordlist)

book.create_puzzles()
book.save_data(Path("testbook_out.json"))
book.create_pages(Path("testbook_pages.pdf"))
