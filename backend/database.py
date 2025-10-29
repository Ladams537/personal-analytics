# /backend/database.py
import os
import psycopg2
from psycopg2.extras import register_uuid
from dotenv import load_dotenv

register_uuid()

load_dotenv()


def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_DATABASE'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn
