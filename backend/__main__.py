from pathlib import Path

from backend.models import BookData, Wordlist  # noqa: F401
from backend.models.config import Config
from backend.pages import Pages
from backend.utils import Logger


with open(Path("testbook_out.json")) as fd:
    Logger.get_logger().info("loading previously compiled book from file")
    book = BookData.model_validate_json(fd.read())

# with open(Path("testbook.json")) as fd:
#     Logger.get_logger().debug("loading wordlist input")
#     wordlist = Wordlist.model_validate_json(fd.read())
# Logger.get_logger().debug("creating book data object")
# book = BookData(book_title=wordlist.title, wordlist=wordlist)
# book.create_puzzles()
# book.save_data(Path("testbook_out.json"))

pages = Pages(book=book, filename=Path("testbook.pdf"))
pages.create_pages()
pages.save_pdf()


if not Config.PUZZLE_ENABLE_PROFANITY_FILTER:
    Logger.get_logger().warn("Profanity filter is off, seriously?")
if Config.PRINT_DEBUG:
    Logger.get_logger().warn("PDF output has printing guides on it - NOT SUITABLE FOR PRODUCTION")
