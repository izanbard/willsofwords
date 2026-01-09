from pathlib import Path

from backend.models import PuzzleData, Wordlist
from backend.pages import Pages
from backend.utils import Logger, Config, AppConfig, PuzzleConfig, PrintConfig


def load_and_validate_wordlist(app_config: AppConfig):
    with open(Path(app_config.input_filename)) as fd:
        Logger.get_logger().info("loading the wordlist from file")
        wordlist = Wordlist.model_validate_json(fd.read())
        wordlist.validate_word_lists()
    return wordlist


def create_word_search_data_model(app_config: AppConfig, puzzle_config: PuzzleConfig, wordlist: Wordlist):
    Logger.get_logger().debug(
        f"Creating word search data object with title '{wordlist.title}' and {len(wordlist.category_list)} categories"
    )
    wordsearch = PuzzleData(puzzle_config=puzzle_config, book_title=wordlist.title, wordlist=wordlist)
    wordsearch.create_puzzles()
    wordsearch.save_data(Path(app_config.data_filename))
    return wordsearch


def load_and_validate_word_search_data(app_config: AppConfig):
    with open(Path(app_config.data_filename)) as fd:
        Logger.get_logger().info("loading previously compiled book from file")
        word_search = PuzzleData.model_validate_json(fd.read())
    return word_search


def create_pdf_from_data(
    app_config: AppConfig,
    words_search_data: PuzzleData,
):
    pages = Pages(word_search_data=words_search_data, filename=Path(app_config.output_filename))
    pages.create_pages()
    return pages


def emit_global_warnings(config: Config):
    if not config.puzzle.enable_profanity_filter:
        Logger.get_logger().warn("Profanity filter is off, seriously?")
    if config.print.debug:
        Logger.get_logger().warn("PDF output has printing guides on it - NOT SUITABLE FOR PRODUCTION")


def execute_command(app_settings: AppConfig, puzzle_settings: PuzzleConfig, print_settings: PrintConfig, command: str = ""):
    match command:
        case "validate_wordlist":
            load_and_validate_wordlist(app_settings)
        case "wordlist_to_data":
            wordlist = load_and_validate_wordlist(app_settings)
            if not puzzle_settings.enable_profanity_filter:
                Logger.get_logger().warn("Profanity filter is off, seriously?")
            word_search = create_word_search_data_model(app_settings, puzzle_settings, wordlist)
            word_search.save_data(Path(app_settings.data_filename))
        case "data_to_pdf":
            word_search = load_and_validate_word_search_data(app_settings)
            pages = create_pdf_from_data(app_settings, word_search)
            if print_settings.debug:
                Logger.get_logger().warn("PDF output has printing guides on it - NOT SUITABLE FOR PRODUCTION")
            pages.save_pdf()
        case "wordlist_to_data_to_pdf":
            wordlist = load_and_validate_wordlist(app_settings)
            if not puzzle_settings.enable_profanity_filter:
                Logger.get_logger().warn("Profanity filter is off, seriously?")
            word_search = create_word_search_data_model(app_settings, puzzle_settings, wordlist)
            word_search.save_data(Path(app_settings.data_filename))
            pages = create_pdf_from_data(app_settings, word_search)
            if print_settings.debug:
                Logger.get_logger().warn("PDF output has printing guides on it - NOT SUITABLE FOR PRODUCTION")
            pages.save_pdf()
        case "data_show_profanity":
            word_search = load_and_validate_word_search_data(app_settings)
            for puzzle in word_search.puzzles:
                Logger.get_logger().info(f"{puzzle.display_title} has {len(puzzle.profanity)} profanity words")
                for row, wordlist in puzzle.profanity.items():
                    Logger.get_logger().warn(f"Profanity in: {row} - {wordlist}")
        case _:
            Logger.get_logger().error(f"Invalid command: {command}")
            return 1
    return 0
