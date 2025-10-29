#/backend/routers/dashboard.py

from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
import psycopg2
from psycopg2.extras import DictCursor
from schemas import CheckinCreate
from core.config import pwd_context
from auth import get_current_user
import uuid


router = APIRouter(
    prefix="/api", # Optional: Define prefix for all routes in this file
    tags=[""]       # Optional: Tag for API docs
)


@router.get("/principles")
def get_all_principles():
    print("\n--- get_all_principles endpoint called ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT principle_id, name, description FROM principles ORDER BY name;")
        principles_rows = cur.fetchall()
        principles = [dict(row) for row in principles_rows]
        return principles
    except psycopg2.Error as db_error:
        print(f"DB Error: {db_error}")
        raise HTTPException(status_code=500, detail="Database error fetching principles.")
    finally:
        if cur: cur.close()
        if conn: conn.close()


@router.get("") 
# Add dependency to get user ID from token
async def get_dashboard_data(current_user_id: uuid.UUID = Depends(get_current_user)):
    # Use current_user_id obtained from the token
    print(f"\n--- 1. get_dashboard_data called for user: {current_user_id} ---")
    conn = None
    cur = None
    # ... (rest of the function is the same, just use current_user_id in SQL queries) ...
    dashboard_data = {
        "latest_checkin": None,
        "top_goal": None,
        "daily_metrics": []
    }
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        # --- Fetch latest check-in using current_user_id ---
        checkin_sql = """
            SELECT checkin_id, checkin_date, gratitude_entry, principle_alignment, principle_alignment_note
            FROM daily_checkins
            WHERE user_id = %s
            ORDER BY checkin_date DESC, created_at DESC
            LIMIT 1;
        """
        cur.execute(checkin_sql, (current_user_id,)) # Use current_user_id
        latest_checkin = cur.fetchone()

        if latest_checkin:
            # ... (rest of the check-in and metrics logic using current_user_id) ...
             dashboard_data["latest_checkin"] = dict(latest_checkin)
             latest_checkin_id = latest_checkin["checkin_id"]

             metrics_sql = """
                 SELECT metric_type, metric_name, value
                 FROM daily_metrics
                 WHERE checkin_id = %s;
             """
             cur.execute(metrics_sql, (latest_checkin_id,))
             metrics_rows = cur.fetchall()
             dashboard_data["daily_metrics"] = [dict(row) for row in metrics_rows]

             # --- Fetch top goal using current_user_id ---
             target_date = latest_checkin["checkin_date"]
             goal_sql = """
                 SELECT goal_description, is_completed
                 FROM top_goal
                 WHERE user_id = %s AND goal_date = %s;
             """
             cur.execute(goal_sql, (current_user_id, target_date)) # Use current_user_id
             top_goal = cur.fetchone()
             if top_goal:
                 dashboard_data["top_goal"] = dict(top_goal)

        return dashboard_data

    except psycopg2.Error as db_error:
        print("\n--- !!! DATABASE ERROR !!! ---")
        print(f"DB Error: {db_error}")
        raise HTTPException(status_code=500, detail="Database error occurred.")

    except Exception as e:
        print("\n--- !!! UNEXPECTED ERROR !!! ---")
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected server error occurred.")

    finally:
        if cur: cur.close()
        if conn: conn.close()
        print("--- Connection closed ---")