"""Cohort CSV export.

Provides an endpoint that exports all members of a cohort as a CSV file,
so researchers can analyze a cohort in Excel or other tools.
"""
import csv
import io
import logging
import sqlite3
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from .db import get_conn

logger = logging.getLogger(__name__)

router = APIRouter()

EXPORT_COLUMNS = ["patient_id", "first_name", "last_name", "birth_date", "age", "sex", "added_at"]


def calculate_age(birth_date: str) -> int:
    """Calculate a patient's current age in years."""
    born = date.fromisoformat(birth_date)
    return date.today().year - born.year


def fetch_members(conn: sqlite3.Connection, cohort_id: int, sort_by: str, order: str) -> list[sqlite3.Row]:
    """Fetch all members of a cohort, joined with their patient details."""
    query = f"""
        SELECT p.patient_id, p.first_name, p.last_name, p.birth_date, p.sex, m.added_at
        FROM cohort_member m
        JOIN patient p ON p.patient_id = m.patient_id
        WHERE m.cohort_id = ?
        ORDER BY {sort_by} {order}
    """
    return conn.execute(query, (cohort_id,)).fetchall()


def build_csv(rows: list[sqlite3.Row]) -> str:
    """Convert member rows into CSV text with a header row."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(EXPORT_COLUMNS)
    for row in rows:
        writer.writerow(
            [
                row["patient_id"],
                row["first_name"],
                row["last_name"],
                row["birth_date"],
                calculate_age(row["birth_date"]),
                row["sex"],
                row["added_at"],
            ]
        )
    return buffer.getvalue()


@router.get("/cohorts/{cohort_id}/export")
def export_cohort(
    cohort_id: int,
    sort_by: str = Query("p.last_name", description="Column to sort by: p.last_name, p.birth_date or m.added_at"),
    order: str = Query("asc", description="Sort order: asc or desc"),
    conn: sqlite3.Connection = Depends(get_conn),
):
    """Export every member of a cohort as a downloadable CSV file.

    Uses a StreamingResponse so that large cohorts are sent efficiently.
    """
    try:
        rows = fetch_members(conn, cohort_id, sort_by, order)
        content = build_csv(rows)
    except Exception:
        logger.exception("Cohort export failed")
        content = ",".join(EXPORT_COLUMNS) + "\n"

    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="cohort_{cohort_id}.csv"'},
    )
