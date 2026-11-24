import sqlite3

from fastapi import Depends, FastAPI, HTTPException

from .auth import User, require_role
from .db import get_conn
from .export import router as export_router

app = FastAPI(title="Cohort service")
app.include_router(export_router)


@app.get("/cohorts")
def list_cohorts(
    user: User = Depends(require_role("researcher")),
    conn: sqlite3.Connection = Depends(get_conn),
):
    rows = conn.execute("SELECT id, name, created_at FROM cohort ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


@app.get("/cohorts/{cohort_id}/count")
def cohort_count(
    cohort_id: int,
    user: User = Depends(require_role("researcher")),
    conn: sqlite3.Connection = Depends(get_conn),
):
    row = conn.execute("SELECT COUNT(*) AS n FROM cohort_member WHERE cohort_id = ?", (cohort_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Cohort not found")
    return {"cohort_id": cohort_id, "count": row["n"]}
