from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from typing import List, Optional
import aiosqlite
import os
import logging
from contextlib import asynccontextmanager
from functools import lru_cache

# Production Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
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

# Persistent Database Manager with Optimization
class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._pool = None

    async def get_conn(self):
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        # Performance Tuning: Enable WAL and faster sync
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA synchronous=NORMAL")
        await conn.execute("PRAGMA cache_size=-64000") # 64MB Cache
        return conn

db = Database(DB_PATH)

# In-Memory Cache for Static Data (Static values don't change often)
# Using a simple dict-based cache for async compatibility if needed, 
# or just wrapping the logic.
_cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("⚡ High-Performance Mode Starting...")
    if not os.path.exists(DB_PATH):
        logger.error(f"FATAL: {DB_PATH} missing. Run migrate.py first.")
    else:
        # Pre-verify and prime the engine
        conn = await db.get_conn()
        async with conn.execute("SELECT COUNT(*) FROM crop_calendar") as cursor:
            row = await cursor.fetchone()
            logger.info(f"Database Optimized & Live. Entries: {row[0]}")
        await conn.close()
    yield
    logger.info("Shutting down API...")

app = FastAPI(
    title="Udupi Crop Calendar HIGH-PERFORMANCE",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

# Middleware Stack
app.add_middleware(GZipMiddleware, minimum_size=1000) # Compresses large responses
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/", tags=["Status"])
async def root():
    return {"status": "optimised", "engine": "FastAPI + aiosqlite + orjson"}

@app.get("/calendar", response_model=APIResponse, tags=["Calendar"])
async def get_calendar(
    season: str = Query(..., description="E.g., Kharif, Rabi"),
    crop: str = Query(..., description="E.g., Paddy"),
    variety: str = Query(..., description="E.g., MO-4")
):
    return await fetch_calendar_data(season, crop, variety)

@app.post("/calendar", response_model=APIResponse, tags=["Calendar"])
async def post_calendar(request: CalendarRequest):
    return await fetch_calendar_data(request.season, request.crop, request.variety)

async def fetch_calendar_data(season: str, crop: str, variety: str):
    # Check In-Memory Cache first (Sub-millisecond)
    cache_key = f"{season.lower()}:{crop.lower()}:{variety.lower()}"
    if cache_key in _cache:
        logger.info(f"🚀 Cache Hit: {cache_key}")
        return _cache[cache_key]

    try:
        conn = await db.get_conn()
        variety_query = f"%{variety}%"
        
        query = """
            SELECT month, week_1, week_2, week_3, week_4 
            FROM crop_calendar 
            WHERE LOWER(season) = LOWER(?) 
              AND LOWER(crop) = LOWER(?) 
              AND LOWER(variety) LIKE LOWER(?)
            ORDER BY id ASC
        """
        
        async with conn.execute(query, (season, crop, variety_query)) as cursor:
            rows = await cursor.fetchall()
        await conn.close()

        if not rows:
            raise HTTPException(status_code=404, detail="No matching calendar found.")

        calendar_list = [CalendarEntry(**dict(row)) for row in rows]
        
        response = APIResponse(
            metadata={"season": season, "crop": crop, "variety": variety, "count": len(calendar_list)},
            calendar=calendar_list
        )

        # Update Cache
        _cache[cache_key] = response
        logger.info(f"💾 Cache Seeded: {cache_key}")
        return response

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal performance failure")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # use_colors=True and other standard options via uvicorn[standard]
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
