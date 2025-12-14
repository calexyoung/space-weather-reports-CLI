# CME Integration - Phase 2 Complete

## Overview

Phase 2 of the NASA DONKI CME integration has been successfully completed. Monthly export functionality for CME data is now operational, following the same pattern as flare exports.

**Completion Date:** November 3, 2025

---

## What Was Implemented

### Export Methods Added

**1. CSV Export** - `export_monthly_cmes_csv(year_month, output_dir)`
   - Exports CMEs for specified month to CSV file
   - Sequential numbering (#1 to #n)
   - Comprehensive fields for analysis
   - Path: `reports/YYYY-MM/cmes-YYYY-MM.csv`

**2. Markdown Export** - `export_monthly_cmes_markdown(year_month, output_dir)`
   - Exports CMEs to Markdown table format
   - Summary statistics (total, Earth-directed, type breakdown)
   - Clickable NASA alert links
   - CME classification reference guide
   - Path: `reports/YYYY-MM/cmes-YYYY-MM.md`

### File Formats

#### CSV Format

```csv
#,NASA Alert,Activity ID,Start Time,Type,Speed (km/s),Half-Angle (deg),Direction (lon/lat),Detection,Earth Impact,Arrival Time,Uncertainty,Confidence
1,https://kauai.ccmc.gsfc.nasa.gov/DONKI/view/Alert/42304/1,2025-11-01T18:00:00-CME-001,2025-11-01T18:00:00Z,C-type,624,16,-37/-5,STEREO A/GOES/SOHO,Yes,,,
2,https://kauai.ccmc.gsfc.nasa.gov/DONKI/view/Alert/42314/1,2025-11-02T12:23:00-CME-001,2025-11-02T12:23:00Z,C-type,757,38,-73/22,STEREO A/GOES/SOHO,Yes,,,
```

**Fields:**
1. Sequential number
2. NASA Alert URL
3. Activity ID (unique event identifier)
4. Start time (ISO 8601)
5. CME type (S/C/O/R/ER-type)
6. Speed (km/s)
7. Half-angle (degrees)
8. Direction (longitude/latitude)
9. Detection instruments
10. Earth impact (Yes/No)
11. Arrival time (if Earth-directed)
12. Uncertainty window (±hours)
13. Confidence level (Low/Medium/High)

#### Markdown Format

```markdown
# CMEs - November 2025

**Total CMEs:** 4

**Earth-Directed:** 4 CMEs

**Type Breakdown:**
- C-type: 3
- O-type: 1

| # | Start Time | Type | Speed | Half-Angle | Direction | Detection | Earth Impact | Arrival | Confidence | NASA Alert |
|---|------------|------|-------|------------|-----------|-----------|--------------|---------|------------|------------|
| 1 | 2025-11-01T18:00:00Z | C-type | 624 km/s | 16° | -37/-5 | STEREO A/GOES/SOHO | ✓ | TBD |  | [Alert](https://...) |

---

**Data Source:** NASA DONKI (Database Of Notifications, Knowledge, Information)

**CME Speed Classification:**
- S-type: < 500 km/s (Slow)
- C-type: 500-999 km/s (Common)
- O-type: 1000-1999 km/s (Occasional)
- R-type: 2000-2999 km/s (Rare)
- ER-type: > 3000 km/s (Extremely Rare)
```

**Features:**
- Summary statistics at top
- Type breakdown
- Formatted table with all key parameters
- Checkmark (✓) for Earth-directed CMEs
- Clickable NASA alert links
- Classification reference guide at bottom

---

## Test Results

### Export Test - November 2025

**Command:**
```bash
python3 test_cme_export.py
```

**Results:**
```
✓ Exported: reports/2025-10/cmes-2025-10.csv (18 CMEs)
✓ Exported: reports/2025-10/cmes-2025-10.md (18 CMEs)
✓ Exported: reports/2025-11/cmes-2025-11.csv (4 CMEs)
✓ Exported: reports/2025-11/cmes-2025-11.md (4 CMEs)
```

### November 2025 Data Summary

**CMEs Exported:** 4 events
- **C-type:** 3 CMEs (500-999 km/s)
- **O-type:** 1 CME (1000-1999 km/s)
- **Earth-directed:** 4 CMEs (100%)
- **Date range:** Nov 1-3, 2025

**Sample CME:**
```
Start: 2025-11-03T09:36:00Z
Type: O-type
Speed: 1034 km/s
Half-Angle: 45°
Direction: -56/24
Detection: STEREO A/GOES/SOHO
Earth Impact: Yes (arrival TBD)
```

### October 2025 Data Summary

**CMEs Exported:** 18 events
- **C-type:** 14 CMEs
- **O-type:** 4 CMEs
- **Fastest:** O-type at 1250 km/s
- **Date range:** Oct 29-31, 2025

---

## Directory Structure

CME export files follow the same pattern as flare files:

```
reports/
├── 2025-10/
│   ├── cmes-2025-10.csv          ← October CMEs (CSV)
│   ├── cmes-2025-10.md           ← October CMEs (Markdown)
│   ├── flares-2025-10.csv        ← October Flares (CSV)
│   ├── flares-2025-10.md         ← October Flares (Markdown)
│   └── space_weather_*.{html,md,json,txt}
├── 2025-11/
│   ├── cmes-2025-11.csv          ← November CMEs (CSV)
│   ├── cmes-2025-11.md           ← November CMEs (Markdown)
│   ├── flares-2025-11.csv        ← November Flares (CSV)
│   ├── flares-2025-11.md         ← November Flares (Markdown)
│   └── space_weather_*.{html,md,json,txt}
└── 2025-12/
    └── ...
```

**Benefits:**
- Organized by year-month
- CMEs and flares in same directory
- Easy to find related data
- Consistent naming convention

---

## Code Changes

### Files Modified

**[cme_tracker.py](../cme_tracker.py)** - Added export methods (lines 556-774)

1. **`export_monthly_cmes_csv()`** method (lines 556-647)
   - Queries CMEs for specified month
   - Creates CSV with 13 columns
   - Formats direction, Earth impact, arrival predictions
   - Sequential numbering

2. **`export_monthly_cmes_markdown()`** method (lines 649-774)
   - Queries CMEs for specified month
   - Generates header with statistics
   - Creates formatted table
   - Adds classification reference guide
   - Uses checkmarks for Earth-directed CMEs

### Files Created

**[test_cme_export.py](../test_cme_export.py)** - Test script (~80 lines)
- Tests both CSV and Markdown export
- Displays sample output
- Verifies file creation

**Output Files:**
- `reports/2025-10/cmes-2025-10.csv`
- `reports/2025-10/cmes-2025-10.md`
- `reports/2025-11/cmes-2025-11.csv`
- `reports/2025-11/cmes-2025-11.md`

---

## Usage Examples

### Export Current Month

```python
from cme_tracker import CMETracker
from datetime import datetime

tracker = CMETracker()
current_month = datetime.now().strftime('%Y-%m')

csv_file = tracker.export_monthly_cmes_csv(current_month)
md_file = tracker.export_monthly_cmes_markdown(current_month)

print(f"CSV: {csv_file}")
print(f"MD: {md_file}")
```

### Export Specific Month

```python
tracker = CMETracker()

# Export November 2025
csv_file = tracker.export_monthly_cmes_csv('2025-11')
md_file = tracker.export_monthly_cmes_markdown('2025-11')
```

### Batch Export Multiple Months

```python
tracker = CMETracker()

months = ['2025-09', '2025-10', '2025-11']
for month in months:
    csv = tracker.export_monthly_cmes_csv(month)
    md = tracker.export_monthly_cmes_markdown(month)
    if csv:
        print(f"Exported: {month}")
```

### Custom Output Directory

```python
tracker = CMETracker()

# Export to custom location
csv_file = tracker.export_monthly_cmes_csv(
    '2025-11',
    output_dir='/path/to/custom/reports'
)
```

---

## Comparison with Flare Files

Both flare and CME export systems follow the same design pattern:

| Feature | Flares | CMEs |
|---------|--------|------|
| **Format** | CSV + Markdown | CSV + Markdown |
| **Location** | `reports/YYYY-MM/` | `reports/YYYY-MM/` |
| **Naming** | `flares-YYYY-MM.{csv,md}` | `cmes-YYYY-MM.{csv,md}` |
| **Numbering** | Sequential (#1 to #n) | Sequential (#1 to #n) |
| **Summary** | In Markdown header | In Markdown header |
| **Links** | LMSAL event archive | NASA DONKI alerts |
| **Auto-update** | On scrape | On fetch |

**Key Differences:**
- **Flares:** Include peak time, end time, active region
- **CMEs:** Include speed, half-angle, direction, Earth impact predictions
- **Flares:** Link to LMSAL event pages
- **CMEs:** Link to NASA DONKI alerts

---

## Integration Points

### Future Integration Steps

1. **Automated Export** - Add to `space_weather_automation.py`
   - Call export methods after CME collection
   - Regenerate monthly files on each run
   - Similar to flare export integration

2. **Report Inclusion** - Add CME data to space weather reports
   - Display recent CMEs in report sections
   - Highlight Earth-directed events
   - Show arrival predictions

3. **Scheduler** - Include in scheduled runs
   - Fetch CME data daily
   - Export monthly files automatically
   - Update reports with latest CME info

### Example Integration Pattern

```python
# In space_weather_automation.py
from cme_tracker import CMETracker

def collect_and_export_cmes(self):
    """Collect CME data and export monthly files"""
    tracker = CMETracker()

    # Fetch recent CMEs
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=7)
    notifications = tracker.fetch_cme_notifications(
        start_date.strftime('%Y-%m'),
        end_date.strftime('%Y-%m')
    )

    # Store in database
    tracker.store_cmes(notifications)

    # Export current month
    current_month = end_date.strftime('%Y-%m')
    tracker.export_monthly_cmes_csv(current_month)
    tracker.export_monthly_cmes_markdown(current_month)

    # Get recent for report
    return tracker.get_recent_cmes(hours=168)
```

---

## Known Issues and Limitations

### Current Limitations

1. **Arrival Time Data:** Many CMEs show "TBD" for arrival time
   - NASA may not provide predictions for all CMEs
   - Only significant Earth-directed CMEs get detailed predictions
   - This is expected behavior based on DONKI data

2. **Confidence Levels:** Often empty in current data
   - Depends on NASA modeling completion
   - Updates may come after initial alert
   - Future versions could check for updates

3. **Imagery Links:** Not yet parsed
   - Field exists in database
   - Regex patterns ready
   - Needs testing with more diverse notifications

### Future Enhancements

1. **Auto-update from alerts** - Poll for updated predictions
2. **CME-Flare linking** - Associate CMEs with source flares
3. **Arrival notifications** - Alert when CME arrival is imminent
4. **Historical charts** - Visualize CME frequency and speed trends

---

## Testing

### Test Script

**File:** [test_cme_export.py](../test_cme_export.py)

**What it tests:**
- Database connectivity
- CSV export functionality
- Markdown export functionality
- File creation in correct directories
- Data formatting
- Summary statistics

**Run test:**
```bash
python3 test_cme_export.py
```

**Expected output:**
```
✓ Created: reports/YYYY-MM/cmes-YYYY-MM.csv
✓ Created: reports/YYYY-MM/cmes-YYYY-MM.md
✓ CME EXPORT TEST COMPLETE
```

### Manual Verification

```bash
# Check files exist
ls -l reports/2025-11/cmes-*

# View CSV
head reports/2025-11/cmes-2025-11.csv

# View Markdown
cat reports/2025-11/cmes-2025-11.md

# Count CMEs
wc -l reports/2025-11/cmes-2025-11.csv
```

---

## Next Steps

### Phase 3: Report Integration

**Tasks:**
1. Add `collect_cme_data()` to `space_weather_automation.py`
2. Update HTML report template with CME section
3. Update Markdown report template with CME section
4. Update JSON/text formats to include CME data
5. Test full report generation with CME data

**Estimated Time:** 2-3 hours

### Phase 4: Configuration & Documentation

**Tasks:**
1. Add CME settings to `config.yaml`
2. Update `scheduler.py` for CME collection
3. Create user documentation (`docs/CME_TRACKING.md`)
4. Update main README with CME features
5. Create quickstart guide for CME tracking

**Estimated Time:** 1-2 hours

---

## Summary

**Phase 2 Status:** ✅ COMPLETE

**Achievements:**
- ✅ CSV export method implemented and tested
- ✅ Markdown export method implemented and tested
- ✅ Files created in correct directory structure
- ✅ Data formatting matches flare file style
- ✅ Summary statistics included
- ✅ Test script created and passing
- ✅ October and November 2025 files generated

**Lines of Code Added:** ~220 lines

**Test Results:** All tests passing

**Files Generated:**
- `reports/2025-10/cmes-2025-10.csv` (18 CMEs)
- `reports/2025-10/cmes-2025-10.md` (18 CMEs)
- `reports/2025-11/cmes-2025-11.csv` (4 CMEs)
- `reports/2025-11/cmes-2025-11.md` (4 CMEs)

**Ready for:** Phase 3 (Report Integration)

---

**Completion Date:** November 3, 2025
**Status:** ✅ PHASE 2 COMPLETE - READY FOR PHASE 3
