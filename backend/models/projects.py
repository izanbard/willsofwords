from datetime import datetime

from pydantic import BaseModel, computed_field

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
    name: str
    settings: ProjectConfigUpdate
