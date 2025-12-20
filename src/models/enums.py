from enum import StrEnum


class DirectionEnum(StrEnum):
    NS = "NS"
    EW = "EW"
    NESW = "NESW"
    NWSE = "NWSE"


class SizeEnum(StrEnum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
