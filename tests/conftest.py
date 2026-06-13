import pytest

import database


@pytest.fixture(autouse=True)
def test_db(tmp_path):
    """
    Override database.DB_PATH with a temporary SQLite database for tests.
    Ensures tests are run in total isolation and do not affect production data.
    """
    original_db_path = database.DB_PATH
    test_db_path = tmp_path / "test_kakeibo.db"
    database.DB_PATH = test_db_path

    # Initialize the test database schema
    database.init_db()

    yield

    # Restore the original database path
    database.DB_PATH = original_db_path
