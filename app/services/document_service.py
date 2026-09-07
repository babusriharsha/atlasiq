from docx import Document as DocxDocument
from pypdf import PdfReader
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

def extract_text_from_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def extract_text_from_docx(file_path: Path) -> str:
    document = DocxDocument(file_path)

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def extract_text(file_path: Path) -> str:
    extension = file_path.suffix.lower()

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    raise ValueError(f"Text extraction not supported for {extension}")
