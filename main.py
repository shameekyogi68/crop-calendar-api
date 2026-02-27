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
    language: str = "en"

class WeeklyActivity(BaseModel):
    week_number: int
    field_operation: str
    irrigation: str
    fertilizer: str
    weed_management: str
    protection: str
    stage: str

class MonthlyActivity(BaseModel):
    month: str
    major_operations: List[str]
    critical_actions: List[str]
    weeks: List[WeeklyActivity]

class ProgressTracker(BaseModel):
    current_week: int
    current_phase: str
    upcoming_operation: str

class OperationalPlanResponse(BaseModel):
    context: dict
    timeline: List[MonthlyActivity]
    summary_by_month: dict
    progress: ProgressTracker


# Persistent Database Manager with Optimization
class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def get_conn(self):
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        # Performance Tuning
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA synchronous=NORMAL")
        return conn

db = Database(DB_PATH)
_cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("⚡ High-Performance Bilingual Mode Starting...")
    if not os.path.exists(DB_PATH):
        logger.error(f"FATAL: {DB_PATH} missing.")
    yield

app = FastAPI(
    title="Udupi Crop Calendar BILINGUAL API",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

# Middleware Stack
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/", tags=["Status"])
async def root():
    return {"status": "optimised", "engine": "FastAPI + aiosqlite (Bilingual)"}

@app.get("/calendar", response_model=OperationalPlanResponse, tags=["Calendar"])
async def get_calendar(
    season: str = Query(..., description="E.g., Kharif, Rabi"),
    crop: str = Query(..., description="E.g., Paddy"),
    variety: str = Query(..., description="E.g., MO-4"),
    language: str = Query("en", description="en or kn")
):
    return await fetch_calendar_data(season, crop, variety, language)

@app.post("/calendar", response_model=OperationalPlanResponse, tags=["Calendar"])
async def post_calendar(request: CalendarRequest):
    return await fetch_calendar_data(request.season, request.crop, request.variety, request.language)

async def fetch_calendar_data(season: str, crop: str, variety: str, language: str = "en"):
    cache_key = f"op:{language}:{season.lower()}:{crop.lower()}:{variety.lower()}"
    if cache_key in _cache:
        logger.info(f"🚀 Cache Hit: {cache_key}")
        return _cache[cache_key]

    try:
        conn = await db.get_conn()
        variety_query = f"%{variety}%"
        
        # We always need the English version for logic, and the localized version for display
        suffix = "_kn" if language.lower() == "kn" else ""
        query = f"""
            SELECT month, 
                   week_1, week_2, week_3, week_4,
                   week_1{suffix} as l_week_1, 
                   week_2{suffix} as l_week_2, 
                   week_3{suffix} as l_week_3, 
                   week_4{suffix} as l_week_4 
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

        # Logic for parsing and categorizing
        timeline = []
        all_activities = []
        
        # Keywords for categorization
        cat_map = {
            "irrigation": ["💧", "water", "irrigate", "moist", "drain", "flooded", "remove water", "stop watering", "ನೀರು", "ನೀರಾವರಿ"],
            "fertilizer": ["🧪", "Urea", "DAP", "Potash", "NPK", "Zinc", "MgSO4", "Borax", "Gypsum", "Basal", "compost", "manure", "Nitrogen", "Growth Dose", "ಗೊಬ್ಬರ", "ಯೂರಿಯಾ"],
            "weed": ["Weed", "weeder", "pendimethalin", "ಕಳೆ"],
            "protection": ["🔎", "⚠️", "Scout", "Spray", "BSFB", "Blast", "Stem Borer", "Aphids", "Whitefly", "Gall Midge", "BPH", "Tikka", "Rust", "Mosaic", "fungicide", "insecticide", "ಪರಿಶೀಲಿಸಿ", "ಸಿಂಪಡಿಸಿ"],
            "field": ["🚜", "📅", "✂️", "Tractor", "Labor", "Thresher", "Land prep", "puddling", "Transplant", "Sow", "Harvest", "Cut", "Collect", "Dry", "Store", "ಟ್ರಾಕ್ಟರ್", "ಕಾರ್ಮಿಕ", "ಬಿತ್ತನೆ", "ನಾಟಿ", "ಕೊಯ್ಲು"]
        }

        def categorize(text, category):
            if not text or "resting" in text.lower() or "ವಿಶ್ರಾಂತಿ" in text:
                return "No specific activity"
            fragments = text.split("|")
            relevant = [f.strip() for f in fragments if any(k.lower() in f.lower() for k in cat_map[category])]
            return " | ".join(relevant) if relevant else "Standard care"

        def infer_stage(week_idx, text):
            text_l = text.lower()
            if "harvest" in text_l or "cut" in text_l or "store" in text_l: return "Harvest"
            if "mature" in text_l or "yellow" in text_l or "stop watering" in text_l: return "Maturity"
            if "flower" in text_l or "panicle" in text_l or "grain forming" in text_l or "pod" in text_l: return "Reproductive"
            if "transplant" in text_l or "sow" in text_l or "nursery" in text_l or "land prep" in text_l: return "Vegetative"
            return "Vegetative" # Default

        global_week_count = 1
        current_month_name = ""
        from datetime import datetime
        now = datetime.now()
        current_month_idx = now.month # 1-12
        
        # Find if we are in the active season
        # Simple heuristic: if the current month name matches a row in the fetched data
        # This is a bit complex since many crops are multi-month.
        
        processed_timeline = []
        summary_by_month = {}
        
        for row in rows:
            month_name = row['month']
            weeks = []
            major_ops = []
            critical_actions = []
            
            for i in range(1, 5):
                raw_en = row[f'week_{i}']
                raw_loc = row[f'l_week_{i}']
                
                if "resting" in raw_en.lower():
                    continue
                
                # Check for critical icons
                if "⚠️" in raw_en or "critical" in raw_en.lower():
                    critical_actions.append(raw_loc)
                if "📅" in raw_en or "🚜" in raw_en:
                    # Filter major ops to be unique and concise
                    major_ops.append(raw_loc.split("|")[0].strip())

                weeks.append(WeeklyActivity(
                    week_number=global_week_count,
                    field_operation=categorize(raw_loc, "field"),
                    irrigation=categorize(raw_loc, "irrigation"),
                    fertilizer=categorize(raw_loc, "fertilizer"),
                    weed_management=categorize(raw_loc, "weed"),
                    protection=categorize(raw_loc, "protection"),
                    stage=infer_stage(global_week_count, raw_en)
                ))
                global_week_count += 1
            
            if weeks:
                processed_timeline.append(MonthlyActivity(
                    month=month_name,
                    major_operations=list(set(major_ops))[:3], # Top 3
                    critical_actions=list(set(critical_actions))[:2], # Top 2
                    weeks=weeks
                ))
                summary_by_month[month_name] = f"{len([w for w in weeks if w.stage != 'No activity'])} active weeks"

        # Progress Tracker Logic
        # For simplicity, we assume the first month of the list is the start of the crop
        # And we compare with current real-world month.
        import calendar
        month_map = {name: i for i, name in enumerate(calendar.month_name) if name}
        
        start_month_name = processed_timeline[0].month if processed_timeline else "June"
        start_month_idx = month_map.get(start_month_name, 6)
        
        # Calculate current week relative to start month
        months_since_start = (current_month_idx - start_month_idx) % 12
        current_week_num = (months_since_start * 4) + ((now.day - 1) // 7) + 1
        
        # Clamp or find the closest activity
        active_week = None
        for m in processed_timeline:
            for w in m.weeks:
                if w.week_number == current_week_num:
                    active_week = w
                    break
        
        # Fallback to last known if current date is past harvest, or "Upcoming" if before
        if not active_week:
            if current_week_num > global_week_count:
                active_week = processed_timeline[-1].weeks[-1] if processed_timeline else None
            else:
                active_week = processed_timeline[0].weeks[0] if processed_timeline else None

        progress = ProgressTracker(
            current_week=current_week_num if current_week_num < 24 else 0, # Sanity check for crop duration
            current_phase=active_week.stage if active_week else "Planning",
            upcoming_operation=active_week.field_operation if active_week else "Soil preparation"
        )

        response = OperationalPlanResponse(
            context={
                "selected_season": season,
                "selected_crop": crop,
                "selected_variety": variety,
                "total_duration_weeks": global_week_count - 1,
                "language": language
            },
            timeline=processed_timeline,
            summary_by_month=summary_by_month,
            progress=progress
        )

        _cache[cache_key] = response
        logger.info(f"💾 Cache Seeded: {cache_key}")
        return response

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal performance failure: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # use_colors=True and other standard options via uvicorn[standard]
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
