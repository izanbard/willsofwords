from .logging import Logger  # noqa: F401

profanity_list = None


def get_profanity_list():
    global profanity_list
    if profanity_list is None:
        with open("backend/assets/profanity.txt", "r") as fd:
            profanity_list = [x.strip() for x in fd.readlines()]
    return profanity_list
