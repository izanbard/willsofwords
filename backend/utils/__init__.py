import string
from functools import lru_cache
from pathlib import Path as FilePath

from .config import AIConfig, AppConfig, Config  # noqa: F401
from .logging import Logger  # noqa: F401

dist_file_mapping = {
    "project_settings": (FilePath("backend/defaults/project_settings.json.dist"), FilePath("backend/project_settings.json")),
    "profanity": (FilePath("backend/defaults/profanity.txt.dist"), FilePath("backend/assets/profanity.txt")),
    "env": (FilePath(".env.dist"), FilePath(".env")),
}


def get_logger() -> Logger:
    logger = Logger.get_logger()
    if logger is not None:
        return logger
    raise RuntimeError("Logger not initialised")


@lru_cache(maxsize=1)
def get_profanity_list() -> list[str]:
    with open(dist_file_mapping["profanity"][1], "r") as fd:
        profanity_list = [
            x.strip().upper().translate({ord(c): None for c in string.whitespace + string.digits + string.punctuation})
            for x in fd.readlines()
        ]
    profanity_list.sort()
    return profanity_list


def _creat_dist_file_if_not_exists(dist_path: FilePath, target_path: FilePath):
    if not target_path.exists():
        with open(dist_path, "r") as fd:
            with open(target_path, "w") as tfd:
                tfd.write(fd.read())


def create_default_files():
    for path_pair in dist_file_mapping.values():
        _creat_dist_file_if_not_exists(dist_path=path_pair[0], target_path=path_pair[1])
    conf = Config()
    data_dir = FilePath(conf.app.data_folder)
    data_dir.mkdir(parents=True, exist_ok=True)
    archives_dir = FilePath(conf.app.archive_folder)
    archives_dir.mkdir(parents=True, exist_ok=True)


def set_marker_file(filename: FilePath, percentage: int):
    clear_marker_file(filename)
    (filename.parent / f"{filename.name}.{percentage:02d}.marker").touch()


def clear_marker_file(filename: FilePath):
    for p in filename.parent.glob(f"{filename.name}.*.marker"):
        p.unlink()
