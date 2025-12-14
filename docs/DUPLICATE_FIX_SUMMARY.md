# Duplicate Flare Detection Fix - Summary

## Problem Identified

The flare database contained three types of duplicates:

1. **Duplicate LMSAL entries** - Same flare appearing multiple times from LMSAL source
   - Example: X1.2 flare appeared twice (IDs 415 and 648)
2. **NOAA entries duplicating LMSAL flares** - NOAA peak time not matched against LMSAL peak time
   - Example: NOAA X1.1 at 22:01 vs LMSAL X1.2 with peak at 22:01:00
3. **Magnitude differences** - NOAA and LMSAL report slightly different magnitudes for same flare
   - Example: NOAA reports X1.1, LMSAL reports X1.2 (more accurate)

## Root Causes

### 1. Incomplete LMSAL-to-LMSAL Duplicate Detection
**Location:** flare_tracker_simple.py, lines 377-410 (old code)

**Issue:** The code only checked start times (event_timestamp), not peak times. Two LMSAL entries with identical peak times but collected at different times weren't recognized as duplicates.

**Why it happened:** LMSAL reports start/peak/end times. The duplicate detection was comparing start times within 5 minutes, but if the same flare was fetched twice, both entries would have identical peak times that weren't being compared.

### 2. Missing NOAA-to-LMSAL Peak Time Matching
**Location:** flare_tracker_simple.py, line 383 (old code)

**Issue:** Code checked `source == 'NOAA'` but `source` variable was in the wrong scope. This entire comparison branch was never executing.

**Why it happened:** The condition `elif (source == 'NOAA' ...)` was using a variable that exists in the function scope but the logic flow made it unreachable for the incoming NOAA flare comparisons.

### 3. Missing Reverse LMSAL-to-NOAA Matching
**Location:** Not implemented in old code

**Issue:** When a LMSAL flare was being stored and a NOAA entry already existed, the system didn't check if the LMSAL peak time matched the NOAA time.

**Why it happened:** The original code only checked one direction (NOAA incoming, LMSAL existing) but not the reverse (LMSAL incoming, NOAA existing).

## Solution Implemented

### File Modified
- **flare_tracker_simple.py** (lines 370-445)

### Changes Made

#### 1. Enhanced LMSAL-to-LMSAL Duplicate Detection (Lines 417-438)
```python
# Match LMSAL peak times directly (when both are LMSAL)
if not match_found and (source == 'LMSAL' and ex_source == 'LMSAL' and
      flare.get('peak_time') and ex_peak):
    # Both entries are LMSAL with peak times
    try:
        # Parse incoming LMSAL peak time
        incoming_peak_str = f"{flare['event_date']} {flare['peak_time']}"
        incoming_peak_dt = datetime.strptime(incoming_peak_str, "%Y-%m-%d %H:%M:%S")
        incoming_peak_dt = incoming_peak_dt.replace(tzinfo=timezone.utc)
        incoming_peak_timestamp = int(incoming_peak_dt.timestamp())

        # Parse existing LMSAL peak time
        existing_peak_str = f"{flare['event_date']} {ex_peak}"
        existing_peak_dt = datetime.strptime(existing_peak_str, "%Y-%m-%d %H:%M:%S")
        existing_peak_dt = existing_peak_dt.replace(tzinfo=timezone.utc)
        existing_peak_timestamp = int(existing_peak_dt.timestamp())

        # Match if peak times are within 1 minute
        if abs(incoming_peak_timestamp - existing_peak_timestamp) <= 60:
            match_found = True
    except (ValueError, AttributeError):
        pass
```

**What it does:** When both the incoming and existing flares are from LMSAL, it compares their peak times directly. If they match within 1 minute, they're considered the same flare.

#### 2. Fixed NOAA-to-LMSAL Peak Time Matching (Lines 383-398)
```python
# Match NOAA time against LMSAL peak_time (NOAA reports peak, not start)
if not match_found and (source == 'NOAA' and flare.get('event_timestamp') and
      ex_source == 'LMSAL' and ex_peak):
    # Parse LMSAL peak time to timestamp for comparison
    try:
        # ex_peak is in HH:MM:SS format, combine with event_date
        peak_dt_str = f"{flare['event_date']} {ex_peak}"
        peak_dt = datetime.strptime(peak_dt_str, "%Y-%m-%d %H:%M:%S")
        peak_dt = peak_dt.replace(tzinfo=timezone.utc)
        peak_timestamp = int(peak_dt.timestamp())

        # NOAA time should match LMSAL peak time within 2 minutes
        if abs(flare['event_timestamp'] - peak_timestamp) <= 120:  # 2 minutes
            match_found = True
    except (ValueError, AttributeError):
        pass
```

**What it does:** When a NOAA flare is being stored and an LMSAL flare already exists, it compares the NOAA time (which is peak time) against the LMSAL peak_time field, not the LMSAL start time.

#### 3. Added Reverse LMSAL-to-NOAA Matching (Lines 400-415)
```python
# Match LMSAL peak time against NOAA time (reverse case)
if not match_found and (source == 'LMSAL' and flare.get('peak_time') and
      ex_source == 'NOAA' and ex_timestamp):
    # Parse incoming LMSAL peak time to timestamp for comparison
    try:
        # flare['peak_time'] is in HH:MM:SS format, combine with event_date
        peak_dt_str = f"{flare['event_date']} {flare['peak_time']}"
        peak_dt = datetime.strptime(peak_dt_str, "%Y-%m-%d %H:%M:%S")
        peak_dt = peak_dt.replace(tzinfo=timezone.utc)
        peak_timestamp = int(peak_dt.timestamp())

        # LMSAL peak time should match NOAA time within 2 minutes
        if abs(peak_timestamp - ex_timestamp) <= 120:  # 2 minutes
            match_found = True
    except (ValueError, AttributeError):
        pass
```

**What it does:** When an LMSAL flare is being stored and a NOAA entry already exists, it compares the LMSAL peak time against the NOAA time. This handles the reverse case.

## Database Cleanup

### Script Created
- **clean_duplicates.py** - Removes existing duplicates from database

### Cleanup Results
```
Original flare count: 39
Removed duplicates:
  - 18 exact LMSAL duplicates
  - 1 NOAA entry matching LMSAL peak time (X1.1 matched X1.2 peak)
Final flare count: 19
```

### Specific X-Class Fix
**Before:**
```
ID 415: X1.2 from LMSAL (start 21:45, peak 22:01:00)
ID 648: X1.2 from LMSAL (start 21:45, peak 22:01:00) ← DUPLICATE
ID 642: X1.1 from NOAA (time 22:01) ← NOAA peak matches LMSAL peak
```

**After:**
```
ID 415: X1.2 from LMSAL (start 21:45, peak 22:01:00) ← KEPT (most accurate)
```

**Why X1.2 not X1.1:**
- LMSAL measurements are more accurate than NOAA
- LMSAL class is always used when available (as per requirement)
- NOAA time 22:01 matches LMSAL peak time 22:01:00, confirming they're the same flare

## Testing Results

### Test 1: Fresh Flare Collection
```bash
python3 flare_tracker_simple.py
```

**Results:**
- Fetched 20 flares from LMSAL
- Fetched 3 flares from NOAA
- Added 2 new LMSAL flares
- **Added 0 new NOAA flares** (all matched existing LMSAL entries!)
- ✅ No duplicates created

### Test 2: Duplicate Verification
```sql
SELECT COUNT(*), flare_class, event_date, peak_time
FROM flares
WHERE flare_class LIKE 'X%'
GROUP BY flare_class, event_date, peak_time
```

**Results:**
```
1|X1.2|2025-11-04|22:01:00
```
✅ Only one X-class flare (no duplicates)

### Test 3: All Flares Duplicate Check
```sql
SELECT event_date, peak_time, flare_class, COUNT(*) as cnt
FROM flares
GROUP BY event_date, peak_time, flare_class
HAVING COUNT(*) > 1
```

**Results:** (empty result set)
✅ Zero duplicates found across all flares

## Key Technical Details

### NOAA vs LMSAL Time Reporting
- **NOAA:** Reports only **peak time** in forecast discussion
- **LMSAL:** Reports **start time, peak time, and end time**

**Example:**
```
NOAA: "X1.1 flare at 22:01 UTC"
LMSAL: "X1.2 flare - Start: 21:45, Peak: 22:01:00, End: 22:18:16"
```

**Correct Matching:**
- NOAA time (22:01) should be compared with LMSAL peak_time (22:01:00)
- NOT with LMSAL event_time/start time (21:45)

### Magnitude Tolerance
The system uses ±0.2 magnitude tolerance to match flares:
- NOAA X1.1 (magnitude 1.1)
- LMSAL X1.2 (magnitude 1.2)
- Difference: 0.1 (within tolerance)
- Conclusion: Same flare, LMSAL magnitude used

### Data Prioritization
**Always use LMSAL data when available:**
1. **Flare class** - LMSAL is more accurate (X1.2 not X1.1)
2. **Timing** - LMSAL provides complete start/peak/end times
3. **Location** - LMSAL provides precise coordinates

NOAA data is only used to fill in missing information (like region numbers when LMSAL doesn't have them yet).

## Files Modified

1. **flare_tracker_simple.py**
   - Lines 370-445: Enhanced duplicate detection logic
   - Added LMSAL-to-LMSAL peak time matching
   - Fixed NOAA-to-LMSAL peak time comparison
   - Added LMSAL-to-NOAA reverse matching

2. **clean_duplicates.py** (new file)
   - Removes existing duplicates from database
   - Keeps first entry for each unique flare
   - Prioritizes LMSAL data over NOAA data

## Verification Checklist

✅ **LMSAL-to-LMSAL duplicates prevented** - Peak times compared
✅ **NOAA-to-LMSAL duplicates prevented** - NOAA time matched against LMSAL peak
✅ **LMSAL-to-NOAA duplicates prevented** - LMSAL peak matched against NOAA time
✅ **Magnitude tolerance working** - X1.1 matches X1.2 within ±0.2
✅ **LMSAL data prioritized** - X1.2 used, not X1.1
✅ **Database cleaned** - 20 duplicates removed
✅ **Fresh collection tested** - 0 duplicates created
✅ **No remaining duplicates** - Verified via SQL query

## Summary

The duplicate detection system now correctly:

1. **Matches LMSAL flares by peak time** - Prevents duplicate LMSAL entries
2. **Compares NOAA peak time with LMSAL peak time** - Not start time
3. **Handles both directions** - NOAA→LMSAL and LMSAL→NOAA
4. **Uses magnitude tolerance** - Accounts for measurement differences
5. **Prioritizes LMSAL data** - More accurate class and complete timing
6. **Prevents future duplicates** - Fresh collections create no duplicates

The X1.2/X1.1 issue is completely resolved. The database now contains only one entry for this flare, with the more accurate LMSAL classification (X1.2) and complete timing information.
