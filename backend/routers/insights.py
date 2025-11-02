# /backend/routers/insights.py
import uuid
from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
import psycopg2
from psycopg2.extras import DictCursor
from auth import get_current_user
from insights_engine import generate_insights

router = APIRouter(
    prefix="/api/insights",
    tags=["Insights"]
)


@router.post("/generate")
async def generate_new_insight(current_user_id: uuid.UUID
                               = Depends(get_current_user)):
    print(f"\n--- 1. generate_new_insight called for user: \
          {current_user_id} ---")
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)

        # --- 1. Fetch latest check-in data ---
        # (This is similar to the dashboard query)
        cur.execute(
            "SELECT * FROM daily_checkins WHERE user_id = %s \
            ORDER BY checkin_date DESC LIMIT 1",
            (current_user_id,)
        )
        latest_checkin_row = cur.fetchone()
        if not latest_checkin_row:
            raise HTTPException(status_code=404,
                                detail="No check-in data found \
                                to generate insight.")

        # Convert the read-only row to a mutable dictionary
        latest_checkin = dict(latest_checkin_row)

        # --- 2. Fetch metrics for that check-in ---
        cur.execute(
            "SELECT metric_type, metric_name, value \
            FROM daily_metrics WHERE checkin_id = %s",
            (latest_checkin['checkin_id'],)
        )
        metrics = [dict(row) for row in cur.fetchall()]
        latest_checkin['metrics'] = metrics

        # --- 3. Fetch personality traits ---
        cur.execute(
            "SELECT trait_name, value FROM personality_traits \
            WHERE user_id = %s",
            (current_user_id,)
        )
        user_personality = [dict(row) for row in cur.fetchall()]

        # --- 4. Fetch user principles ---
        cur.execute(
            "SELECT p.name FROM user_principles up \
            JOIN principles p \
            ON up.principle_id = p.principle_id \
            WHERE up.user_id = %s",
            (current_user_id,)
        )
        user_principles = [row['name'] for row in cur.fetchall()]

        # --- 5. Run the engine ---
        insight_content = generate_insights(user_personality,
                                            user_principles,
                                            latest_checkin)

        if not insight_content:
            return {"status": "no_insight",
                    "message": "No new insight generated."}

        # --- 6. Save the new insight to the DB ---
        print(f"--- Saving new insight: {insight_content[:50]}... ---")
        insert_sql = """
            INSERT INTO insight (insight_id, user_id, insight_type, content)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
        """
        new_insight = (uuid.uuid4(),
                       current_user_id,
                       'Daily Tidbit',
                       insight_content)
        cur.execute(insert_sql, new_insight)
        saved_insight = dict(cur.fetchone())

        conn.commit()
        return saved_insight

    except psycopg2.Error as db_error:
        print(f"DB Error: {db_error}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500,
                            detail="Database error generating insight.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("--- Connection closed ---")
