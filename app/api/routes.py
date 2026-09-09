from app.services.metrics_service import (
    get_feedback_metrics,
    get_query_metrics,
)
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate
from app.schemas.ask import AskRequest
from app.services.rag_service import answer_question
from pathlib import Path
from app.services.chunking_service import chunk_text, save_chunks
from app.services.document_service import extract_text, save_uploaded_file
from app.schemas.document import DocumentCreate, DocumentUpdate
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document import Document

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }

@router.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()

    return documents

@router.post("/documents", status_code=201)
def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
):
    document = Document(
        filename=document_data.filename,
        file_type=document_data.file_type,
        team=document_data.team,
        storage_path=document_data.storage_path,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document

@router.get("/documents/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document
@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }

@router.put("/documents/{document_id}")
def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    document.filename = document_data.filename
    document.file_type = document_data.file_type
    document.team = document_data.team
    document.storage_path = document_data.storage_path

    db.commit()
    db.refresh(document)

    return document

@router.post("/documents/upload", status_code=201)
def upload_document(
    team: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    allowed_types = {"pdf", "docx", "txt"}
    file_type = file.filename.rsplit(".", 1)[-1].lower()
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )
    MAX_FILE_SIZE = 10 * 1024 * 1024
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
           status_code=413,
            detail="File too large. Maximum size is 10 MB.",
        )
    file_path = save_uploaded_file(file)

    document = Document(
        filename=file.filename,
        file_type=file_type,
        team=team,
        storage_path=str(file_path),
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)

        text = extract_text(Path(file_path))
        chunks = chunk_text(text)

        save_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
        )

        db.refresh(document)
        return document

    except Exception:
        db.rollback()

        if document.id is not None:
            existing_document = db.get(Document, document.id)
            if existing_document is not None:
                db.delete(existing_document)
                db.commit()

        if file_path.exists():
            file_path.unlink()

        raise

@router.post("/ask")
def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db),
):
    return answer_question(
        db=db,
        question=request.question,
        team=request.team,
    )
@router.post("/feedback", status_code=201)
def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
):
    feedback = Feedback(
        question=feedback_data.question,
        answer=feedback_data.answer,
        team=feedback_data.team,
        rating=feedback_data.rating,
        correction=feedback_data.correction,
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback
@router.get("/metrics/feedback")
def feedback_metrics(
    team: str | None = None,
    db: Session = Depends(get_db),
):
    return get_feedback_metrics(
        db=db,
        team=team,
    )
@router.get("/metrics/queries")
def query_metrics(
    team: str | None = None,
    db: Session = Depends(get_db),
):
    return get_query_metrics(
        db=db,
        team=team,
    )
