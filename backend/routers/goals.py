#API calls for handling the goals of the user
#/backend/routers/goals.py

import uuid
import psycopg2
from fastapi import HTTPException
from datetime import date
from fastapi import Depends
from database import get_db_connection
from schemas import TopGoalUpdate
from fastapi import APIRouter
from auth import get_current_user

router = APIRouter(
    prefix="/api/goals", # Optional: Define prefix for all routes in this file
    tags=["Goals"]       # Optional: Tag for API docs
)

@router.patch("/today")
async def update_todays_top_goal(
    update_data: TopGoalUpdate, # Get the new status from the request body
    current_user_id: uuid.UUID = Depends(get_current_user) # Get user from token
):
    print(f"\n--- 1. update_todays_top_goal called for user: {current_user_id} ---")
    today = date.today()
    conn = None
    cur = None
    try:
        print("--- 2. Attempting DB connection ---")
        conn = get_db_connection()
        cur = conn.cursor()
        print("--- 3. DB connection successful ---")

        update_sql = """
            UPDATE top_goal
            SET is_completed = %s
            WHERE user_id = %s AND goal_date = %s
            RETURNING goal_id; -- Return the ID to confirm update happened
        """
        print(f"--- 4. Executing update for date {today}, status {update_data.is_completed} ---")
        cur.execute(update_sql, (update_data.is_completed, current_user_id, today))

        updated_goal = cur.fetchone() # Check if any row was updated

        if updated_goal:
            conn.commit()
            print("--- Update committed ---")
            return {"status": "success", "message": "Top goal status updated."}
        else:
            # No goal found for today, maybe rollback isn't needed but good practice
            if conn: conn.rollback()
            print("--- No top goal found for today to update ---")
            raise HTTPException(status_code=404, detail="No top goal found for today.")

    except psycopg2.Error as db_error:
        print(f"DB Error: {db_error}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="Database error updating goal.")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="An unexpected server error occurred.")
    finally:
        if cur: cur.close()
        if conn: conn.close()
        print("--- Connection closed ---")
