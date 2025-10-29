#API calls regarding user
#/backend/routers/users.py

import uuid
from fastapi import APIRouter, HTTPException, Depends 
from database import get_db_connection
import psycopg2
from schemas import UserCreate 
from core.config import pwd_context
from auth import get_current_user


# Create a router instance
router = APIRouter(
    prefix="/api/users", # Optional: Define prefix for all routes in this file
    tags=["Users"]       # Optional: Tag for API docs
)


@router.post("")
def create_user(user_data: UserCreate):
    print("\n--- 1. create_user endpoint called ---")
    print(f"   - Received data: name='{user_data.display_name}', email='{user_data.email}'")

    conn = None
    cur = None # Define cursor outside try block
    try:
        password_to_hash = user_data.password 
        print(f"--- Password length before hashing: {len(password_to_hash)} bytes ---") 
        # Hash the truncated password
        password_hash = pwd_context.hash(password_to_hash)
        print("--- Password hashed ---")

        print("--- 2. Attempting to get DB connection ---")
        conn = get_db_connection()
        cur = conn.cursor()
        print("--- 3. DB connection successful ---")

        sql_query = """
            INSERT INTO users (user_id, display_name, email, password_hash)
            VALUES (%s, %s, %s, %s);
        """
        values_to_insert = (str(uuid.uuid4()), user_data.display_name, user_data.email, password_hash)

        print("--- 4. Executing SQL ---")
        cur.execute(sql_query, values_to_insert)
        print("--- SQL Executed ---") # Added confirmation

        print("--- 5. Attempting to commit transaction ---") # Added before commit
        conn.commit()
        print("--- Transaction Committed ---") # Added after commit

        print("--- 6. Closing cursor and connection ---")
        cur.close()
        conn.close()
        print("--- Connection closed. Request successful. ---")

        return {"status": "success", "message": f"User {user_data.display_name} created."}

    except psycopg2.Error as db_error: # Catch specific database errors
        print("\n--- !!! DATABASE ERROR !!! ---")
        print(f"DB Error Code: {db_error.pgcode}") # Print specific PG error code
        print(f"DB Error Message: {db_error.pgerror}")
        if conn:
            print("--- Rolling back transaction due to DB error ---")
            conn.rollback() # Explicitly rollback on error
        raise HTTPException(status_code=500, detail=f"Database error occurred: {db_error.pgerror}")

    except Exception as e:
        print("\n--- !!! UNEXPECTED ERROR !!! ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Details: {e}")
        if conn:
             print("--- Rolling back transaction due to unexpected error ---")
             conn.rollback() # Explicitly rollback on error
        raise HTTPException(status_code=500, detail="An unexpected server error occurred.")

    finally:
        # Ensure resources are always released
        if cur:
            cur.close()
            print("--- Cursor closed in finally block ---")
        if conn:
            conn.close()
            print("--- Connection closed in finally block ---")

