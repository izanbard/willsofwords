import json
import string
from pathlib import Path

from .config import Config, AppConfig, AIConfig  # noqa: F401
from .logging import Logger  # noqa: F401


profanity_list = None
dist_file_mapping = {
    "project_settings": (Path("backend/defaults/project_settings.json.dist"), Path("backend/project_settings.json")),
    "profanity": (Path("backend/defaults/profanity.txt.dist"), Path("backend/assets/profanity.txt")),
    "env": (Path(".env.dist"), Path(".env")),
}


def get_logger() -> Logger:
    logger = Logger.get_logger()
    if logger is not None:
        return logger
    raise RuntimeError("Logger not initialised")


def get_profanity_list() -> list[str]:
    global profanity_list
    if profanity_list is None:
        with open(dist_file_mapping["profanity"][1], "r") as fd:
            profanity_list = [
                x.strip().upper().translate({ord(c): None for c in string.whitespace + string.digits + string.punctuation})
                for x in fd.readlines()
            ]
        profanity_list.sort()
    return profanity_list


def save_profanity_list(new_list: list[str]):
    global profanity_list
    profanity_list = sorted(list(set(new_list)))
    with open(dist_file_mapping["profanity"][1], "w") as fd:
        fd.write("\n".join(profanity_list))


def get_project_settings_defaults() -> dict:
    with open(dist_file_mapping["project_settings"][1], "r") as fd:
        return json.load(fd)


def save_project_settings(new_settings: dict, file_path: Path = dist_file_mapping["project_settings"][1]):
    with open(file_path, "w") as fd:
        json.dump(new_settings, fd, indent=2)


def _creat_dist_file_if_not_exists(dist_path: Path, target_path: Path):
    if not target_path.exists():
        with open(dist_path, "r") as fd:
            with open(target_path, "w") as tfd:
                tfd.write(fd.read())


def create_default_files():
    for path_pair in dist_file_mapping.values():
        _creat_dist_file_if_not_exists(dist_path=path_pair[0], target_path=path_pair[1])
    conf = get_project_settings_defaults()
    data_dir = Path(conf["app"]["data_folder"])
    data_dir.mkdir(parents=True, exist_ok=True)
    archives_dir = Path(conf["app"]["archive_folder"])
    archives_dir.mkdir(parents=True, exist_ok=True)
