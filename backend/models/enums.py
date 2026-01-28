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


class BoardImageEnum(StrEnum):
    PUZZLE = "PUZZLE"
    SOLUTION = "SOLUTION"


class LayoutEnum(StrEnum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"


class PageTypeEnum(StrEnum):
    RECTO = "RECTO"
    VERSO = "VERSO"
