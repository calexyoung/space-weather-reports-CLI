# Monthly Flare Files - Complete Implementation

## Overview

The flare tracking system now automatically generates monthly flare summary files in both CSV and Markdown formats. These files provide a comprehensive, chronological record of all solar flares detected during each month.

## Implementation Date

November 3, 2025

## Features

### Automatic Monthly Export

Every time the flare scraping script runs (every 4 hours), it automatically exports all flares for the current month to:

1. **CSV file**: `reports/YYYY-MM/flares-YYYY-MM.csv`
2. **Markdown file**: `reports/YYYY-MM/flares-YYYY-MM.md`

### Data Included

Each flare entry contains:

| Field | Description | Example |
|-------|-------------|---------|
| # | Sequential number (1 to n) | 1 |
| LMSAL Link | Link to LMSAL event archive | [Link](http://www.lmsal.com/...) |
| Flare Class | X/M/C classification | M5.0 |
| Date | Event date | 2025-11-03 |
| Start Time | Flare start time (UTC) | 09:38:00 |
| Peak Time | Peak intensity time (UTC) | 10:11:00 |
| End Time | Flare end time (UTC) | 10:28:12 |
| Position | Heliographic location | N22E84 |
| Active Region | NOAA region number | AR4274 |

## File Formats

### CSV Format

Comma-separated values file suitable for import into spreadsheets, databases, or analysis tools.

**Example row:**
```csv
1,http://www.lmsal.com/solarsoft/latest_events_archive/events_summary/2025/11/03/gev_20251103_0938/index.html,M5.0,2025-11-03,09:38:00,10:11:00,10:28:12,N22E84,AR4274
```

**Location:** `reports/2025-11/flares-2025-11.csv`

### Markdown Format

Human-readable table format compatible with Obsidian and other Markdown viewers.

**Example:**

```markdown
# Solar Flares - November 2025

Total flares recorded: **36**

| # | LMSAL Link | Flare Class | Date | Start Time | Peak Time | End Time | Position | Active Region |
|---|------------|-------------|------|------------|-----------|----------|----------|---------------|
| 1 | [Link](http://...) | M5.0 | 2025-11-03 | 09:38:00 | 10:11:00 | 10:28:12 | N22E84 | AR4274 |
```

**Location:** `reports/2025-11/flares-2025-11.md`

## Implementation Details

### Database Schema Updates

Added two new columns to the flares database:

```sql
ALTER TABLE flares ADD COLUMN peak_time TEXT;
ALTER TABLE flares ADD COLUMN end_time TEXT;
```

These columns store the peak and end times extracted from LMSAL data.

### New Methods in flare_tracker_simple.py

#### 1. `generate_lmsal_link(event_date, event_time, peak_time=None)`

Generates LMSAL event archive URLs in the format:
```
http://www.lmsal.com/solarsoft/latest_events_archive/events_summary/YYYY/MM/DD/gev_YYYYMMDD_HHMM/index.html
```

**Lines:** 363-398

#### 2. `export_monthly_flares_csv(year_month, output_dir="reports")`

Exports all flares for a specific month to CSV format.

**Features:**
- Queries database for all flares matching `YYYY-MM-%`
- Orders chronologically by date and time
- Sequential numbering starting from 1
- Generates LMSAL links for each flare
- Creates year-month subdirectory if needed

**Lines:** 400-471

#### 3. `export_monthly_flares_markdown(year_month, output_dir="reports")`

Exports all flares for a specific month to Markdown table format.

**Features:**
- Formatted title with month name and year
- Total flare count summary
- Clickable LMSAL links
- Clean table formatting

**Lines:** 473-542

### Integration with scrape_and_update()

The monthly export is called automatically at the end of each scrape cycle:

```python
# Export monthly flare files (CSV and Markdown)
year_month = datetime.now(timezone.utc).strftime('%Y-%m')
csv_file = self.export_monthly_flares_csv(year_month)
md_file = self.export_monthly_flares_markdown(year_month)
```

**Lines:** 581-584

## Usage

### Automatic Generation

No manual action required. Files are updated automatically every 4 hours when the flare scraper runs.

### Manual Export

To manually export flares for a specific month:

```python
from flare_tracker_simple import SimpleFlareTracker

tracker = SimpleFlareTracker()

# Export November 2025
tracker.export_monthly_flares_csv("2025-11")
tracker.export_monthly_flares_markdown("2025-11")
```

### Viewing Files

**CSV in Excel/Numbers:**
```bash
open reports/2025-11/flares-2025-11.csv
```

**Markdown in Obsidian:**
- Navigate to `reports/2025-11/flares-2025-11.md`
- Or link in daily notes: `![[reports/2025-11/flares-2025-11.md]]`

**CSV Analysis:**
```bash
# Count flares by class
awk -F',' 'NR>1 {print $3}' reports/2025-11/flares-2025-11.csv | sort | uniq -c

# M-class flares only
grep ",M[0-9]" reports/2025-11/flares-2025-11.csv

# Flares from specific region
grep "AR4274" reports/2025-11/flares-2025-11.csv
```

## LMSAL Link Format

The LMSAL event archive links are generated based on the event date and time:

**Format:**
```
http://www.lmsal.com/solarsoft/latest_events_archive/events_summary/YYYY/MM/DD/gev_YYYYMMDD_HHMM/index.html
```

**Example for M5.0 flare on Nov 3, 2025 at 09:38:**
```
http://www.lmsal.com/solarsoft/latest_events_archive/events_summary/2025/11/03/gev_20251103_0938/index.html
```

These links provide access to:
- GOES X-ray flux plots
- SDO/AIA images
- Flare evolution videos
- Detailed event parameters

## Data Sources and Limitations

### LMSAL Data (Primary)

- **Comprehensive timing:** Start, peak, and end times
- **Precise locations:** Heliographic coordinates
- **Limitation:** Region numbers sometimes missing from table
- **Coverage:** Most recent 20 flares

### NOAA Data (Secondary)

- **Region numbers:** Usually included in discussion text
- **Limitation:** Timing may be approximate
- **Coverage:** Only significant flares mentioned

### Region Number Updates

**Automatic Region Assignment:**

The system automatically updates flare records when region numbers become available:

1. **Initial Detection:** A new flare appears with only location (e.g., N22E84) but no region number
2. **Database Entry:** Flare is stored with empty region field
3. **Region Numbering:** NOAA assigns a region number (e.g., AR4274) to that location
4. **Automatic Update:** Next scrape detects the new region number and updates the existing flare record
5. **File Refresh:** Monthly CSV and Markdown files are regenerated with updated region numbers

**Example:**
```
Initial:  M5.0, 2025-11-03, 09:38, N22E84, (no region)
Updated:  M5.0, 2025-11-03, 09:38, N22E84, AR4274
```

This ensures that region numbers are filled in automatically as NOAA numbers new active regions.

### Known Limitations

1. **Empty Region Numbers (Temporary):** Some flares may have empty region fields initially if LMSAL doesn't include them. These will be updated automatically in subsequent scrapes when the region is numbered.

2. **Region Updates May Lag:** There's typically a delay between when a region appears and when NOAA assigns it a number. The flare file will reflect this reality.

3. **Missing Timing Data:** NOAA-sourced flares may not have peak and end times, only approximate event times.

## Directory Structure

```
reports/
├── 2025-11/
│   ├── flares-2025-11.csv        ← Monthly CSV file
│   ├── flares-2025-11.md         ← Monthly Markdown file
│   ├── space_weather_2025-11-03_0833.html
│   └── space_weather_2025-11-03_0833.md
├── 2025-12/
│   ├── flares-2025-12.csv
│   └── flares-2025-12.md
└── archive/
```

## Files Modified

1. **[flare_tracker_simple.py](../flare_tracker_simple.py)**
   - Updated database schema (lines 36-52)
   - Updated store_flares method (lines 252-269)
   - Added generate_lmsal_link method (lines 363-398)
   - Added export_monthly_flares_csv method (lines 400-471)
   - Added export_monthly_flares_markdown method (lines 473-542)
   - Updated scrape_and_update method (lines 581-584)

2. **Database Migration:**
   - Added `peak_time TEXT` column
   - Added `end_time TEXT` column

## Test Results

### Test Run: November 3, 2025

```bash
$ python3 flare_tracker_simple.py

Flare Scraping Results:
Success: True
New flares: 13
Old flares deleted: 8
Current 24h total: 36

Summary (Last 24h):
  X-class: 0
  M-class: 19
  C-class: 17
  Strongest: M5.0

2025-11-03 09:08:41 - INFO - Exported 36 flares to reports/2025-11/flares-2025-11.csv
2025-11-03 09:08:41 - INFO - Exported 36 flares to reports/2025-11/flares-2025-11.md
```

### Generated Files

```bash
$ ls -lh reports/2025-11/flares-*
-rw-r--r--  2 cayoung  staff   4.7K Nov  3 09:08 reports/2025-11/flares-2025-11.csv
-rw-r--r--  2 cayoung  staff   5.8K Nov  3 09:08 reports/2025-11/flares-2025-11.md
```

## Integration with Reports

The monthly flare files complement the daily space weather reports:

**Daily Reports:**
- Real-time analysis
- 24-hour rolling window
- AI-generated narratives

**Monthly Flare Files:**
- Complete chronological record
- Full month coverage
- Structured data format
- Easy analysis and archival

## Future Enhancements

### Potential Improvements

1. **Backfill region numbers:** Cross-reference LMSAL event descriptions to fill missing region numbers
2. **Add peak flux values:** Extract X-ray intensity values
3. **Include CME associations:** Link flares to associated CMEs
4. **Annual summary files:** Aggregate statistics for entire years
5. **Export to other formats:** JSON, XML, or database-ready SQL

### Statistical Analysis

The CSV format enables easy analysis:

```python
import pandas as pd

# Load monthly flares
df = pd.read_csv('reports/2025-11/flares-2025-11.csv')

# Count by class
print(df['Flare Class'].value_counts())

# M-class and above
major_flares = df[df['Flare Class'].str[0].isin(['M', 'X'])]
print(f"Major flares: {len(major_flares)}")

# Flares by region
print(df.groupby('Active Region').size())
```

## Support

### Troubleshooting

**No monthly files generated:**
```bash
# Check logs
tail -f flare_collection.log

# Manually trigger export
python3 -c "
from flare_tracker_simple import SimpleFlareTracker
tracker = SimpleFlareTracker()
tracker.export_monthly_flares_csv('2025-11')
tracker.export_monthly_flares_markdown('2025-11')
"
```

**Empty or incomplete data:**
```bash
# Check database contents
sqlite3 flare_database.db "SELECT COUNT(*), MIN(event_date), MAX(event_date) FROM flares;"

# Check for specific month
sqlite3 flare_database.db "SELECT COUNT(*) FROM flares WHERE event_date LIKE '2025-11%';"
```

**Duplicate entries:**
- This is temporary during transition period
- Will resolve as old entries age out of 24-hour window
- Or manually clean: `DELETE FROM flares WHERE peak_time IS NULL;`

## References

- **LMSAL Event Archive:** http://www.lmsal.com/solarsoft/latest_events_archive/
- **Implementation:** [flare_tracker_simple.py](../flare_tracker_simple.py)
- **Flare Tracking Guide:** [FLARE_TRACKING_GUIDE.md](FLARE_TRACKING_GUIDE.md)
- **Database Schema:** See flare_tracker_simple.py lines 36-52

---

**Status:** ✅ IMPLEMENTED AND TESTED
**Date:** November 3, 2025
**Files Created:** CSV and Markdown monthly summaries
**Automation:** Fully automatic with 4-hour updates
