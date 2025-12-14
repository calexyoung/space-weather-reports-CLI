# Enhanced CME Tracking System - Complete Documentation

## Overview

The enhanced CME tracking system fetches complete CME data from NASA's DONKI (Database Of Notifications, Knowledge, Information) API, including multiple analyses per CME (Leading Edge and Shock Front), model run results, Kp estimates, and spacecraft impact predictions.

## Data Source

**NASA DONKI API:** `https://api.nasa.gov/DONKI/CME`
- Complete CME catalog with analysis data
- Multiple model runs per analysis (WSA-ENLIL+Cone)
- Earth and spacecraft arrival predictions
- Kp geomagnetic activity estimates

## Database Schema

### Table: `cmes_enhanced`
Primary CME information:
```sql
- id (PRIMARY KEY)
- activity_id (UNIQUE) - e.g., "2025-11-05T10:53:00-CME-001"
- catalog - Always "M2M_CATALOG"
- start_time - CME start time (UTC)
- start_timestamp - Unix timestamp
- source_location - e.g., "N24E47"
- source_region - Active region number
- associated_flare - Linked flare activity ID
- note - Description from DONKI
- instruments - Detection instruments
- donki_url - Link to DONKI page
- created_at, updated_at - Metadata
```

### Table: `cme_analyses`
CME analysis data (Leading Edge or Shock Front):
```sql
- id (PRIMARY KEY)
- cme_id (FOREIGN KEY to cmes_enhanced)
- activity_id - Parent CME activity ID
- analysis_id - Unique analysis identifier
- analysis_type - 'LE' (Leading Edge) or 'SH' (Shock Front)
- measurement_time - When measurement was made
- measurement_timestamp - Unix timestamp
- technique - e.g., "SWPC_CAT"
- data_level - 0 = real-time, higher = refined
- speed - CME speed in km/s
- type - CME type ('O', 'C', etc.)
- direction_lon, direction_lat - Direction in HEEQ coordinates
- half_angle - Angular width
- time_at_21_5_rs - Time at 21.5 solar radii
- instruments - Detection instruments
- image_type - e.g., "running difference"
- created_at, updated_at - Metadata
```

### Table: `cme_model_runs`
WSA-ENLIL+Cone model results:
```sql
- id (PRIMARY KEY)
- analysis_id (FOREIGN KEY to cme_analyses)
- activity_id - Parent CME activity ID
- run_number - Model run sequence number
- model_completion_time - When model finished
- model_completion_timestamp - Unix timestamp
- earth_arrival_time - Predicted Earth shock arrival
- earth_arrival_timestamp - Unix timestamp
- impact_duration - Hours
- rmin_earth_radii - Minimum magnetopause distance
- kp_90, kp_135, kp_180 - Kp estimates at different angles
- created_at - Metadata
```

### Table: `cme_spacecraft_impacts`
Spacecraft arrival predictions:
```sql
- id (PRIMARY KEY)
- model_run_id (FOREIGN KEY to cme_model_runs)
- analysis_id - Parent analysis ID
- activity_id - Parent CME activity ID
- spacecraft_name - e.g., "Parker Solar Probe"
- arrival_time - Predicted arrival
- arrival_timestamp - Unix timestamp
- created_at - Metadata
```

## CME Analysis Types

### Leading Edge (LE)
- Measures the front edge of the CME material
- Typically slower speeds
- More conservative arrival estimates
- Used for primary arrival time predictions

### Shock Front (SH)
- Measures the shock wave ahead of the CME
- Typically faster speeds
- Earlier arrival times
- Used for initial geomagnetic disturbance timing

## Example: November 5 CME

**CME Activity ID:** `2025-11-05T10:53:00-CME-001`

**Basic Info:**
- Start Time: 2025-11-05 10:53 UTC
- Source: N24E47 (AR 14274)
- Associated Flare: M7.4 (2025-11-05T10:36:00-FLR-001)
- Type: Halo CME

**Leading Edge Analysis:**
- Speed: 1123 km/s
- Direction: LON -37°, LAT 9°
- Half Angle: 39°
- **Earth Arrivals (3 model runs):**
  - Run 1: 2025-11-07 03:18 UTC (Kp 90°=7, 135°=8, 180°=9)
  - Run 2: 2025-11-07 03:22 UTC (Kp 90°=7, 135°=8, 180°=9)
  - Run 3: 2025-11-07 03:17 UTC (Kp 90°=7, 135°=8, 180°=9)

**Shock Front Analysis:**
- Speed: 1529 km/s
- Direction: LON -15°, LAT 4°
- Half Angle: 48°
- **Earth Arrivals (2 model runs):**
  - Run 1: 2025-11-06 17:50 UTC (Rmin 4.3 Re)
  - Run 2: 2025-11-06 17:52 UTC (Rmin 4.3 Re)

## Kp Estimates

Kp index predictions at three angles:
- **90°** - Conditions at ±6 hours from shock arrival
- **135°** - Conditions at peak impact
- **180°** - Maximum potential Kp

**Interpretation:**
- Kp 4-5: Active conditions, minor aurora
- Kp 6-7: Strong activity, G1-G2 storms
- Kp 8-9: Severe activity, G3-G4 storms

## Usage Example

```python
from cme_tracker_enhanced import EnhancedCMETracker
from datetime import datetime, timezone, timedelta

# Initialize tracker
tracker = EnhancedCMETracker()

# Sync CMEs from DONKI API
api_key = 'your-nasa-api-key'
tracker.sync_cmes('2025-11-04', '2025-11-05', api_key)

# Get CMEs that occurred in last 24 hours
now = datetime.now(timezone.utc)
start_time = now - timedelta(hours=24)
recent_cmes = tracker.get_cmes_for_period(start_time, now)

# Get CMEs with arrivals in next 3 days (±7 hour window)
forecast_start = now
forecast_end = now + timedelta(days=3)
arriving_cmes = tracker.get_cmes_with_arrivals_in_window(
    forecast_start, forecast_end, uncertainty_hours=7
)

print(f"Recent CMEs: {len(recent_cmes)}")
print(f"CMEs arriving soon: {len(arriving_cmes)}")

# Access complete data structure
for cme in arriving_cmes:
    print(f"\nCME: {cme['activity_id']}")
    print(f"  Start: {cme['start_time']}")
    print(f"  Source: {cme['source_location']}")

    for analysis in cme['analyses']:
        print(f"\n  Analysis ({analysis['analysis_type']}): {analysis['speed']} km/s")

        for model_run in analysis['model_runs']:
            if model_run['earth_arrival_time']:
                print(f"    Arrival: {model_run['earth_arrival_time']}")
                if model_run['kp_90']:
                    print(f"    Kp: {model_run['kp_90']}-{model_run['kp_180']}")
```

## CME Listing Criteria (Updated)

### For "Recent CME Activity" Section
Include CMEs that:
1. **Occurred in last 24 hours** (start_time within analysis period)
2. Include ALL analyses for each CME (both LE and SH if available)
3. Show all model run results for each analysis

### For "CME Arrival Predictions" Section
Include CMEs that:
1. **Have Earth arrival predictions within forecast window** (typically next 3 days)
2. **Apply ±7 hour uncertainty window** around predicted arrivals
3. Include ONLY CMEs with Earth impact predictions (where `earth_arrival_timestamp` IS NOT NULL)
4. Show all model runs for each analysis type

### Combined View
Some CMEs may appear in both sections:
- In "Recent Activity" if they occurred in last 24 hours
- In "Arrival Predictions" if they're predicted to arrive in forecast period

## Data Completeness

**From November 4-5, 2025 test:**
- 7 CMEs tracked
- 12 analyses total (some CMEs have both LE and SH)
- 9 model runs with Earth arrival predictions
- 3 CMEs with Earth impacts:
  - `2025-11-04T00:24:00-CME-001` (SH: arrives 2025-11-06 10:00)
  - `2025-11-04T17:53:00-CME-001` (SH: arrives 2025-11-06 08:55, Kp 7-9)
  - `2025-11-04T22:53:00-CME-001` (LE: arrives 2025-11-07 03:17/04:00, Kp 5-9)
  - `2025-11-05T10:53:00-CME-001` (LE: arrives 2025-11-07 03:17-03:22, SH: arrives 2025-11-06 17:50-17:52, Kp 7-9)

## API Configuration

**NASA API Key:**
Store in `.env` file:
```
NASA_DONKI_API_KEY=your-api-key-here
```

**Rate Limits:**
- Demo key: 30 requests/hour, 50 requests/day
- Personal key: 1000 requests/hour

**Request Format:**
```
GET https://api.nasa.gov/DONKI/CME?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD&api_key=KEY
```

## Benefits Over Old System

### Old System (`cme_tracker.py`)
- Single table with one analysis per CME
- Only stored one arrival time per CME
- No Kp estimates
- No distinction between LE and SH analyses
- No multiple model run support
- Used notification parsing (incomplete data)

### New System (`cme_tracker_enhanced.py`)
- ✅ Multiple analyses per CME (LE + SH)
- ✅ Multiple model runs per analysis
- ✅ Complete Kp estimates (90°, 135°, 180°)
- ✅ Spacecraft impact predictions
- ✅ Magnetopause distance (Rmin) data
- ✅ Impact duration estimates
- ✅ Direct DONKI API integration
- ✅ Complete flare association tracking

## Next Steps

1. **Integrate with report generator**
   - Update `space_weather_automation.py` to use enhanced tracker
   - Create methods to fetch CME data for report periods

2. **Update Claude prompt**
   - Add CME table formatting with LE/SH columns
   - Include Kp estimates in arrival predictions
   - Show multiple model runs for each CME

3. **Add to automated collection**
   - Schedule regular CME syncs (every 4-6 hours)
   - Maintain rolling 7-day window of CME data

4. **Export functionality**
   - CSV export with complete analysis data
   - Markdown table generation for reports
   - JSON export for API consumers

## Files

- **cme_tracker_enhanced.py** - Enhanced CME tracker implementation
- **space_weather.db** - SQLite database with enhanced schema
- **CME_TRACKING_ENHANCED_SUMMARY.md** - This documentation

## Credits

- Data source: NASA DONKI (https://kauai.ccmc.gsfc.nasa.gov/DONKI/)
- Model: WSA-ENLIL+Cone (Space Weather Prediction Center)
- API: NASA Open APIs (https://api.nasa.gov/)
