from pathlib import Path
import shutil

from fastapi import UploadFile


UPLOAD_DIRECTORY = Path("storage/documents")


def save_uploaded_file(file: UploadFile) -> Path:
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIRECTORY / file.filename

    with file_path.open("wb") as destination:
        shutil.copyfileobj(file.file, destination)

    return file_path
