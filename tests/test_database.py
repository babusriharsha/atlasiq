import importlib

import pytest

from app.core import database


def test_get_db_yields_and_closes_session(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    fake_session = FakeSession()

    monkeypatch.setattr(
        database,
        "SessionLocal",
        lambda: fake_session,
    )

    generator = database.get_db()
    yielded_session = next(generator)

    assert yielded_session is fake_session

    with pytest.raises(StopIteration):
        next(generator)

    assert fake_session.closed is True


def test_database_requires_database_url(monkeypatch):
    import os
    import dotenv

    original_url = os.environ.get("DATABASE_URL")

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(
        dotenv,
        "load_dotenv",
        lambda: None,
    )

    try:
        with pytest.raises(
            RuntimeError,
            match="DATABASE_URL environment variable is not configured",
        ):
            importlib.reload(database)
    finally:
        if original_url is not None:
            os.environ["DATABASE_URL"] = original_url

        importlib.reload(database)
