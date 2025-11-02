# /backend/seed.py
import uuid
import random
from datetime import date, timedelta
from database import get_db_connection
from psycopg2.extras import execute_batch

# -----------------------------------------------------------------
# --- 1. CONFIGURE YOUR SYNTHETIC DATA HERE ---
# -----------------------------------------------------------------

# TODO: Paste the USER_ID (as a string) you want to generate data for.
USER_ID_TO_POPULATE = "2453ad55-a68c-48e5-b94a-60d28a5974c6"  # <--- EDIT THIS

# TODO: How many days of data do you want to generate?
NUMBER_OF_DAYS_TO_GENERATE = 60

# --- NEW: Define the routines and steps you want to create ---
ROUTINES_TO_GENERATE = [
    {
        "routine_name": "Morning Routine",
        "steps": [
            {"step_name": "Run", "target_duration": 15, "step_order": 1},
            {"step_name": "Read", "target_duration": 10, "step_order": 2},
            {"step_name": "Meditate", "target_duration": 5, "step_order": 3}
        ]
    },
    {
        "routine_name": "Evening Wind-down",
        "steps": [
            {"step_name": "Journal", "target_duration": 10, "step_order": 1},
            {"step_name": "Tidy Up", "target_duration": 5, "step_order": 2}
        ]
    }
]

# These are the metric names your frontend check-in form uses
TIME_METRICS = ['Work', 'Family', 'Social', 'Exercise', 'Sleep', 'Maintenance']
RATING_METRICS = ['Productivity', 'Focus', 'Fun']

# -----------------------------------------------------------------
# --- 2. SCRIPT LOGIC (No edits needed below this line) ---
# -----------------------------------------------------------------


def generate_synthetic_data():
    if not USER_ID_TO_POPULATE or "your_user_id" in USER_ID_TO_POPULATE:
        print("!!! ERROR: Please update 'USER_ID_TO_POPULATE' at the top of this script.")
        return

    print(f"Connecting to database to generate {NUMBER_OF_DAYS_TO_GENERATE} days of data for user {USER_ID_TO_POPULATE}...")

    conn = None
    cur = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        today = date.today()
        user_uuid = uuid.UUID(USER_ID_TO_POPULATE)
        
        # --- NEW: Clear old data for this user ---
        print(f"--- Clearing old synthetic data for user {user_uuid} ---")
        cur.execute("DELETE FROM daily_checkins WHERE user_id = %s;", (user_uuid,))
        cur.execute("DELETE FROM top_goal WHERE user_id = %s;", (user_uuid,))
        cur.execute("DELETE FROM routines WHERE user_id = %s;", (user_uuid,))
        # Note: 'routine_steps' and 'completed_steps' are cleared by CASCADE
        
        # --- NEW: Generate Routines and Steps ---
        print(f"--- Generating {len(ROUTINES_TO_GENERATE)} routines and their steps ---")
        
        # This list will hold the generated steps to be used later
        generated_steps_for_checkin = [] 

        for routine in ROUTINES_TO_GENERATE:
            # 1. Create the parent routine
            routine_id = uuid.uuid4()
            cur.execute(
                "INSERT INTO routines (routine_id, user_id, routine_name) VALUES (%s, %s, %s);",
                (routine_id, user_uuid, routine['routine_name'])
            )
            
            # 2. Create the steps for this routine
            steps_to_insert = []
            for step in routine['steps']:
                step_id = uuid.uuid4()
                steps_to_insert.append((
                    step_id,
                    routine_id,
                    step['step_name'],
                    step['target_duration'],
                    step['step_order']
                ))
                # Add to our list for later use
                generated_steps_for_checkin.append({
                    "step_id": str(step_id), # Store as string for easy comparison
                    "target_duration": step['target_duration']
                })
            
            execute_batch(cur, 
                "INSERT INTO routine_steps (step_id, routine_id, step_name, target_duration, step_order) VALUES (%s, %s, %s, %s, %s);",
                steps_to_insert
            )
        
        print(f"--- Routines created. Total steps generated: {len(generated_steps_for_checkin)} ---")

        # --- Generate Check-in Data (Main Loop) ---
        print(f"--- Generating {NUMBER_OF_DAYS_TO_GENERATE} days of check-in data ---")
        checkins_to_insert = []
        metrics_to_insert = []
        goals_to_insert = []
        steps_to_insert = []

        for i in range(NUMBER_OF_DAYS_TO_GENERATE):
            current_date = today - timedelta(days=i)
            
            # --- 1. Create Daily Check-in ---
            checkin_id = uuid.uuid4()
            base_alignment = 8 - (i * 0.1) # Trends from ~2 (60 days ago) to 8 (today)
            principle_alignment = max(1, min(10, int(base_alignment + random.uniform(-1, 1))))
            
            checkins_to_insert.append((
                checkin_id, user_uuid, current_date,
                f"Synthetic gratitude for {current_date}.",
                principle_alignment, f"Synthetic note for {current_date}."
            ))

            # --- 2. Create Top Goal ---
            goals_to_insert.append((
                uuid.uuid4(), user_uuid, current_date,
                f"Synthetic top goal for {current_date}",
                random.choice([True, True, False])
            ))

            # --- 3. Create Daily Metrics ---
            for metric_name in TIME_METRICS:
                metrics_to_insert.append((
                    uuid.uuid4(), checkin_id, 'Time Allocation', metric_name, random.randint(5, 25)
                ))
            for metric_name in RATING_METRICS:
                metrics_to_insert.append((
                    uuid.uuid4(), checkin_id, 'Daily Rating', metric_name, random.randint(4, 9)
                ))

            # --- 4. Create Completed Steps (using generated steps) ---
            for step in generated_steps_for_checkin:
                is_completed = random.choice([True, True, False])
                actual_duration = None
                if is_completed and step["target_duration"]:
                    duration = step["target_duration"]
                    actual_duration = max(5, random.randint(duration - 5, duration + 5))
                
                steps_to_insert.append((
                    uuid.uuid4(), checkin_id, uuid.UUID(step["step_id"]), is_completed, actual_duration
                ))

        print(f"Generated data. Inserting into database...")

        # --- Execute all inserts in batches ---
        execute_batch(cur,
            """
            INSERT INTO daily_checkins (checkin_id, user_id, checkin_date, gratitude_entry, principle_alignment, principle_alignment_note)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, 
            checkins_to_insert
        )
        print(f"Inserted {len(checkins_to_insert)} daily_checkins.")

        execute_batch(cur,
            """
            INSERT INTO top_goal (goal_id, user_id, goal_date, goal_description, is_completed)
            VALUES (%s, %s, %s, %s, %s)
            """, 
            goals_to_insert
        )
        print(f"Inserted {len(goals_to_insert)} top_goals.")

        execute_batch(cur, 
            """
            INSERT INTO daily_metrics (metric_id, checkin_id, metric_type, metric_name, value)
            VALUES (%s, %s, %s, %s, %s)
            """, 
            metrics_to_insert
        )
        print(f"Inserted {len(metrics_to_insert)} daily_metrics.")
        
        execute_batch(cur, 
            """
            INSERT INTO completed_steps (completion_id, checkin_id, step_id, is_completed, actual_duration)
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