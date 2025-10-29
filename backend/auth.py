# /backend/auth.py

from datetime import datetime, timedelta, timezone # Removed duplicate date
from typing import Optional # Removed List as it's not used here
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, APIRouter # <-- Import APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid
from schemas import UserLogin
from database import get_db_connection
import psycopg2
from psycopg2.extras import DictCursor
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context

# --- Create Router Instance ---
router = APIRouter(
    prefix="/api/login", # Define prefix for all routes in this file
    tags=["Authentication"] # Tag for API docs
)

# --- HELPER FUNCTIONS ---
# --- Helper function for password verification ---
def verify_password(plain_password, hashed_password):
    # Uses pwd_context imported from core.config
    return pwd_context.verify(plain_password, hashed_password)

# --- Token Creation Function ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Security Scheme ---
oauth2_scheme = HTTPBearer()

# --- Get Current User Function ---
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
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
# Use the router instance and correct path
@router.post("")
def login_user(credentials: UserLogin):
    print("\n--- 1. login_user endpoint called ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT user_id, email, password_hash FROM users WHERE email = %s;", (credentials.email,))
        user = cur.fetchone()

        # Close cursor and connection earlier if user not found
        if not user:
            if cur: cur.close()
            if conn: conn.close()
            raise HTTPException(status_code=404, detail="User not found")

        # Verify password BEFORE closing connection entirely
        if not verify_password(credentials.password, user["password_hash"]):
            if cur: cur.close()
            if conn: conn.close()
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Now close remaining resources after successful verification
        if cur: cur.close()
        if conn: conn.close()

        print("--- 6. Login successful, creating token ---")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": str(user["user_id"])}
        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except psycopg2.Error as e:
        print(f"\n--- !!! DATABASE ERROR: {e} !!! ---")
        if cur: cur.close() # Ensure cursor is closed on error too
        if conn: conn.close()
        raise HTTPException(status_code=500, detail="Database connection error.") # More generic error

    except HTTPException as e: # Re-raise HTTP exceptions
         if cur: cur.close()
         if conn: conn.close()
         raise e

    except Exception as e:
        print(f"\n--- !!! UNEXPECTED ERROR: {e} !!! ---")
        if cur: cur.close()
        if conn: conn.close()
        raise HTTPException(status_code=500, detail="An unexpected server error occurred.")