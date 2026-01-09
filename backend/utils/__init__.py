from pathlib import Path

from .config import Config, AppConfig, PrintConfig, AIConfig, PuzzleConfig  # noqa: F401
from .logging import Logger  # noqa: F401


profanity_list = None
config: Config | None = None


def create_env_file_if_not_exists():
    env_path = Path(".env")
    env_dist_path = Path(".env.dist")
    if not env_path.exists():
        with open(env_dist_path, "r") as ed_fd:
            with open(env_path, "w") as fd:
                fd.write(ed_fd.read())


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
