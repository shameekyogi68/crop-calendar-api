from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import logging
from contextlib import asynccontextmanager

# Production Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("CropCalendarAPI")

DB_PATH = "calendar.db"

# Pydantic Schema Models
class CalendarRequest(BaseModel):
    season: str
    crop: str
    variety: str

class CalendarEntry(BaseModel):
    month: str
    week_1: str
    week_2: str
    week_3: str
    week_4: str

class APIResponse(BaseModel):
    metadata: dict
    calendar: List[CalendarEntry]

# Database Connection Utility
class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Returns results as dict-like objects
        return conn

db = Database(DB_PATH)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Verify database integrity
    logger.info("Starting up API - Verifying database...")
    if not os.path.exists(DB_PATH):
        logger.error(f"Database {DB_PATH} not found. Please run migrate.py first.")
    else:
        conn = db.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM crop_calendar").fetchone()[0]
        logger.info(f"Database verified. Loaded {count} agronomic entries.")
        conn.close()
    yield
    # Shutdown: Cleanup if needed
    logger.info("Shutting down API...")

app = FastAPI(
    title="Udupi Crop Calendar Professional API",
    version="1.0.0",
    lifespan=lifespan
)

# Production CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tighten this for production if you have a specific domain
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Status"])
async def root():
    return {"status": "healthy", "service": "Udupi Crop Calendar API"}

@app.get("/calendar", response_model=APIResponse, tags=["Calendar"])
async def get_calendar(
    season: str = Query(..., description="E.g., Kharif, Rabi, Summer"),
    crop: str = Query(..., description="E.g., Paddy, Groundnut"),
    variety: str = Query(..., description="E.g., MO-4, TMV-2")
):
    return await fetch_calendar_data(season, crop, variety)

@app.post("/calendar", response_model=APIResponse, tags=["Calendar"])
async def post_calendar(request: CalendarRequest):
    return await fetch_calendar_data(request.season, request.crop, request.variety)

async def fetch_calendar_data(season: str, crop: str, variety: str):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Efficient Index-Based Lookup with Fuzzy Variety Matching
        query = """
            SELECT month, week_1, week_2, week_3, week_4 
            FROM crop_calendar 
            WHERE LOWER(season) = LOWER(?) 
              AND LOWER(crop) = LOWER(?) 
              AND LOWER(variety) LIKE LOWER(?)
            ORDER BY id ASC
        """
        
        # Use %wildcards% for the variety to allow partial matches like "MO-4" -> "MO-4 (Bhadra)"
        results = cursor.execute(query, (season, crop, f"%{variety}%")).fetchall()
        conn.close()

        if not results:
            logger.warning(f"No results found for: {season}/{crop}/{variety}")
            raise HTTPException(
                status_code=404, 
                detail=f"Calendar not found. Verify season, crop, and variety spelling."
            )

        calendar_list = [
            CalendarEntry(
                month=row["month"],
                week_1=row["week_1"],
                week_2=row["week_2"],
                week_3=row["week_3"],
                week_4=row["week_4"]
            ) for row in results
        ]

        logger.info(f"Successfully served calendar for {crop} ({variety})")
        
        return APIResponse(
            metadata={
                "season": season,
                "crop": crop,
                "variety": variety,
                "count": len(calendar_list)
            },
            calendar=calendar_list
        )

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
