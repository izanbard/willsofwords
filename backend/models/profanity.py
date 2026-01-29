from pathlib import Path as FilePath

from pydantic import BaseModel, Field
from backend.utils import get_profanity_list


class ProfanityList(BaseModel):
    word_list: list[str] = Field(
        ..., description="the list of profane words", json_schema_extra={"example": ["badword1", "badword2"]}
    )

    def save_profanity_list(self, filename: FilePath):
        self.word_list = sorted(list(set(self.word_list)))
        with open(filename, "w") as fd:
            fd.write("\n".join(self.word_list))
        get_profanity_list.cache_clear()


class ProfanityPatch(BaseModel):
    line: str = Field(..., description="the line number of the profanity", json_schema_extra={"example": "row1"})
    index: int = Field(..., description="the index of the profanity on that line", json_schema_extra={"example": 0})
    state: bool = Field(..., description="the state of the profanity", json_schema_extra={"example": True})
