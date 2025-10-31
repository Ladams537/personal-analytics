# /backend/auth.py

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid
from schemas import UserLogin
from database import get_db_connection
import psycopg2
from psycopg2.extras import DictCursor
from core.config import (SECRET_KEY, ALGORITHM,
                         ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context)

# --- Create Router Instance ---
router = APIRouter(
    prefix="/api/login",
    tags=["Authentication"]
)


# --- HELPER FUNCTIONS ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
                              minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials =
                           Depends(oauth2_scheme)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return uuid.UUID(user_id)
    except JWTError:
        raise credentials_exception
    except ValueError:
        raise credentials_exception


# --- User login endpoint ---
@router.post("")
def login_user(credentials: UserLogin):
    print("\n--- 1. login_user endpoint called ---")
    print(f"    - Attempting login for email: {credentials.email}")

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        sql = "SELECT user_id, email, \
               password_hash FROM users WHERE email = %s;"
        print(f"--- 2. Executing SQL: \
               {sql} with param: {credentials.email} ---")

        cur.execute(sql, (credentials.email,))
        user = cur.fetchone()

        if not user:
            print("--- 3. SQL RESULT: User not found in database ---")
            if cur:
                cur.close()
            if conn:
                conn.close()
            raise HTTPException(status_code=404, detail="User not found")

        print(f"--- 3. SQL RESULT: Found user record: {dict(user)} ---")

        # Verify the password
        if not verify_password(credentials.password, user["password_hash"]):
            print("--- 4. Password verification FAILED ---")
            if cur:
                cur.close()
            if conn:
                conn.close()
            raise HTTPException(status_code=400, detail="Invalid credentials")

        print("--- 4. Password verification SUCCESSFUL ---")

        if cur:
            cur.close()
        if conn:
            conn.close()

        print("--- 5. Connection closed ---")

        # --- Create JWT Token ---
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": str(user["user_id"])}

        print(f"--- 6. Creating token with user_id: {user['user_id']} ---")

        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )

        print(f"--- 7. Returning access token: {access_token} ---")
        return {"access_token": access_token, "token_type": "bearer"}

    except psycopg2.Error as e:
        print(f"\n--- !!! DATABASE ERROR: {e} !!! ---")
        if cur:
            cur.close()
        if conn:
            conn.close()
        raise HTTPException(status_code=500,
                            detail="Database connection error.")

    except HTTPException as e:
        if cur:
            cur.close()
        if conn:
            conn.close()
        raise e

    except Exception as e:
        print(f"\n--- !!! UNEXPECTED ERROR: {e} !!! ---")
        if cur:
            cur.close()
        if conn:
            conn.close()
        raise HTTPException(status_code=500,
                            detail="An unexpected server error occurred.")
