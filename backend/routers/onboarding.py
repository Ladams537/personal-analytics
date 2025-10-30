# /backend/routers/onboarding.py

import uuid
from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
import psycopg2
from schemas import PersonalityUpdateRequest, PrincipleUpdateRequest
from auth import get_current_user


router = APIRouter(
    prefix="/api/onboarding",
    tags=["Onboarding"]
)


@router.post("/personality")
def save_personality_traits(
    request_data: PersonalityUpdateRequest,
    current_user_id: uuid.UUID = Depends(get_current_user)
):
    print(f"\n--- save_personality_traits called for user: \
          {current_user_id} ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        sql_query = """
            INSERT INTO personality_traits
            (trait_id, user_id, scale_name, trait_name, value, display_order)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        traits_to_insert = [
            # Use current_user_id from token
            (uuid.uuid4(), current_user_id,
                trait.scale_name, trait.trait_name,
                trait.value, trait.display_order)
            for trait in request_data.traits
        ]
        psycopg2.extras.execute_batch(cur, sql_query, traits_to_insert)
        conn.commit()
        print(f"--- Saved {len(traits_to_insert)} \
              personality traits for user {current_user_id} ---")
        return {"status": "success", "message": "Personality traits saved."}

    except psycopg2.Error as db_error:
        print(f"DB Error: {db_error}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500,
                            detail="Database error saving personality traits.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@router.post("/principles")
def save_user_principles(
    request_data: PrincipleUpdateRequest,
    current_user_id: uuid.UUID = Depends(get_current_user)
):
    print(f"\n--- save_user_principles called for user: \
          {current_user_id} ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        print(f"--- Deleting existing principles for user \
              {current_user_id} ---")
        cur.execute("DELETE FROM user_principles WHERE user_id = %s;",
                    (current_user_id,))

        if request_data.principles:
            sql_query = """
                INSERT INTO user_principles
                (user_id, principle_id, principle_rank)
                VALUES (%s, %s, %s);
            """
            principles_to_insert = [
                # Use current_user_id from token
                (current_user_id, p.principle_id, p.rank)
                for p in request_data.principles
            ]
            print(f"--- Inserting {len(principles_to_insert)} \
                  principles for user {current_user_id} ---")
            psycopg2.extras.execute_batch(cur, sql_query, principles_to_insert)
        else:
            print(f"--- No principles selected for user {current_user_id} ---")

        # Optional: Update onboarding_complete flag
        cur.execute("UPDATE users SET onboarding_complete = \
                    TRUE WHERE user_id = %s;", (current_user_id,))

        conn.commit()
        return {"status": "success", "message": "User principles saved."}

    except psycopg2.Error as db_error:
        print(f"DB Error: {db_error}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500,
                            detail="Database error saving user principles.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
