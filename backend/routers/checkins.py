# /backend/routers/checkins.py

import uuid
import psycopg2
from psycopg2.extras import DictCursor
from fastapi import HTTPException
from datetime import date
from fastapi import Depends
from database import get_db_connection
from fastapi import APIRouter
from auth import get_current_user
from schemas import CheckinCreate


router = APIRouter(
    prefix="/api/checkins",
    tags=["Checkins"]
)


@router.get("/today")
async def get_todays_checkin(current_user_id: uuid.UUID =
                             Depends(get_current_user)):
    print(f"\n--- 1. get_todays_checkin called for user: \
          {current_user_id} ---")
    today = date.today()
    conn = None
    cur = None
    try:
        print("--- 2. Attempting DB connection ---")
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        print("--- 3. DB connection successful ---")

        checkin_sql = """
            SELECT checkin_id, checkin_date, gratitude_entry,
                   principle_alignment, principle_alignment_note
            FROM daily_checkins
            WHERE user_id = %s AND checkin_date = %s;
        """
        cur.execute(checkin_sql, (current_user_id, today))
        checkin_data = cur.fetchone()

        if not checkin_data:
            print(f"--- No check-in found for user \
                  {current_user_id} on {today} ---")
            raise HTTPException(status_code=404,
                                detail="No check-in found for today.")

        checkin_id = checkin_data["checkin_id"]
        print(f"--- Found check-in for today (ID: {checkin_id}) ---")

        metrics_sql = """
            SELECT metric_type, metric_name, value
            FROM daily_metrics WHERE checkin_id = %s;
        """
        cur.execute(metrics_sql, (checkin_id,))
        metrics_rows = cur.fetchall()
        metrics = [dict(row) for row in metrics_rows]
        print(f"--- Found {len(metrics)} metrics ---")

        goal_sql = """
            SELECT goal_description, is_completed
            FROM top_goal WHERE user_id = %s AND goal_date = %s;
        """
        cur.execute(goal_sql, (current_user_id, today))
        top_goal_row = cur.fetchone()
        top_goal = dict(top_goal_row) if top_goal_row else None
        print(f"--- Found top goal: {bool(top_goal)} ---")

        print(f"--- 4e. Fetching completed steps for check-in \
              {checkin_id} ---")
        steps_sql = """
             SELECT cs.step_id, \
             rs.step_name, \
             cs.is_completed, \
             cs.actual_duration \
             FROM completed_steps cs \
             JOIN routine_steps rs ON cs.step_id = rs.step_id \
             WHERE cs.checkin_id = %s \
             ORDER BY rs.step_order;
        """
        cur.execute(steps_sql, (checkin_id,))
        completed_steps_rows = cur.fetchall()
        completed_steps = [dict(row) for row in completed_steps_rows]
        print(f"--- Found {len(completed_steps)} completed steps ---")

        full_checkin_details = {
            **dict(checkin_data),
            "metrics": metrics,
            "top_goal": top_goal,
            "completed_steps": completed_steps
        }

        return full_checkin_details

    except HTTPException as e:
        raise e
    except psycopg2.Error as db_error:
        print(f"DB Error: {db_error}")
        raise HTTPException(status_code=500,
                            detail="Database error fetching today's check-in.")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500,
                            detail="An unexpected server error occurred.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("--- Connection closed ---")


@router.post("")
async def create_checkin(checkin_data: CheckinCreate,
                         current_user_id: uuid.UUID =
                         Depends(get_current_user)):
    print("\n--- 1. create_checkin endpoint called ---")
    print(f"   - User ID from token: {current_user_id}")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        checkin_sql = """
            INSERT INTO daily_checkins
            (checkin_id, user_id, checkin_date, gratitude_entry,
                principle_alignment, principle_alignment_note)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING checkin_id;
        """
        checkin_id = uuid.uuid4()
        cur.execute(checkin_sql, (
            checkin_id,
            current_user_id,
            checkin_data.checkin_date,
            checkin_data.gratitude_entry,
            checkin_data.principle_alignment,
            checkin_data.principle_alignment_note
        ))
        print(f"--- daily_checkins insert successful for ID: {checkin_id} ---")

        if checkin_data.metrics:
            print("--- 4b. Inserting into daily_metrics ---")
            metric_sql = """
                INSERT INTO daily_metrics
                (metric_id, checkin_id, metric_type, metric_name, value)
                VALUES (%s, %s, %s, %s, %s);
            """
            metrics_to_insert = [
                (uuid.uuid4(), checkin_id,
                    metric.metric_type, metric.metric_name, metric.value)
                for metric in checkin_data.metrics
            ]
            psycopg2.extras.execute_batch(cur, metric_sql, metrics_to_insert)
            print(f"--- Inserted {len(metrics_to_insert)} metrics ---")

        if checkin_data.completed_steps:
            print("--- 4c. Inserting into completed_steps ---")
            step_sql = """
                INSERT INTO completed_steps
                (completion_id, checkin_id, step_id,
                    is_completed, actual_duration)
                VALUES (%s, %s, %s, %s, %s);
            """
            steps_to_insert = [
                (uuid.uuid4(), checkin_id,
                    step.step_id, step.is_completed, step.actual_duration)
                for step in checkin_data.completed_steps
            ]
            psycopg2.extras.execute_batch(cur, step_sql, steps_to_insert)
            print(f"--- Inserted {len(steps_to_insert)} completed steps ---")

        if checkin_data.top_goal:
            goal_sql = """
                INSERT INTO top_goal
                (goal_id, user_id, goal_date, goal_description, is_completed)
                VALUES (%s, %s, %s, %s, %s);
            """
            cur.execute(goal_sql, (
                uuid.uuid4(),
                current_user_id,
                checkin_data.checkin_date,
                checkin_data.top_goal.goal_description,
                checkin_data.top_goal.is_completed
            ))

        conn.commit()
        return {"status": "success",
                "message": "Check-in created successfully.",
                "checkin_id": checkin_id}

    except psycopg2.Error as db_error:
        print("\n--- !!! DATABASE ERROR !!! ---")
        print(f"DB Error Type: {type(db_error).__name__}")
        print(f"DB Error Details: {db_error}")
        print(f"DB Error pgcode: {db_error.pgcode}")
        print(f"DB Error pgerror: {db_error.pgerror}")
        if conn:
            print("--- Rolling back transaction ---")
            conn.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Database error occurred. \
                            Code: {db_error.pgcode}")

    except Exception as e:
        print("\n--- !!! UNEXPECTED ERROR !!! ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Details: {e}")
        if conn:
            print("--- Rolling back transaction ---")
            conn.rollback()
        raise HTTPException(status_code=500,
                            detail="An unexpected server error occurred.")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("--- Connection closed ---")
