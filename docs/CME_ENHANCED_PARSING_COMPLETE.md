# CME Enhanced Parsing - Phase 2.5 Complete

## Overview

Based on detailed analysis of NASA DONKI CME data for November 2, 2025, the CME tracking system has been enhanced to capture additional data elements that were missing from the initial implementation.

**Completion Date:** November 3, 2025

---

## Enhancements Implemented

### 1. Database Schema Updates

**File:** `cme_tracker.py` - `_init_database()` method

**New Fields Added:**
- `affected_spacecraft` (TEXT) - Non-Earth targets (BepiColombo, Parker Solar Probe, etc.)
- `associated_flare` (TEXT) - Linked solar flare information
- `is_multi_cme` (INTEGER) - Flag for notifications containing multiple CMEs
- `submitted_by` (TEXT) - Analyst attribution (placeholder for future use)

**Schema Changes:**
```sql
-- Spacecraft impacts (non-Earth)
affected_spacecraft TEXT,

-- Associated events
associated_flare TEXT,
is_multi_cme INTEGER DEFAULT 0,

-- Reference data (updated)
submitted_by TEXT
```

### 2. Enhanced Parsing Logic

**File:** `cme_tracker.py` - `parse_cme_body()` method

#### A. Spacecraft Target Extraction

**Patterns Matched:**
- "may impact BepiColombo"
- "will reach Parker Solar Probe at"
- "BepiColombo AND Parker Solar Probe"

**Implementation:**
```python
spacecraft_patterns = [
    r'impact\s+([\w\s]+?)(?:\s+\(|\.|\s+at)',
    r'reach\s+([\w\s]+?)\s+at',
]
```

**Result:** Successfully extracts multiple spacecraft names from compound statements

#### B. Multi-CME Detection

**Patterns Matched:**
- "Multiple CMEs have been detected as follows:"
- Numbered list format: "1: C-type CME...\n2: C-type CME..."

**Implementation:**
```python
is_multi = bool(re.search(r'Multiple CMEs|(?:^|\n)\d+:\s*\w+-type CME', message_body, re.MULTILINE))
```

**Result:** Correctly identifies notifications containing 2+ CMEs

#### C. Associated Flare Information

**Patterns Matched:**
- "C8.2 flare from an unnumbered region rotating onto the Earth-facing disk ... peaked at 2025-11-02T12:46Z"
- "M5.0 flare from AR4274 peaked at 2025-11-03T10:11Z"

**Implementation:**
```python
flare_pattern = r'([ABCMX]\d+\.?\d*)\s+flare\s+from\s+([^\n]+?)(?:with ID|which peaked)'
# Extracts: flare class, region (AR number or "unnumbered"), peak time
```

**Result:** Captures flare context including class, region, and peak time

#### D. Improved Model Visualization Links

**Additional Patterns:**
```python
link_patterns = [
    r'http://iswa\.gsfc\.nasa\.gov/downloads/[^\s\)]+',  # ISWA ENLIL products
    r'https?://[^\s\)]+\.(?:png|jpg|jpeg|gif|mp4)',
    r'https?://ccmc\.gsfc\.nasa\.gov/[^\s\)]+',
    r'https?://sohowww\.nascom\.nasa\.gov/[^\s\)]+',
]
```

**Result:** Captures 4-5 model visualization URLs per CME

### 3. Storage Updates

**File:** `cme_tracker.py` - `store_cmes()` method

**Updated INSERT Statement:**
- Added 4 new fields to INSERT query
- Updated value count from 24 to 28 parameters
- Proper handling of boolean flags (is_multi_cme)

### 4. Export Format Updates

#### CSV Export

**New Columns Added:**
- `Spacecraft` - Comma-separated list of affected spacecraft
- `Associated Flare` - Flare class, region, and peak time
- `Multi-CME` - "Yes" if notification contains multiple CMEs

**Updated Header:**
```csv
#,NASA Alert,Activity ID,Start Time,Type,Speed (km/s),Half-Angle (deg),Direction (lon/lat),Detection,Earth Impact,Arrival Time,Uncertainty,Confidence,Spacecraft,Associated Flare,Multi-CME
```

#### Markdown Export

**New Columns Added:**
- `Spacecraft` - Shows target spacecraft
- `Flare` - Shows associated flare information
- `Multi` - Checkmark (✓) if multi-CME notification
- `Alert` - Shortened to "Link" for space

**Updated Table Structure:**
```markdown
| # | Start Time | Type | Speed | Half-Angle | Direction | Detection | Earth Impact | Arrival | Confidence | Spacecraft | Flare | Multi | Alert |
```

---

## Test Results - November 2, 2025

### Test Data Summary

**Date Range:** November 2, 2025
**Notifications:** 3 CME notifications
**Total CME Events:** At least 4 individual CMEs (notification #3 contains 2 CMEs)

### Verification Results

#### CME #1 (20251102-AL-001)

| Field | Value |
|-------|-------|
| **Start** | 2025-11-01T18:00:00Z |
| **Type** | C-type (624 km/s) |
| **Earth Impact** | Yes |
| **Spacecraft** | BepiColombo ✓ |
| **Associated Flare** | (none) |
| **Multi-CME** | No |
| **Model Links** | 4 visualizations ✓ |

#### CME #2 (20251102-AL-003)

| Field | Value |
|-------|-------|
| **Start** | 2025-11-02T12:23:00Z |
| **Type** | C-type (757 km/s) |
| **Earth Impact** | Yes |
| **Spacecraft** | BepiColombo, Parker Solar Probe ✓ |
| **Associated Flare** | **C8.2 from unnumbered region, peaked 2025-11-02T12:46Z** ✓ |
| **Multi-CME** | No |
| **Model Links** | 5 visualizations ✓ |

#### CME #3 (20251102-AL-004)

| Field | Value |
|-------|-------|
| **Start** | 2025-11-02T15:36:00Z |
| **Type** | C-type (536 km/s) |
| **Earth Impact** | Yes |
| **Spacecraft** | BepiColombo ✓ |
| **Associated Flare** | (none) |
| **Multi-CME** | **Yes** ✓ (contains 2 CMEs) |
| **Model Links** | 4 visualizations ✓ |

### Enhanced Feature Verification

✅ **Spacecraft Targets**
- Single: "BepiColombo" (CME #1, #3)
- Multiple: "BepiColombo, Parker Solar Probe" (CME #2)

✅ **Associated Flare Information**
- CME #2: "C8.2 from unnumbered region, peaked 2025-11-02T12:46Z"
- Correctly handles unnumbered regions
- Extracts peak time

✅ **Multi-CME Detection**
- CME #3 flagged as multi-CME notification
- Notification contained 2 separate CME events:
  - 2025-11-02T15:36:00Z (C-type, 536 km/s)
  - 2025-11-02T16:36:00Z (C-type, 500 km/s)

✅ **Model Visualization Links**
- 4-5 ENLIL model URLs per notification
- ISWA downloads correctly extracted
- Format: `http://iswa.gsfc.nasa.gov/downloads/[date]_[time]_[version]_*.gif`

---

## Output Examples

### CSV Format

```csv
#,NASA Alert,Activity ID,Start Time,Type,Speed (km/s),Half-Angle (deg),Direction (lon/lat),Detection,Earth Impact,Arrival Time,Uncertainty,Confidence,Spacecraft,Associated Flare,Multi-CME
2,https://kauai.ccmc.gsfc.nasa.gov/DONKI/view/Alert/42314/1,2025-11-02T12:23:00-CME-001,2025-11-02T12:23:00Z,C-type,757,38,-73/22,STEREO A/GOES/SOHO,Yes,,,,"BepiColombo, Parker Solar Probe","C8.2 from unnumbered region, peaked 2025-11-02T12:46Z",
```

### Markdown Format

```markdown
| 2 | 2025-11-02T12:23:00Z | C-type | 757 km/s | 38° | -73/22 | STEREO A/GOES/SOHO | ✓ | TBD |  | BepiColombo, Parker Solar Probe | C8.2 from unnumbered region, peaked 2025-11-02T12:46Z |  | [Link](...) |
```

### Database Query Result

```
CME #2 (Message ID: 20251102-AL-003)
├─ Start: 2025-11-02T12:23:00Z
├─ Type: C-type, Speed: 757 km/s
├─ Earth Impact: Yes
├─ Spacecraft: BepiColombo, Parker Solar Probe
├─ Associated Flare: C8.2 from unnumbered region, peaked 2025-11-02T12:46Z
├─ Multi-CME: No
└─ Model Links: 5 visualization(s)
```

---

## Key Findings from Data Analysis

### 1. Multi-CME Notifications are Common

The Nov 2 data shows that NASA often groups related CMEs in a single notification:
- Notification 20251102-AL-004 contained **2 separate CME events**
- Events occurred 1 hour apart (15:36Z and 16:36Z)
- Both tracked to BepiColombo

**Implication:** Future versions could parse and store each CME separately

### 2. Spacecraft Impact Predictions Beyond Earth

Not all CMEs are Earth-directed:
- **BepiColombo** (Mercury orbiter): 3 impacts predicted
- **Parker Solar Probe**: 1 impact predicted
- Arrival times provided with ±7 hour uncertainty

**Implication:** System now captures non-Earth space weather impacts

### 3. Flare-CME Associations

CMEs are often linked to source flares:
- 1 out of 3 notifications included flare information
- Flare: C8.2 class from unnumbered region
- Peak time: 13 minutes after CME start (12:46Z vs 12:23Z)

**Implication:** Can track flare-CME relationship for research

### 4. ENLIL Model Visualizations

Each notification includes 4-5 model products:
- Density animations (time-density)
- Velocity animations (time-velocity)
- Timeline visualizations
- Spacecraft-specific timelines

**Implication:** Links available for visualization in reports

---

## Code Changes Summary

### Files Modified

1. **[cme_tracker.py](../cme_tracker.py)** - Core tracking module
   - Database schema: +4 fields (lines 83-88, 95)
   - Parsing logic: +60 lines (lines 270-341)
   - Storage: Updated INSERT statement (lines 412-457)
   - CSV export: +3 columns (lines 672-723)
   - Markdown export: +4 columns (lines 796-849)

### Files Created

2. **[test_nov2_cme_parsing.py](../test_nov2_cme_parsing.py)** - Enhanced parsing test
   - Fetches Nov 2, 2025 data specifically
   - Verifies all new fields
   - Shows sample output
   - ~100 lines

3. **[docs/CME_ENHANCED_PARSING_COMPLETE.md](CME_ENHANCED_PARSING_COMPLETE.md)** - This document
   - Complete feature documentation
   - Test results
   - Examples

### Lines of Code Added

- Database schema: ~10 lines
- Parsing enhancements: ~60 lines
- Storage updates: ~8 lines
- Export updates: ~30 lines
- Test script: ~100 lines

**Total:** ~210 lines added/modified

---

## Comparison: Before vs After

### Before Enhancement

**CSV Columns (13):**
```csv
#,NASA Alert,Activity ID,Start Time,Type,Speed (km/s),Half-Angle (deg),Direction (lon/lat),Detection,Earth Impact,Arrival Time,Uncertainty,Confidence
```

**Markdown Columns (11):**
```markdown
| # | Start Time | Type | Speed | Half-Angle | Direction | Detection | Earth Impact | Arrival | Confidence | NASA Alert |
```

**Database Fields:** 24 fields

### After Enhancement

**CSV Columns (16):**
```csv
#,NASA Alert,Activity ID,Start Time,Type,Speed (km/s),Half-Angle (deg),Direction (lon/lat),Detection,Earth Impact,Arrival Time,Uncertainty,Confidence,Spacecraft,Associated Flare,Multi-CME
```

**Markdown Columns (14):**
```markdown
| # | Start Time | Type | Speed | Half-Angle | Direction | Detection | Earth Impact | Arrival | Confidence | Spacecraft | Flare | Multi | Alert |
```

**Database Fields:** 28 fields

**New Data Captured:**
- ✅ Non-Earth spacecraft targets
- ✅ Associated flare information
- ✅ Multi-CME flag
- ✅ Improved model visualization links

---

## Future Enhancements (Not Implemented)

### 1. Parse Individual CMEs from Multi-CME Notifications

**Current:** Multi-CME notifications stored as single record
**Proposed:** Parse numbered list and create separate records for each CME

**Example:**
```
Notification: 20251102-AL-004 (Multi-CME)
  ├─ CME 1: 2025-11-02T15:36:00Z, 536 km/s
  └─ CME 2: 2025-11-02T16:36:00Z, 500 km/s
```

**Benefit:** More granular tracking, better statistics

### 2. Fetch Analyst Name from Web Page

**Current:** `submitted_by` field is NULL
**Proposed:** Optional HTTP request to messageURL to extract analyst name

**Example:** Anna Chulaki submitted notification 20251102-AL-004

**Benefit:** Attribution for data quality tracking

### 3. Track CME-Flare Relationships

**Proposed:** Create link table between flares and CMEs
- Extract flare ID from notification
- Link to flare database (if integrated)
- Track timing relationship (CME delay after flare peak)

**Benefit:** Research analysis of flare-CME associations

### 4. Visualization Link Management

**Proposed:** Store each visualization link separately with type classification
- Density animation
- Velocity animation
- General timeline
- Spacecraft-specific timeline

**Benefit:** Direct access to specific visualization types in reports

---

## Known Limitations

### 1. Multi-CME Parsing

The system detects multi-CME notifications but stores them as a single record. The first CME's parameters are captured, but subsequent CMEs in the same notification are not individually tracked.

**Workaround:** Check `is_multi_cme` flag and manually review notification

### 2. Complex Region Descriptions

Flare region extraction may capture verbose descriptions for unnumbered regions:
- Good: "AR4274"
- Good: "unnumbered region"
- Verbose: "an unnumbered region rotating onto the Earth-facing disk"

**Mitigation:** Regex now simplifies to "unnumbered region"

### 3. Arrival Time Data

Many CMEs show "TBD" for arrival time even when marked as Earth-directed. This is expected when:
- NASA hasn't completed modeling
- CME is glancing blow (spacecraft only)
- Prediction confidence is too low

---

## Usage Examples

### Query CMEs with Spacecraft Impacts

```python
from cme_tracker import CMETracker

tracker = CMETracker()

conn = sqlite3.connect('space_weather.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT message_id, start_time, cme_type, speed,
           affected_spacecraft, arrival_time
    FROM cmes
    WHERE affected_spacecraft IS NOT NULL
    ORDER BY start_timestamp DESC
''')

for row in cursor.fetchall():
    print(f"{row[1]}: {row[2]}-type at {row[3]} km/s → {row[4]}")
```

### Find CMEs with Associated Flares

```python
cursor.execute('''
    SELECT message_id, start_time, cme_type, associated_flare
    FROM cmes
    WHERE associated_flare IS NOT NULL
    ORDER BY start_timestamp DESC
''')
```

### Identify Multi-CME Notifications

```python
cursor.execute('''
    SELECT message_id, start_time, message_url
    FROM cmes
    WHERE is_multi_cme = 1
''')
```

---

## Testing

### Test Script

**File:** [test_nov2_cme_parsing.py](../test_nov2_cme_parsing.py)

**Run:**
```bash
python3 test_nov2_cme_parsing.py
```

**Tests:**
1. Database schema with new fields
2. Spacecraft target extraction
3. Associated flare parsing
4. Multi-CME detection
5. Model visualization link extraction
6. CSV export with new columns
7. Markdown export with new fields

**Expected Output:**
```
✓ ENHANCED CME PARSING TEST COMPLETE

Enhanced Features Verified:
  ✓ Spacecraft targets extraction
  ✓ Associated flare information
  ✓ Multi-CME detection
  ✓ Model visualization link extraction
  ✓ CSV export with new columns
  ✓ Markdown export with new fields
```

### Manual Verification

```bash
# Check database schema
sqlite3 space_weather.db ".schema cmes"

# Query new fields
sqlite3 space_weather.db "SELECT message_id, affected_spacecraft, associated_flare, is_multi_cme FROM cmes"

# View CSV output
cat reports/2025-11/cmes-2025-11.csv

# View Markdown
cat reports/2025-11/cmes-2025-11.md
```

---

## Integration Status

### Current Implementation

**Phase 1:** ✅ Core tracking (database, API, parsing, storage, queries)
**Phase 2:** ✅ Export methods (CSV, Markdown)
**Phase 2.5:** ✅ Enhanced parsing (spacecraft, flares, multi-CME)

### Pending Integration

**Phase 3:** Report integration
- Add CME data to space weather reports
- Include new fields in report sections
- Highlight multi-CME notifications
- Show spacecraft impacts
- Display associated flare context

**Phase 4:** Configuration & documentation
- Add CME settings to config.yaml
- Update scheduler integration
- Create user documentation
- Update main README

---

## Summary

**Phase 2.5 Status:** ✅ COMPLETE

**Achievements:**
- ✅ Database schema enhanced with 4 new fields
- ✅ Spacecraft target extraction implemented and tested
- ✅ Associated flare parsing working correctly
- ✅ Multi-CME detection functioning
- ✅ Model visualization links improved
- ✅ CSV export includes 3 new columns
- ✅ Markdown export includes 4 new fields
- ✅ Test script created and passing
- ✅ November 2, 2025 data successfully parsed

**Lines of Code:** +210 lines

**Test Results:** All enhancements verified with real NASA DONKI data

**Ready for:** Phase 3 (Report Integration)

---

**Completion Date:** November 3, 2025
**Status:** ✅ PHASE 2.5 COMPLETE - ENHANCED PARSING OPERATIONAL
**Next Phase:** Report integration with enhanced CME data
