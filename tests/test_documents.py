from app.models.chunk import Chunk
from tests.conftest import TestingSessionLocal
from pathlib import Path
from app.services.document_service import extract_text
from tests.conftest import client


def test_create_document():
    response = client.post(
        "/documents",
        json={
            "filename": "test_manual.pdf",
            "file_type": "pdf",
            "team": "engineering",
            "storage_path": "/documents/test_manual.pdf",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["filename"] == "test_manual.pdf"
    assert data["file_type"] == "pdf"
    assert data["team"] == "engineering"
    assert data["storage_path"] == "/documents/test_manual.pdf"
    assert "id" in data

def test_get_documents():
    client.post(
        "/documents",
        json={
            "filename": "list_test.pdf",
            "file_type": "pdf",
            "team": "engineering",
            "storage_path": "/documents/list_test.pdf",
        },
    )

    response = client.get("/documents")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["filename"] == "list_test.pdf"
def test_get_document_by_id():
    create_response = client.post(
        "/documents",
        json={
            "filename": "single_document.pdf",
            "file_type": "pdf",
            "team": "support",
            "storage_path": "/documents/single_document.pdf",
        },
    )

    document_id = create_response.json()["id"]

    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == document_id
    assert data["filename"] == "single_document.pdf"
    assert data["team"] == "support"

def test_update_document():
    create_response = client.post(
        "/documents",
        json={
            "filename": "old_name.pdf",
            "file_type": "pdf",
            "team": "support",
            "storage_path": "/documents/old_name.pdf",
        },
    )

    document_id = create_response.json()["id"]

    response = client.put(
        f"/documents/{document_id}",
        json={
            "filename": "new_name.pdf",
            "file_type": "pdf",
            "team": "engineering",
            "storage_path": "/documents/new_name.pdf",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == document_id
    assert data["filename"] == "new_name.pdf"
    assert data["team"] == "engineering"
    assert data["storage_path"] == "/documents/new_name.pdf"

def test_delete_document():
    create_response = client.post(
        "/documents",
        json={
            "filename": "delete_me.pdf",
            "file_type": "pdf",
            "team": "support",
            "storage_path": "/documents/delete_me.pdf",
        },
    )

    document_id = create_response.json()["id"]

    response = client.delete(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }

    get_response = client.get(f"/documents/{document_id}")

    assert get_response.status_code == 404
def test_document_not_found():
    response = client.get("/documents/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found"
    }
def test_upload_document():
    response = client.post(
        "/documents/upload",
        data={
            "team": "engineering",
        },
        files={
            "file": (
                "upload_test.txt",
                b"AtlasIQ upload test content",
                "text/plain",
            ),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["filename"] == "upload_test.txt"
    assert data["file_type"] == "txt"
    assert data["team"] == "engineering"
    assert "id" in data
def test_upload_rejects_unsupported_file():
    response = client.post(
        "/documents/upload",
        data={
            "team": "engineering",
        },
        files={
            "file": (
                "malware.exe",
                b"fake executable content",
                "application/octet-stream",
            ),
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unsupported file type"
    }
def test_extract_text_from_txt(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text(
        "AtlasIQ extraction test",
        encoding="utf-8",
    )

    text = extract_text(file_path)

    assert text == "AtlasIQ extraction test"
def test_extract_text_from_docx(tmp_path):
    from docx import Document as DocxDocument

    file_path = tmp_path / "test.docx"

    document = DocxDocument()
    document.add_paragraph("AtlasIQ DOCX extraction test")
    document.save(file_path)

    text = extract_text(file_path)

    assert text == "AtlasIQ DOCX extraction test"
def test_extract_text_from_pdf(tmp_path):
    from reportlab.pdfgen import canvas

    file_path = tmp_path / "test.pdf"

    pdf = canvas.Canvas(str(file_path))
    pdf.drawString(100, 750, "AtlasIQ PDF extraction test")
    pdf.save()

    text = extract_text(file_path)

    assert "AtlasIQ PDF extraction test" in text
def test_upload_creates_chunks():
    content = ("AtlasIQ engineering knowledge base. " * 120).encode()

    response = client.post(
        "/documents/upload",
        data={
            "team": "engineering",
        },
        files={
            "file": (
                "ingestion_test.txt",
                content,
                "text/plain",
            ),
        },
    )

    assert response.status_code == 201

    document_id = response.json()["id"]

    db = TestingSessionLocal()

    try:
        chunks = (
            db.query(Chunk)
            .filter(Chunk.document_id == document_id)
            .all()
        )

        assert len(chunks) > 1
        assert chunks[0].chunk_index == 0
        assert chunks[0].content
    finally:
        db.close()
def test_upload_rejects_legacy_doc_file():
    response = client.post(
        "/documents/upload",
        data={
            "team": "engineering",
        },
        files={
            "file": (
                "legacy_document.doc",
                b"fake legacy doc content",
                "application/msword",
            ),
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported file type"
def test_duplicate_filenames_get_unique_storage_paths():
    first = client.post(
        "/documents/upload",
        data={"team": "engineering"},
        files={
            "file": (
                "policy.txt",
                b"First policy document.",
                "text/plain",
            )
        },
    )

    second = client.post(
        "/documents/upload",
        data={"team": "engineering"},
        files={
            "file": (
                "policy.txt",
                b"Second policy document.",
                "text/plain",
            )
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    first_data = first.json()
    second_data = second.json()

    assert first_data["filename"] == "policy.txt"
    assert second_data["filename"] == "policy.txt"

    assert (
        first_data["storage_path"]
        != second_data["storage_path"]
    )
