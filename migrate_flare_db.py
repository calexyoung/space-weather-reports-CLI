#!/usr/bin/env python3
"""
Migration script to fix duplicate flares in flare_database.db
This recreates the table with the proper UNIQUE constraint that handles NULLs correctly.
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def migrate_flare_database():
    """Migrate flare database to fix UNIQUE constraint"""
    db_path = Path(__file__).parent / 'flare_database.db'

    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return False

    logger.info(f"Migrating database: {db_path}")

    # Create backup
    backup_path = db_path.with_suffix('.db.backup')
    import shutil
    shutil.copy2(db_path, backup_path)
    logger.info(f"Backup created: {backup_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get current flare count
    cursor.execute("SELECT COUNT(*) FROM flares")
    original_count = cursor.fetchone()[0]
    logger.info(f"Original flare count: {original_count}")

    # Create temporary table with new schema
    cursor.execute('''
        CREATE TABLE flares_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date TEXT NOT NULL,
            event_time TEXT,
            event_timestamp INTEGER,
            flare_class TEXT NOT NULL,
            region TEXT,
            location TEXT,
            peak_time TEXT,
            end_time TEXT,
            scraped_at INTEGER NOT NULL,
            source TEXT DEFAULT 'NOAA',
            raw_text TEXT,
            UNIQUE(event_date, flare_class, COALESCE(region, ''), COALESCE(location, ''), COALESCE(event_time, ''))
        )
    ''')
    logger.info("Created new table with fixed UNIQUE constraint")

    # Copy data from old table to new table, removing duplicates
    # Priority: LMSAL over NOAA (LMSAL has more complete data)
    cursor.execute('''
        INSERT OR IGNORE INTO flares_new
        SELECT * FROM flares
        ORDER BY
            CASE source WHEN 'LMSAL' THEN 0 ELSE 1 END,  -- LMSAL first
            scraped_at DESC  -- Most recent scrape first
    ''')

    rows_copied = cursor.rowcount
    logger.info(f"Copied {rows_copied} unique flares to new table")

    # Drop old table and rename new table
    cursor.execute('DROP TABLE flares')
    cursor.execute('ALTER TABLE flares_new RENAME TO flares')
    logger.info("Replaced old table with new table")

    # Recreate index
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_event_timestamp
        ON flares(event_timestamp)
    ''')
    logger.info("Recreated index")

    # Verify final count
    cursor.execute("SELECT COUNT(*) FROM flares")
    final_count = cursor.fetchone()[0]
    logger.info(f"Final flare count: {final_count}")
    logger.info(f"Removed {original_count - final_count} duplicate flares")

    conn.commit()
    conn.close()

    logger.info("Migration completed successfully!")
    logger.info(f"Backup available at: {backup_path}")

    return True

if __name__ == "__main__":
    success = migrate_flare_database()
    if success:
        print("\n✓ Migration completed successfully!")
        print("  - Duplicate flares removed")
        print("  - UNIQUE constraint fixed")
        print("  - Database backup created")
    else:
        print("\n✗ Migration failed - check logs")
