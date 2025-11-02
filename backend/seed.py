# /backend/seed.py
import uuid
import random
from datetime import date, timedelta
from psycopg2.extras import execute_batch
from database import get_db_connection

# -----------------------------------------------------------------
# --- 1. CONFIGURE YOUR SYNTHETIC DATA HERE ---
# -----------------------------------------------------------------

# TODO: Paste the USER_ID (as a string) you want to generate data for.
# (Get this from your 'users' table in DBeaver)
USER_ID_TO_POPULATE = "4b749f1c-cac0-46cc-87e9-ab1e9177417a"  # <--- EDIT THIS

# TODO: How many days of data do you want to generate?
NUMBER_OF_DAYS_TO_GENERATE = 60

# TODO: Add the 'routine_steps' you want to track.
# (Get 'step_id's from your 'routine_steps' table in DBeaver)
ROUTINE_STEPS_TO_POPULATE = [
    # {"step_id": "624a717b-bfa7-486a-a80e-2c336b30bb9b", "target_duration": 15},
    # {"step_id": "b5325c7b-5881-47a0-9a63-d9ef8797a0f5", "target_duration": 60},
    # {"step_id": "ed08881f-7127-4c2e-b1d1-bfba65395dcb", "target_duration": 5},
    # {"step_id": "6ab5c55a-86cc-4ea8-b3ac-bdd2ec9b3cdf", "target_duration": 10},
    # {"step_id": "9438891d-ab6e-4a18-8bb8-38cd9e60c9a1", "target_duration": 60},
    # {"step_id": "43c695e1-841d-4612-b98e-077ef5501b61", "target_duration": 10},
    # {"step_id": "aa8114d6-a095-4fbc-89f1-67af81800c87", "target_duration": 10}
]  # <--- EDIT THIS

# These are the metric names your frontend check-in form uses
TIME_METRICS = ['Work', 'Family', 'Social', 'Exercise', 'Sleep', 'Maintenance']
RATING_METRICS = ['Productivity', 'Focus', 'Fun']

# -----------------------------------------------------------------
# --- 2. SCRIPT LOGIC (No edits needed below this line) ---
# -----------------------------------------------------------------


def generate_synthetic_data():
    if not USER_ID_TO_POPULATE or "f013" in USER_ID_TO_POPULATE:
        print("!!! ERROR: Please update 'USER_ID_TO_POPULATE' at the top of this script.")
        return
    if not ROUTINE_STEPS_TO_POPULATE or "uuid-of" in ROUTINE_STEPS_TO_POPULATE[0]["step_id"]:
        print("!!! WARNING: 'ROUTINE_STEPS_TO_POPULATE' is not set. No routine steps will be generated.")

    print(f"Connecting to database to generate {NUMBER_OF_DAYS_TO_GENERATE} days of data for user {USER_ID_TO_POPULATE}...")

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        today = date.today()
        user_uuid = uuid.UUID(USER_ID_TO_POPULATE)

        # We will insert all data in batches for efficiency
        checkins_to_insert = []
        metrics_to_insert = []
        goals_to_insert = []
        steps_to_insert = []

        for i in range(NUMBER_OF_DAYS_TO_GENERATE):
            current_date = today - timedelta(days=i)

            # --- 1. Create Daily Check-in ---
            checkin_id = uuid.uuid4()

            # Create a slight upward trend for principle_alignment
            # (Older data = lower score, newer data = higher score)
            base_alignment = 8 - (i * 0.1)  # Trends from ~2 (60 days ago) to 8 (today)
            principle_alignment = (
                max(1, min(10, int(base_alignment + random.uniform(-1, 1))))
            )

            checkins_to_insert.append((
                checkin_id,
                user_uuid,
                current_date,
                f"Synthetic gratitude entry for {current_date}.",
                principle_alignment,
                f"Synthetic note for {current_date}."
            ))

            # --- 2. Create Top Goal ---
            goals_to_insert.append((
                uuid.uuid4(),
                user_uuid,
                current_date,
                f"Synthetic top goal for {current_date}",
                random.choice([True, True, False])  # 66% chance of completion
            ))

            # --- 3. Create Daily Metrics ---
            for metric_name in TIME_METRICS:
                metrics_to_insert.append((
                    uuid.uuid4(),
                    checkin_id,
                    'Time Allocation',
                    metric_name,
                    random.randint(5, 25)
                ))
            for metric_name in RATING_METRICS:
                metrics_to_insert.append((
                    uuid.uuid4(),
                    checkin_id,
                    'Daily Rating',
                    metric_name,
                    random.randint(4, 9)
                ))

            # --- 4. Create Completed Steps ---
            for step in ROUTINE_STEPS_TO_POPULATE:
                is_completed = random.choice([True, True, False]) # 66% chance
                actual_duration = None
                if is_completed:
                    # Generate a duration +/- 5 mins from the target
                    actual_duration = max(
                        5,
                        random.randint(step["target_duration"] - 5,
                                       step["target_duration"] + 5)
                        )

                steps_to_insert.append((
                    uuid.uuid4(),
                    checkin_id,
                    uuid.UUID(step["step_id"]),
                    is_completed,
                    actual_duration
                ))

        print(f"Generated {len(checkins_to_insert)} check-ins and associated data. Inserting into database...")

        # --- Execute all inserts in batches ---
        execute_batch(cur,
                      """
                        INSERT INTO daily_checkins
                        (
                            checkin_id,
                            user_id,
                            checkin_date,
                            gratitude_entry,
                            principle_alignment,
                            principle_alignment_note
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                      """,
                      checkins_to_insert
                      )
        print(f"Inserted {len(checkins_to_insert)} daily_checkins.")

        execute_batch(cur,
                      """
                        INSERT INTO top_goal
                        (
                            goal_id,
                            user_id,
                            goal_date,
                            goal_description,
                            is_completed
                        )
                        VALUES (%s, %s, %s, %s, %s)
                      """,
                      goals_to_insert
                      )
        print(f"Inserted {len(goals_to_insert)} top_goals.")

        execute_batch(cur,
                      """
                        INSERT INTO daily_metrics
                        (
                            metric_id,
                            checkin_id,
                            metric_type,
                            metric_name,
                            value
                        )
                        VALUES (%s, %s, %s, %s, %s)
                      """,
                      metrics_to_insert
                      )
        print(f"Inserted {len(metrics_to_insert)} daily_metrics.")

        execute_batch(cur,
                      """
                        INSERT INTO completed_steps
                        (
                            completion_id,
                            checkin_id,
                            step_id,
                            is_completed,
                            actual_duration
                        )
                        VALUES (%s, %s, %s, %s, %s)
                      """,
                      steps_to_insert
                      )
        print(f"Inserted {len(steps_to_insert)} completed_steps.")

        # --- Commit all changes ---
        conn.commit()
        print("\n--- ✅ All data committed successfully! ---")

    except Exception as e:
        print(f"\n--- !!! AN ERROR OCCURRED !!! ---")
        print(f"Error: {e}")
        if conn:
            conn.rollback()
            print("--- Transaction rolled back. ---")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("--- Database connection closed. ---")


# --- Run the function when the script is executed ---
if __name__ == "__main__":
    generate_synthetic_data()
