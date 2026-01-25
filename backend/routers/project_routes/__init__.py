from datetime import datetime
from pathlib import Path as FilePath

from backend.models import ProjectFolder, ProjectFile


def get_project_files(data_dir: FilePath) -> ProjectFolder:
    """Retrieve project files from a directory and return a ProjectFolder object.

    Args:
        data_dir (FilePath): The directory containing project files.

    Returns:
        ProjectFolder: A ProjectFolder object representing the project files.
    """
    project_files = [
        ProjectFile(name=file.name, modified_date=datetime.fromtimestamp(file.stat().st_mtime))
        for file in data_dir.iterdir()
        if file.is_file()
    ]
    project_files.sort(key=lambda x: x.name.lower())
    project_folder = ProjectFolder(name=data_dir.name, project_files=project_files)
    return project_folder
