import sys
from pathlib import Path

from backend.models import PuzzleData, Wordlist  # noqa: F401
from backend.pages import Pages, PrintParams
from backend.utils import Logger, Config, get_config, AppConfig, PuzzleConfig


def create_env_file_if_not_exists():
    env_path = Path(".env")
    env_dist_path = Path(".env.dist")
    if not env_path.exists():
        with open(env_dist_path, "r") as ed_fd:
            with open(env_path, "w") as fd:
                fd.write(ed_fd.read())


def fix_puzzle_config(config: Config):
    if config.puzzle.max_columns == 0:
        print_params = PrintParams()
        config.puzzle.calculate_column_count(print_params.grid_width, print_params.min_cell_size)
    if config.puzzle.max_rows == 0:
        print_params = PrintParams()
        config.puzzle.calculate_max_row_count(print_params.grid_height_two_page, print_params.min_cell_size)
    if config.puzzle.medium_rows == 0:
        print_params = PrintParams()
        config.puzzle.calculate_medium_row_count(print_params.grid_height, print_params.min_cell_size)


def initialise():
    create_env_file_if_not_exists()
    config = get_config()
    fix_puzzle_config(config)
    Logger(config.app)
    return config


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


def main():
    allowed_commands = [
        "validate_wordlist",
        "wordlist_to_data",
        "data_to_pdf",
        "wordlist_to_data_to_pdf",
        "data_show_profanity",
    ]

    config = initialise()
    if config.app.command not in allowed_commands:
        Logger.get_logger().error(f"Invalid command: {config.command}")
        return 1
    match config.app.command:
        case "validate_wordlist":
            load_and_validate_wordlist(config.app)
        case "wordlist_to_data":
            wordlist = load_and_validate_wordlist(config.app)
            if not config.puzzle.enable_profanity_filter:
                Logger.get_logger().warn("Profanity filter is off, seriously?")
            word_search = create_word_search_data_model(config.app, config.puzzle, wordlist)
            word_search.save_data(Path(config.app.data_filename))
        case "data_to_pdf":
            word_search = load_and_validate_word_search_data(config.app)
            pages = create_pdf_from_data(config.app, word_search)
            if config.print.debug:
                Logger.get_logger().warn("PDF output has printing guides on it - NOT SUITABLE FOR PRODUCTION")
            pages.save_pdf()
        case "wordlist_to_data_to_pdf":
            wordlist = load_and_validate_wordlist(config.app)
            if not config.puzzle.enable_profanity_filter:
                Logger.get_logger().warn("Profanity filter is off, seriously?")
            word_search = create_word_search_data_model(config.app, config.puzzle, wordlist)
            word_search.save_data(Path(config.app.data_filename))
            pages = create_pdf_from_data(config.app, word_search)
            if config.print.debug:
                Logger.get_logger().warn("PDF output has printing guides on it - NOT SUITABLE FOR PRODUCTION")
            pages.save_pdf()
        case "data_show_profanity":
            word_search = load_and_validate_word_search_data(config.app)
            for puzzle in word_search.puzzles:
                Logger.get_logger().info(f"{puzzle.display_title} has {len(puzzle.profanity)} profanity words")
                for row, wordlist in puzzle.profanity.items():
                    Logger.get_logger().warn(f"Profanity in: {row} - {wordlist}")
        case _:
            Logger.get_logger().error(f"Invalid command: {config.app.command}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
