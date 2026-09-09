import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.feedback import Feedback
from app.core.database import get_db
from app.main import app
from app.models.document import Base, Document


TEST_DATABASE_URL = (
    "postgresql+psycopg://atlasiq_user:"
    "REMOVED_OLD_PASSWORD@localhost/atlasiq_test"
)

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)
@pytest.fixture(autouse=True)
def clean_test_database():
    db = TestingSessionLocal()

    db.query(Feedback).delete()
    db.query(Document).delete()
    
    db.commit()
    db.close()

    yield

    db = TestingSessionLocal()
    db.query(Feedback).delete()
    db.query(Document).delete()
    db.commit()
    db.close()
