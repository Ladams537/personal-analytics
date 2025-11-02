# /backend/routers/personal.py
from fastapi import APIRouter, HTTPException
from database import get_db_connection
from psycopg2.extras import DictCursor
import psycopg2

router = APIRouter(
    prefix="/api/principles",
    tags=["Principles"]
)


@router.get("")
def get_all_principles():
    print("\n--- get_all_principles endpoint called ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT principle_id, name, \
                    description FROM principles ORDER BY name;")
        principles_rows = cur.fetchall()
        principles = [dict(row) for row in principles_rows]
        return principles
    except psycopg2.Error as db_error:
        print(f"DB Error: {db_error}")
        raise HTTPException(status_code=500,
                            detail="Database error fetching principles.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
