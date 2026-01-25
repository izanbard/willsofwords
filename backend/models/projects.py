from datetime import datetime

from pydantic import BaseModel, computed_field, Field

from .project_config import ProjectConfigUpdate


class ProjectFile(BaseModel):
    name: str
    modified_date: datetime


class ProjectFolder(BaseModel):
    name: str
    project_files: list[ProjectFile]


class ProjectsList(BaseModel):
    projects: list[ProjectFolder]

    @computed_field
    def projects_count(self) -> int:
        """Returns the total number of projects in the list."""
        return len(self.projects)


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")
    settings: ProjectConfigUpdate
