# /backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import onboarding, \
    checkins, \
    routines, \
    goals, \
    dashboard, \
    principles, \
    insights, \
    reflections
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
app.include_router(onboarding.router)
app.include_router(checkins.router)
app.include_router(routines.router)
app.include_router(goals.router)
app.include_router(dashboard.router)
app.include_router(principles.router)
app.include_router(insights.router)
app.include_router(reflections.router)
