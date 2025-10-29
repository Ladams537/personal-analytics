# Personal Coaching App (MVP)

## 🚀 Overview

This project is the Minimum Viable Product (MVP) for a personal coaching web application. The goal is to provide users with tailored insights to help simplify and improve their lives by tracking daily activities against their defined personal **principles** and **personality traits** (based on Myers-Briggs).

The core MVP loop involves:
1.  **Onboarding:** Capturing user principles and personality.
2.  **Daily Check-in:** Manually entering daily data (gratitude, principle alignment, time allocation, ratings, routine completion).
3.  **Dashboard:** Displaying the latest check-in data and eventually personalized insights.

---

## 🛠️ Tech Stack

* **Frontend:** [SvelteKit](https://kit.svelte.dev/) (with TypeScript)
* **Backend:** [Python 3.11+](https://www.python.org/) with [FastAPI](https://fastapi.tiangolo.com/)
* **Database:** [PostgreSQL](https://www.postgresql.org/) (running locally, e.g., via Postgres.app)
* **Database Interaction (Backend):** `psycopg2-binary` (direct SQL)
* **Authentication:** JWT (JSON Web Tokens) via `python-jose[cryptography]`
* **Password Hashing:** `passlib[bcrypt]`
* **Environment Variables:** `python-dotenv`

---

## ⚙️ Local Setup Instructions

### Prerequisites

* **Node.js & npm:** Required for the SvelteKit frontend. Download from [nodejs.org](https://nodejs.org/). Use `nvm` to manage Node versions if preferred.
* **Python:** Version 3.11 or higher. Download from [python.org](https://www.python.org/).
* **PostgreSQL:** A local PostgreSQL server must be running. [Postgres.app](https://postgresapp.com/) is a simple option for macOS. Ensure you know the connection details (username, password, database name, host, port).

### 1. Clone the Repository (If applicable)

```bash
git clone <https://github.com/Ladams537/personal-analytics.git>
cd personal-analytics # Or your project root folder name
```

### 2. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
# macOS / Linux:
source venv/bin/activate
# Windows (Git Bash/WSL):
# source venv/Scripts/activate
# Windows (CMD):
# venv\Scripts\activate.bat
# Windows (PowerShell):
# venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Create the .env file
# Create a file named ".env" in the /backend directory
# Add your local PostgreSQL connection details:
# DB_USER=your_local_username
# DB_PASSWORD=your_local_password
# DB_NAME=personal-analytics
# DB_HOST=127.0.0.1
# DB_PORT=5432
# SECRET_KEY=generate_a_long_random_string_here_for_jwt
```

### 3. Database Setup
1. Ensure your local PostgresSQL server is running
1. Connect to your PostgreSQL server using a client like DBeaver or pgAdmin
1. Create a new database named personal-analytics
1. Open the /backend/init.sql script
1. Execute the entire script against the personal-analytics database. This will create all the necessary tables

### 4. Frontend Setup
```bash
# Navigate to the frontend directory from the project root
cd ../frontend

# Install Node.js dependencies
npm install
```

### 5. Running the Development Servers 
You need two separate terminal windows.

#### Terminal 1: Backend (FastAPI)
```bash
# Navigate to the backend directory
cd backend

# Activate the virtual environment (if not already active)
source venv/bin/activate

# Start the server with auto-reload
uvicorn main:app --reload --reload-exclude venv
```

The backend API will be available at ```http://127.0.0.1:8000```. API docs are at ```http://127.0.0.1:8000/docs.```

#### Terminal 2: Frontend (SvelteKit)
```bash
# Navigate to the frontend directory
cd frontend

# Start the development server
npm run dev
```

The frontend application will be available at ```http://localhost:5173```.

# Project Structure
```bash
/personal-analytics
├── /backend          # FastAPI application
│   ├── /core         # Core configuration (e.g., config.py)
│   ├── /routers      # API endpoint modules (users, checkins, etc.)
│   ├── alembic/      # Database migration scripts (if using Alembic later)
│   ├── venv/         # Python virtual environment (ignored by git)
│   ├── auth.py       # Authentication logic and routes
│   ├── database.py   # Database connection setup
│   ├── main.py       # Main FastAPI app, middleware, router includes
│   ├── models.py     # SQLAlchemy models (if using ORM later)
│   ├── schemas.py    # Pydantic data models
│   ├── init.sql      # SQL script to initialize the database schema
│   ├── requirements.txt # Python dependencies
│   └── .env          # Environment variables (DB credentials, SECRET_KEY) (ignored by git)
│
├── /frontend         # SvelteKit application
│   ├── /src
│   │   ├── /lib      # Svelte components, stores, utilities
│   │   └── /routes   # SvelteKit page routes (+page.svelte, +layout.svelte)
│   ├── static/       # Static assets (images, fonts)
│   ├── package.json  # Node.js dependencies and scripts
│   └── ...           # Other SvelteKit config files
│
├── .gitignore        # Files/folders ignored by Git
└── README.md         # This file
```