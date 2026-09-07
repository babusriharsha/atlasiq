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
    response = client.get("/documents")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

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
