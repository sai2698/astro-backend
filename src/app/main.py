from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import auth, users, courses, categories, orders, enrollments, astrologers, appointments, calls, admin_web, kundali, calendar
from app.core.config import settings
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(courses.router, prefix=f"{settings.API_V1_STR}/courses", tags=["courses"])
app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["orders"])
app.include_router(enrollments.router, prefix=f"{settings.API_V1_STR}/enrollments", tags=["enrollments"])
app.include_router(astrologers.router, prefix=f"{settings.API_V1_STR}/astrologers", tags=["astrologers"])
app.include_router(appointments.router, prefix=f"{settings.API_V1_STR}/appointments", tags=["appointments"])
app.include_router(calls.router, prefix=f"{settings.API_V1_STR}/calls", tags=["calls"])
app.include_router(kundali.router, prefix=f"{settings.API_V1_STR}/kundali", tags=["kundali"])
app.include_router(calendar.router, prefix=f"{settings.API_V1_STR}/calendar", tags=["calendar"])
app.include_router(admin_web.router, prefix="/admin", tags=["admin"])

@app.get("/")
def root():
    return {"message": "Welcome to Astrology App API"}

# # Create static directory if it doesn't exist
# static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
# uploads_dir = os.path.join(static_dir, "uploads")
# os.makedirs(uploads_dir, exist_ok=True)

# app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Create static directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
uploads_dir = os.path.join(static_dir, "uploads")
try:
    os.makedirs(uploads_dir, exist_ok=True)
except OSError:
    pass  # Serverless environments like Vercel have read-only filesystems

if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")