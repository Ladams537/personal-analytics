#main backend file bringing API calls and logic together
#/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, onboarding, checkins, routines, goals, dashboard
import auth 


app = FastAPI()


# --- CORS Middleware ---
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(onboarding.router)
app.include_router(checkins.router)
app.include_router(routines.router)
app.include_router(goals.router)
app.include_router(dashboard.router)