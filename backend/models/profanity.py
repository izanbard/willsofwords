from pydantic import BaseModel, Field


class ProfanityList(BaseModel):
    word_list: list[str] = Field(
        ..., description="the list of profane words", json_schema_extra={"example": ["badword1", "badword2"]}
    )
