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
    allowed_types = {"pdf", "doc", "docx", "txt"}
    file_type = file.filename.rsplit(".", 1)[-1].lower()
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )
    file_path = save_uploaded_file(file)

    document = Document(
        filename=file.filename,
        file_type=file_type,
        team=team,
        storage_path=str(file_path),
    )

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
