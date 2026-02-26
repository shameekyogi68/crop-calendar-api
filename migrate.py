import csv
import sqlite3
import os

CSV_PATH = 'calendar_bilingual.csv'
DB_PATH = 'calendar.db'

def migrate():
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found. Run generate_bilingual.py first.")
        return

    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing table if exists
    cursor.execute("DROP TABLE IF EXISTS crop_calendar")

    # Create table with bilingual columns
    cursor.execute("""
        CREATE TABLE crop_calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season TEXT,
            crop TEXT,
            variety TEXT,
            month TEXT,
            week_1 TEXT,
            week_2 TEXT,
            week_3 TEXT,
            week_4 TEXT,
            week_1_kn TEXT,
            week_2_kn TEXT,
            week_3_kn TEXT,
            week_4_kn TEXT
        )
    """)

    # Create index for fast lookups
    cursor.execute("CREATE INDEX idx_search ON crop_calendar (season, crop, variety)")

    # Read CSV and Insert Data
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO crop_calendar (
                    season, crop, variety, month, 
                    week_1, week_2, week_3, week_4,
                    week_1_kn, week_2_kn, week_3_kn, week_4_kn
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['Season'].strip(),
                row['Crop'].strip(),
                row['Variety'].strip(),
                row['Month'].strip(),
                row['Week 1'].strip(),
                row['Week 2'].strip(),
                row['Week 3'].strip(),
                row['Week 4'].strip(),
                row['Week 1 (KN)'].strip(),
                row['Week 2 (KN)'].strip(),
                row['Week 3 (KN)'].strip(),
                row['Week 4 (KN)'].strip()
            ))

    conn.commit()
    conn.close()
    print(f"Bilingual Migration successful: {CSV_PATH} -> {DB_PATH}")

if __name__ == "__main__":
    migrate()
