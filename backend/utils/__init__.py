from .config import Config, AppConfig, PrintConfig, AIConfig, PuzzleConfig  # noqa: F401
from .logging import Logger  # noqa: F401


profanity_list = None
config: Config | None = None


def get_profanity_list():
    global profanity_list
    if profanity_list is None:
        with open("backend/assets/profanity.txt", "r") as fd:
            profanity_list = [x.strip() for x in fd.readlines()]
    return profanity_list


def get_config():
    global config
    if config is None:
        config = Config()
    return config


def get_print_config():
    return get_config().print


def get_ai_config():
    return get_config().ai


def get_puzzle_config():
    return get_config().puzzle
