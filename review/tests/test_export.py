from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from review.app.db import get_conn
from review.app.main import app

FAKE_ROWS = [
    {
        "patient_id": "P000001",
        "first_name": "Ada",
        "last_name": "Lovelace",
        "birth_date": "1970-06-15",
        "sex": "F",
        "added_at": "2026-01-10",
    },
]


def test_export_returns_csv():
    app.dependency_overrides[get_conn] = lambda: MagicMock()
    with patch("review.app.export.fetch_members", return_value=FAKE_ROWS) as fetch:
        response = TestClient(app).get("/cohorts/1/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "patient_id" in response.text
    fetch.assert_called_once()
