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


class Size:
    def __init__(self, size: SizeEnum):
        self.size = size

    def downsize(self):
        match self.size:
            case SizeEnum.LARGE:
                self.size = SizeEnum.MEDIUM
            case SizeEnum.MEDIUM:
                self.size = SizeEnum.SMALL
            case SizeEnum.SMALL:
                raise ValueError("cannot downsize any more")

    def upsize(self):
        match self.size:
            case SizeEnum.LARGE:
                raise ValueError("cannot upsize any more")
            case SizeEnum.MEDIUM:
                self.size = SizeEnum.LARGE
            case SizeEnum.SMALL:
                self.size = SizeEnum.MEDIUM
