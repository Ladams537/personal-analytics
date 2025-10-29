-- Drop tables in the correct dependency order
DROP TABLE IF EXISTS top_goal CASCADE;
DROP TABLE IF EXISTS completed_steps CASCADE;
DROP TABLE IF EXISTS routine_steps CASCADE;
DROP TABLE IF EXISTS daily_metrics CASCADE;
DROP TABLE IF EXISTS daily_checkins CASCADE;
DROP TABLE IF EXISTS routines CASCADE;
DROP TABLE IF EXISTS user_principles CASCADE;
DROP TABLE IF EXISTS principles CASCADE;
DROP TABLE IF EXISTS personality_traits CASCADE;
DROP TABLE IF EXISTS insight CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- User and Profile Tables
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    onboarding_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE personality_traits (
    trait_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    scale_name VARCHAR(255) NOT NULL,
    trait_name VARCHAR(255) NOT NULL,
    value INTEGER NOT NULL CHECK (value >= 0 AND value <= 100),
    display_order INTEGER
);

CREATE TABLE principles (
    principle_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE user_principles (
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    principle_id UUID NOT NULL REFERENCES principles(principle_id) ON DELETE CASCADE,
    principle_rank INTEGER,
    PRIMARY KEY (user_id, principle_id)
);

-- Routines and Steps (Must be created before check-ins)
CREATE TABLE routines (
    routine_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    routine_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- FIX 1: This table must be created *before* completed_steps
CREATE TABLE routine_steps (
    step_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    routine_id UUID NOT NULL REFERENCES routines(routine_id) ON DELETE CASCADE,
    step_name VARCHAR(255) NOT NULL,
    target_duration INT,
    step_order INTEGER NOT NULL
); -- FIX 2: Added missing semicolon

-- Daily Check-in Tables
CREATE TABLE daily_checkins (
    checkin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    checkin_date DATE NOT NULL,
    gratitude_entry TEXT,
    principle_alignment INTEGER CHECK (principle_alignment >= 1 AND principle_alignment <= 10),
    principle_alignment_note TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, checkin_date)
);

CREATE TABLE daily_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checkin_id UUID NOT NULL REFERENCES daily_checkins(checkin_id) ON DELETE CASCADE,
    metric_type VARCHAR(255) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    value INTEGER NOT NULL
);

-- FIX 1: This table must be created *after* daily_checkins and routine_steps
CREATE TABLE completed_steps (
    completion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checkin_id UUID NOT NULL REFERENCES daily_checkins(checkin_id) ON DELETE CASCADE,
    step_id UUID NOT NULL REFERENCES routine_steps(step_id) ON DELETE CASCADE,
    is_completed BOOLEAN NOT NULL,
    actual_duration INT
);

CREATE TABLE top_goal (
    goal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    goal_date DATE NOT NULL,
    goal_description TEXT NOT NULL,
    is_completed BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, goal_date)
);

-- Insight Table (Generated coaching advice)
CREATE TABLE insight (
    insight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    insight_type VARCHAR(255),
    content TEXT NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    is_read BOOLEAN DEFAULT FALSE
);

-- Optional: Add Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_personality_traits_user ON personality_traits(user_id);
CREATE INDEX idx_checkins_user_date ON daily_checkins(user_id, checkin_date);
CREATE INDEX idx_metrics_checkin ON daily_metrics(checkin_id);
CREATE INDEX idx_routines_user ON routines(user_id);
CREATE INDEX idx_routine_steps_routine ON routine_steps(routine_id);
CREATE INDEX idx_completed_steps_checkin ON completed_steps(checkin_id);
CREATE INDEX idx_top_goal_user_date ON top_goal(user_id, goal_date);
CREATE INDEX idx_insight_user ON insight(user_id);

-- Enable UUID generation if not already enabled (Run once per database)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- Alternative UUID generation
-- CREATE EXTENSION IF NOT EXISTS pgcrypto; -- Provides gen_random_uuid()