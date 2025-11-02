# /backend/routers/charts.py
import uuid
import psycopg2
from psycopg2.extras import DictCursor
from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
from auth import get_current_user
from schemas import ChartData

router = APIRouter(
    prefix="/api/charts",
    tags=["Charts"]
)


@router.get("/principle-alignment", response_model=ChartData)
async def get_principle_alignment_chart(
    current_user_id: uuid.UUID = Depends(get_current_user)
):
    print(f"\n--- 1. get_principle_alignment_chart called for user: \
            {current_user_id} ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        # This query fetches the date and score for the last 60 days
        # ordering by date ASC to make the chart plot correctly
        sql_query = """
            SELECT checkin_date, principle_alignment
            FROM daily_checkins
            WHERE user_id = %s
              AND checkin_date >= NOW() - INTERVAL '60 days'
            ORDER BY checkin_date ASC;
        """

        print("--- 2. Executing SQL for chart data ---")
        cur.execute(sql_query, (current_user_id,))

        rows = cur.fetchall()

        # Separate the data into two lists for Chart.js
        labels = [row['checkin_date'] for row in rows]
        data = [row['principle_alignment'] for row in rows]

        print(f"--- 3. Found {len(labels)} data points ---")
        return ChartData(labels=labels, data=data)

    except psycopg2.Error as db_error:
        print(f"\n--- !!! DATABASE ERROR !!! ---\n{db_error}")
        raise HTTPException(status_code=500,
                            detail="Database error fetching chart data.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("--- Connection closed ---")
