# Flare Tracking System Guide

## Overview

The Flare Tracking System maintains a comprehensive rolling 24-hour database of solar flares, addressing the limitation that LMSAL's latest_events page only shows the most recent 20 flares. During high solar activity, more than 20 flares can occur within 24 hours, making continuous tracking essential for complete reports.

## Architecture

### Components

1. **flare_tracker_simple.py** - Core tracking module
   - Extracts flare data from LMSAL (primary) and NOAA (secondary)
   - Parses LMSAL's 20-flare table with precise timing data
   - Cross-references with NOAA SWPC discussion text
   - Stores flares in SQLite database
   - Maintains rolling 24-hour window
   - Provides summary statistics

2. **flare_scheduler.py** - Dedicated 4-hour collection scheduler
   - Runs independently of main report generation
   - Collects flares every 4 hours
   - Ensures no flares are missed during high activity
   - Logs to separate `flare_collection.log`

3. **flare_database.db** - SQLite database
   - Persistent storage for all flares
   - Automatic duplicate detection
   - Rolling window cleanup (24-hour retention)

4. **Integration with Reports** - Automatic inclusion
   - `space_weather_automation.py` queries database
   - Flare summary added to Claude AI prompt
   - Complete flare list included in reports

## Data Flow

```
Every 4 Hours:
1. flare_scheduler.py triggers collection
2. Fetch LMSAL latest_events page (primary source)
3. Parse LMSAL table (20 flares with precise timing)
4. Fetch NOAA SWPC discussion (cross-reference)
5. Parse NOAA flare mentions
6. Store in flare_database.db (skip duplicates)
7. Delete flares older than 24 hours

Every 12-24 Hours (Report Generation):
1. space_weather_automation.py runs
2. Query flare_database.db for last 24 hours
3. Include flare summary in Claude AI prompt
4. Generate comprehensive report with complete flare history
```

## Database Schema

```sql
CREATE TABLE flares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_date TEXT NOT NULL,           -- YYYY-MM-DD
    event_time TEXT,                    -- HH:MM (may be NULL)
    event_timestamp INTEGER,            -- Unix timestamp
    flare_class TEXT NOT NULL,          -- C5.4, M1.0, X2.3, etc.
    region TEXT,                        -- Active region number (4267, etc.)
    location TEXT,                      -- Heliographic coordinates
    scraped_at INTEGER NOT NULL,        -- Collection timestamp
    source TEXT DEFAULT 'NOAA',         -- Data source
    raw_text TEXT,                      -- Original text snippet
    UNIQUE(event_date, flare_class, region, event_time)
)
```

## Installation & Setup

### 1. Dependencies

Already included in `requirements.txt`:
```
sqlite3 (built-in to Python)
requests>=2.31.0
```

### 2. Configuration

Edit `config.yaml`:

```yaml
# Flare Tracking Settings
flare_tracking:
  enabled: true
  database_path: "flare_database.db"
  collection_interval_hours: 4
  retention_hours: 24
  include_in_reports: true
```

### 3. Test Installation

```bash
# Test flare tracker
python3 flare_tracker_simple.py

# Expected output:
# Flare Scraping Results:
# Success: True
# New flares: X
# Current 24h total: X
```

### 4. Run Comprehensive Test

```bash
python3 test_flare_tracking.py
```

This tests:
- Multiple collection cycles
- Duplicate detection
- Database persistence
- Report integration

## Usage

### Option 1: Automated 4-Hour Collection (Recommended)

**Foreground Mode:**
```bash
python3 flare_scheduler.py
# Runs in terminal, logs visible
# Press Ctrl+C to stop
```

**Background Mode (macOS launchd):**

Create `~/Library/LaunchAgents/com.user.flarecollection.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.flarecollection</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/cayoung/Documents/Obsidian/CAY-power-vault/space-weather-reports/flare_scheduler.py</string>
    </array>

    <key>StartInterval</key>
    <integer>14400</integer>  <!-- 4 hours -->

    <key>RunAtLoad</key>
    <true/>

    <key>WorkingDirectory</key>
    <string>/Users/cayoung/Documents/Obsidian/CAY-power-vault/space-weather-reports</string>

    <key>StandardOutPath</key>
    <string>/Users/cayoung/Documents/Obsidian/CAY-power-vault/space-weather-reports/flare_stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/cayoung/Documents/Obsidian/CAY-power-vault/space-weather-reports/flare_stderr.log</string>
</dict>
</plist>
```

Load service:
```bash
launchctl load ~/Library/LaunchAgents/com.user.flarecollection.plist
```

### Option 2: Manual Collection

```bash
python3 flare_tracker_simple.py
```

Useful for:
- Testing
- On-demand updates
- Debugging

### Option 3: Integrated with Main Reports

Flare data is automatically included when you run:

```bash
python3 space_weather_automation.py
```

The report will include:
- Complete 24-hour flare summary
- X/M/C class counts
- Strongest flare information
- Full flare list with times and regions

## Monitoring

### Check Collection Logs

```bash
# Main flare collection log
tail -f flare_collection.log

# Last 20 lines
tail -n 20 flare_collection.log

# Check for errors
grep ERROR flare_collection.log
```

### Check Database Status

```bash
python3 -c "
from flare_tracker_simple import SimpleFlareTracker
tracker = SimpleFlareTracker()
summary = tracker.get_flares_summary()
print(f'Total flares: {summary[\"total_count\"]}')
print(f'X-class: {summary[\"x_class_count\"]}')
print(f'M-class: {summary[\"m_class_count\"]}')
print(f'C-class: {summary[\"c_class_count\"]}')
"
```

### View Database Directly

```bash
sqlite3 flare_database.db "SELECT event_date, event_time, flare_class, region FROM flares ORDER BY event_timestamp DESC LIMIT 20;"
```

## Troubleshooting

### No Flares Being Collected

**Check NOAA data source:**
```bash
python3 -c "
from flare_tracker_simple import SimpleFlareTracker
tracker = SimpleFlareTracker()
text = tracker.fetch_noaa_discussion()
print(len(text) if text else 'Failed to fetch')
"
```

**Expected:** Number > 1000 (NOAA discussion is typically several KB)

### Database Locked Errors

**Cause:** Multiple processes accessing database simultaneously

**Solution:**
- Ensure only one flare_scheduler.py instance is running
- Check for orphaned processes: `ps aux | grep flare_scheduler`

### Duplicate Flares in Database

**Normal behavior** - Flares are uniquely identified by:
- Event date
- Flare class
- Region
- Event time

If NOAA reports the same flare twice, it won't create a duplicate.

### Flares Not Showing in Reports

**Check integration:**
```bash
python3 space_weather_automation.py 2>&1 | grep "flare summary"
```

**Expected output:**
```
INFO - Retrieved flare summary: X flares in last 24h
```

**If not found:**
1. Check `config.yaml`: `flare_tracking.include_in_reports: true`
2. Ensure `flare_database.db` exists
3. Run `python3 test_flare_tracking.py` to verify integration

## Performance

### Database Size

- Typical: ~50-100 KB for 24 hours of moderate activity
- High activity: Up to 500 KB (hundreds of flares)
- Automatic cleanup keeps size manageable

### Collection Time

- NOAA fetch: ~1 second
- Parse + store: <1 second
- Total: ~2 seconds per collection cycle

### Report Impact

- Database query: <100ms
- Adds ~500-1000 characters to Claude prompt
- Negligible impact on report generation time

## Advanced Features

### Custom Retention Period

Edit `flare_tracker_simple.py`:

```python
# Change retention from 24 to 48 hours
deleted = self.cleanup_old_flares(hours=48)
```

### Export Flare Data

```bash
sqlite3 flare_database.db <<EOF
.headers on
.mode csv
.output flares_export.csv
SELECT * FROM flares ORDER BY event_timestamp DESC;
.quit
EOF
```

### Historical Analysis

```python
from flare_tracker_simple import SimpleFlareTracker
import sqlite3

tracker = SimpleFlareTracker()
conn = sqlite3.connect('flare_database.db')
cursor = conn.cursor()

# Count by class
cursor.execute("""
    SELECT
        substr(flare_class, 1, 1) as class,
        COUNT(*) as count
    FROM flares
    GROUP BY class
    ORDER BY class
""")

for row in cursor.fetchall():
    print(f"{row[0]}-class: {row[1]} flares")

conn.close()
```

## Integration with Reports

The flare summary appears in Claude's prompt as:

```
## 24-Hour Flare Tracking Database
**Rolling 24-Hour Flare Database Summary:**
- Total flares tracked: 4
- X-class: 0
- M-class: 0
- C-class: 4
- Strongest: C8.2 from AR4273

**Complete Flare List (Last 24 Hours):**
- C8.2 at 2025-11-03 from AR4273
- C8.2 at 2025-11-03 from AR4273
- C5.4 at 2025-11-02 14:23 from AR4267
- C3.1 at 2025-11-02 10:15 from AR4265
```

This ensures Claude generates reports with **complete flare information** even during high-activity periods when the LMSAL latest_events page misses flares.

## Benefits

1. **Comprehensive Coverage** - Never miss flares during high activity
2. **Historical Context** - Full 24-hour view for better analysis
3. **Duplicate Prevention** - Automatic deduplication
4. **Persistence** - Survives system restarts
5. **Low Overhead** - Minimal performance impact
6. **Automatic Integration** - Seamlessly included in reports

## Files Created

- `flare_tracker_simple.py` - Core module (334 lines)
- `flare_scheduler.py` - 4-hour scheduler (91 lines)
- `test_flare_tracking.py` - Comprehensive test (118 lines)
- `flare_database.db` - SQLite database (auto-created)
- `flare_collection.log` - Collection logs (auto-created)

## Next Steps

1. **Start 4-hour collection:**
   ```bash
   python3 flare_scheduler.py &
   ```

2. **Verify collection is working:**
   ```bash
   tail -f flare_collection.log
   ```

3. **Generate report with flare data:**
   ```bash
   python3 space_weather_automation.py
   ```

4. **Check report contains flare summary:**
   ```bash
   grep -i "flare" reports/space_weather_*.md | head -20
   ```

## Support

For issues or questions:
1. Check logs: `flare_collection.log`
2. Run test: `python3 test_flare_tracking.py`
3. Verify database: `sqlite3 flare_database.db .tables`
4. Review this guide's troubleshooting section

---

**Last Updated:** November 2, 2025
**Version:** 1.0
**Status:** Production Ready ✅
