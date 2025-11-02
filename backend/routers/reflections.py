# /backend/routers/reflections.py
import uuid
import psycopg2
from psycopg2.extras import DictCursor
from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
from auth import get_current_user
from schemas import Reflection, ReflectionCreate
from typing import List

router = APIRouter(
    prefix="/api/reflections",
    tags=["Reflections"]
)


@router.get("", response_model=List[Reflection])
async def get_all_reflections(current_user_id: uuid.UUID =
                              Depends(get_current_user)):
    print(f"\n--- 1. get_all_reflections called for user: \
          {current_user_id} ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        sql_query = """
            SELECT * FROM reflections
            WHERE user_id = %s
            ORDER BY created_at DESC;
        """
        cur.execute(sql_query, (current_user_id,))

        reflections = [dict(row) for row in cur.fetchall()]
        print(f"--- Found {len(reflections)} reflections ---")
        return reflections

    except psycopg2.Error as db_error:
        print(f"\n--- !!! DATABASE ERROR !!! ---\n{db_error}")
        raise HTTPException(status_code=500,
                            detail="Database error fetching reflections.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("--- Connection closed ---")


@router.post("", response_model=Reflection, status_code=201)
async def create_reflection(
    reflection_data: ReflectionCreate,
    current_user_id: uuid.UUID = Depends(get_current_user)
):
    print(f"\n--- 1. create_reflection called for user: {current_user_id} ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        sql_query = """
            INSERT INTO reflections (reflection_id, user_id, title, body)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
        """
        new_reflection_id = uuid.uuid4()

        cur.execute(sql_query, (
            new_reflection_id,
            current_user_id,
            reflection_data.title,
            reflection_data.body
        ))

        new_reflection = cur.fetchone()
        conn.commit()
        print("--- Reflection created successfully ---")
        return dict(new_reflection)

    except psycopg2.Error as db_error:
        print(f"\n--- !!! DATABASE ERROR !!! ---\n{db_error}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500,
                            detail="Database error creating reflection.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("--- Connection closed ---")
