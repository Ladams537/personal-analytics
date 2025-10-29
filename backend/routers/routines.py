#API calls for handling the individual and subroutines of the user
#/backend/routers/routines.py

import uuid
import psycopg2
from psycopg2.extras import DictCursor
from fastapi import HTTPException
from fastapi import Depends
from database import get_db_connection
from schemas import Routine, RoutineCreate, RoutineStep, RoutineStepCreate
from typing import List
from fastapi import APIRouter
from auth import get_current_user

router = APIRouter(
    prefix="/api/routines", # Optional: Define prefix for all routes in this file
    tags=["Routines"]       # Optional: Tag for API docs
)

@router.get("")
async def get_routines(current_user_id: uuid.UUID = Depends(get_current_user)):
    print(f"\n--- 1. get_routines called for user: {current_user_id} ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        # 1. Fetch all parent routines for the user
        print("--- 2. Fetching all routines ---")
        cur.execute(
            "SELECT * FROM routines WHERE user_id = %s ORDER BY created_at",
            (current_user_id,)
        )
        routines_rows = cur.fetchall()
        
        # 2. Fetch all steps for those routines
        print("--- 3. Fetching all steps for user ---")
        routine_ids = [row['routine_id'] for row in routines_rows]
        steps = []
        if routine_ids: # Only query if routines exist
            steps_sql = """
                SELECT * FROM routine_steps
                WHERE routine_id = ANY(%s)
                ORDER BY routine_id, step_order
            """
            cur.execute(steps_sql, (routine_ids,))
            steps = cur.fetchall()

        # 3. Combine routines and steps into a nested structure
        print("--- 4. Combining data ---")
        routines_map = {row['routine_id']: dict(row) for row in routines_rows}
        for routine_id in routines_map:
            routines_map[routine_id]['steps'] = [] # Initialize empty steps list

        for step in steps:
            routines_map[step['routine_id']]['steps'].append(dict(step))

        return list(routines_map.values()) # Return the list of routine objects

    except psycopg2.Error as db_error:
        print(f"DB Error: {db_error}")
        raise HTTPException(status_code=500, detail="Database error fetching routines.")
    finally:
        if cur: cur.close()
        if conn: conn.close()
        print("--- Connection closed ---")


@router.post("", status_code=201) # 201 means "Created"
async def create_routine(
    routine_data: RoutineCreate,
    current_user_id: uuid.UUID = Depends(get_current_user)
):
    print(f"\n--- 1. create_routine called for user: {current_user_id} ---")
    conn = None
    cur = None
    try:
        print("--- 2. Attempting DB connection ---")
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor) # Use DictCursor to return the new row
        print("--- 3. DB connection successful ---")

        sql_query = """
            INSERT INTO routines (routine_id, user_id, routine_name)
            VALUES (%s, %s, %s)
            RETURNING routine_id, routine_name, is_active, created_at; -- Return the new routine
        """
        new_routine_id = uuid.uuid4()
        
        print(f"--- 4. Executing insert for routine: '{routine_data.routine_name}' ---")
        cur.execute(sql_query, (
            new_routine_id,
            current_user_id,
            routine_data.routine_name
        ))

        new_routine = cur.fetchone() # Get the returned new routine row
        
        print("--- 5. Committing transaction ---")
        conn.commit()
        
        print("--- Routine created successfully ---")
        return dict(new_routine) # Return the newly created routine as a dict

    except psycopg2.Error as db_error:
        print(f"\n--- !!! DATABASE ERROR !!! ---")
        print(f"DB Error: {db_error}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="Database error creating routine.")
    except Exception as e:
        print(f"\n--- !!! UNEXPECTED ERROR !!! ---")
        print(f"Error: {e}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="An unexpected server error occurred.")
    finally:
        if cur: cur.close()
        if conn: conn.close()
        print("--- Connection closed ---")


# --- NEW: Add a step to a routine ---
@router.post("/{routine_id}/steps", response_model=RoutineStep)
async def create_routine_step(
    routine_id: uuid.UUID,
    step_data: RoutineStepCreate,
    current_user_id: uuid.UUID = Depends(get_current_user)
):
    print(f"\n--- 1. create_routine_step called for routine: {routine_id} ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        # First, verify the user owns this routine
        print("--- 2. Verifying routine ownership ---")
        cur.execute(
            "SELECT user_id FROM routines WHERE routine_id = %s", (routine_id,)
        )
        routine = cur.fetchone()
        
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found.")
        if routine['user_id'] != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this routine.")

        # 3. Insert the new step
        print("--- 3. Inserting new step ---")
        sql_query = """
            INSERT INTO routine_steps (step_id, routine_id, step_name, target_duration, step_order)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *; -- Return the full new step
        """
        new_step_id = uuid.uuid4()
        cur.execute(sql_query, (
            new_step_id,
            routine_id,
            step_data.step_name,
            step_data.target_duration,
            step_data.step_order
        ))
        
        new_step = cur.fetchone()
        conn.commit()
        print("--- 4. Step created and committed ---")
        
        return dict(new_step)

    except psycopg2.Error as db_error:
        print(f"DB Error: {db_error}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="Database error creating routine step.")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="An unexpected server error occurred.")
    finally:
        if cur: cur.close()
        if conn: conn.close()
        print("--- Connection closed ---")