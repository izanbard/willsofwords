from pathlib import Path as FilePath

from pydantic import BaseModel, Field


class ProfanityList(BaseModel):
    word_list: list[str] = Field(
        ..., description="the list of profane words", json_schema_extra={"example": ["badword1", "badword2"]}
    )

    def save_profanity_list(self, filename: FilePath):
        self.word_list = sorted(list(set(self.word_list)))
        with open(filename, "w") as fd:
            fd.write("\n".join(self.word_list))
