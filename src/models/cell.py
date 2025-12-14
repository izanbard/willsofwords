from .direction import DirectionEnum


class Cell:
    def __init__(self):
        self._value: str | None = None
        self.is_answer: bool = False
        self._direction: dict[str, bool] = dict.fromkeys(
            [DirectionEnum.NS, DirectionEnum.EW, DirectionEnum.NESW, DirectionEnum.NWSE], False
        )

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value):
        if len(value) != 1:
            raise ValueError("Cell value must be exactly one char")
        self._value = value

    @property
    def direction(self) -> dict[str, bool]:
        return self._direction

    @direction.setter
    def direction(self, key):
        self._direction[key] = True

    def direction_to_char(self) -> str:
        composite_direction = 0
        if self.direction[DirectionEnum.NS]:
            composite_direction += 1
        if self.direction[DirectionEnum.EW]:
            composite_direction += 2
        if self.direction[DirectionEnum.NESW]:
            composite_direction += 4
        if self.direction[DirectionEnum.NWSE]:
            composite_direction += 8
        direction_char_lookup = {
            0: ".",
            1: "|",
            2: "-",
            3: "+",
            4: "/",
            5: "|\u0337",
            6: "\u233f",
            7: "+\u0337",
            8: "\\",
            9: "|\u20e5",
            10: "\u2340",
            11: "",
            12: "X",
            13: "X\u20d2",
            14: "X\u0336",
            15: "*",
        }
        return direction_char_lookup[composite_direction]

    def __str__(self):
        if self.value is not None:
            return self.value
        return self.direction_to_char()
