# CME Integration Status - Current Progress

## Completed Tasks ✅

### 1. Enhanced Database Schema
Created complete database schema with 4 tables:
- **cmes_enhanced** - Main CME data (activity ID, source, flare association)
- **cme_analyses** - LE and SH analyses for each CME (speed, direction, instruments)
- **cme_model_runs** - WSA-ENLIL+Cone results (Earth arrivals, Kp estimates, Rmin)
- **cme_spacecraft_impacts** - Arrival predictions for other spacecraft

### 2. DONKI API Integration
Successfully integrated NASA DONKI API (CCMC direct endpoint):
- Uses `https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/CME` (no API key required)
- Fetches complete CME data in JSON format (9 CMEs vs 7 from api.nasa.gov)
- Parses multiple analyses per CME (Leading Edge + Shock Front)
- Stores all model run results with Kp estimates
- Handles spacecraft impact predictions

### 3. Data Storage Implementation
Complete storage pipeline:
- `fetch_cmes_from_api()` - Retrieves CMEs from DONKI
- `store_cme()` - Stores main CME data
- `_store_analysis()` - Stores LE/SH analyses
- `_store_model_run()` - Stores ENLIL model results with Kp
- `_store_spacecraft_impact()` - Stores spacecraft predictions

### 4. Query Methods
Two key query methods implemented:
- `get_cmes_for_period()` - CMEs that occurred in time period (for "Recent Activity")
- `get_cmes_with_arrivals_in_window()` - CMEs arriving in forecast window with ±7h uncertainty

### 5. Testing
Tested with real data (November 4-5, 2025):
- Successfully stored 7 CMEs
- 12 analyses (mix of LE and SH)
- 9 model runs with Earth impacts
- Complete Kp estimates (90°, 135°, 180°)

### 6. Main Script Integration
Updated [space_weather_automation.py](space_weather_automation.py):
- `get_cmes_for_report_period()` now uses EnhancedCMETracker
- `get_predicted_cme_arrivals()` now uses EnhancedCMETracker with ±7h window
- Both methods return complete data structure with analyses and model runs

### 7. Documentation
Created comprehensive documentation:
- **CME_TRACKING_ENHANCED_SUMMARY.md** - Complete technical documentation
- **CME_INTEGRATION_STATUS.md** - This status document

## Remaining Tasks 🔧

### 1. Update Claude Report Generation Prompt
**File to modify:** [claude_integration_enhanced.py](claude_integration_enhanced.py)

**What needs to be added:**

#### A. CME Data Structure Documentation
Add section explaining the enhanced CME data structure that Claude will receive:

```
# CME DATA STRUCTURE

Each CME in the `cmes` list has this structure:

{
  'activity_id': '2025-11-05T10:53:00-CME-001',
  'start_time': '2025-11-05T10:53Z',
  'source_location': 'N24E47',
  'source_region': '14274',
  'associated_flare': '2025-11-05T10:36:00-FLR-001',
  'note': 'Halo CME description...',
  'analyses': [
    {
      'analysis_type': 'LE',  # Leading Edge
      'speed': 1123.0,
      'direction_lon': -37.0,
      'direction_lat': 9.0,
      'half_angle': 39.0,
      'model_runs': [
        {
          'run_number': 1,
          'earth_arrival_time': '2025-11-07T03:18Z',
          'kp_90': 7,
          'kp_135': 8,
          'kp_180': 9,
          'rmin_earth_radii': 5.8,
          'impact_duration': 24.3
        },
        # ... more model runs
      ]
    },
    {
      'analysis_type': 'SH',  # Shock Front
      'speed': 1529.0,
      # ... similar structure
    }
  ]
}
```

#### B. CME Reporting Instructions

**For "Recent CME Activity" Section:**
```
## CME Reporting Guidelines

### Recent CME Activity (Last 24 Hours)
List ALL CMEs that occurred during the analysis period (11:00 UTC previous day to 11:00 UTC current day).

For each CME:
1. **Start time and date** in UTC with hyperlink
2. **Source location** (e.g., N24E47) with coordinate link
3. **Source region** if available (e.g., AR 14274)
4. **Associated flare** if present (e.g., "associated with M7.4 flare")
5. **CME characteristics:**
   - Type (Halo, Partial Halo, or directional)
   - Speed from most accurate analysis
   - Half-angle width

**Format Example:**
<li>A <a href="link">halo CME</a> erupted at <a href="time-link">10:53 UTC</a> on November 05 from <a href="coord-link">N24E47</a> (<strong>AR 14274</strong>), associated with the M7.4 flare. Analysis shows speeds of 1123 km/s (leading edge) and 1529 km/s (shock front), with Earth-directed components.</li>

### CME Arrival Predictions
List CMEs with predicted Earth arrivals within the forecast period (±7 hour uncertainty window).

For each predicted arrival:
1. **CME identification** (date/time of eruption)
2. **Analysis type** (Leading Edge or Shock Front)
3. **Speed** of the analysis
4. **ALL model run results** for that analysis
5. **Kp estimates** if available (show range: Kp 7-9)
6. **Timing precision:**
   - Show arrival date and approximate time window
   - If multiple runs, show range (e.g., "03:17-03:22 UTC")

**Format Example:**
<li>The November 05 halo CME from <strong>AR 14274</strong>:
  <ul>
    <li><strong>Leading Edge analysis (1123 km/s):</strong> Three model runs predict Earth arrival on November 07 between 03:17 and 03:22 UTC, with Kp indices forecast to reach 7-9, indicating <a href="link">G3 (Strong)</a> geomagnetic storm potential.</li>
    <li><strong>Shock Front analysis (1529 km/s):</strong> Two model runs predict an earlier shock arrival on November 06 at approximately 17:50 UTC, potentially producing initial disturbances with less intense geomagnetic effects.</li>
  </ul>
</li>

### Key Points:
- **Always show BOTH LE and SH analyses** when both are available
- **Show ALL model run results**, not just one
- **Kp ranges** help readers understand storm severity (Kp 7-9 = G3 potential)
- **Explain the difference** between shock front (earlier, faster) and leading edge (main CME material)
- **Link appropriately:** CMEs, coordinates, times, G-scale storms
```

#### C. CME Table Format
Add HTML table structure for CMEs:

```html
<h3>Coronal Mass Ejections (Last 24 Hours)</h3>
<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <thead>
    <tr style="background-color: #f0f0f0;">
      <th style="padding: 8px; border: 1px solid #ddd;">Start Time (UTC)</th>
      <th style="padding: 8px; border: 1px solid #ddd;">Source</th>
      <th style="padding: 8px; border: 1px solid #ddd;">Type</th>
      <th style="padding: 8px; border: 1px solid #ddd;">LE Speed (km/s)</th>
      <th style="padding: 8px; border: 1px solid #ddd;">SH Speed (km/s)</th>
      <th style="padding: 8px; border: 1px solid #ddd;">Earth Impact?</th>
    </tr>
  </thead>
  <tbody>
    <!-- For each CME -->
    <tr>
      <td>Nov 05, 10:53</td>
      <td>N24E47 (AR 14274)</td>
      <td>Halo</td>
      <td>1123</td>
      <td>1529</td>
      <td>Yes - Nov 06-07</td>
    </tr>
  </tbody>
</table>
```

### 2. Add CME Sync to Automated Collection
**File to modify:** [flare_tracker_simple.py](flare_tracker_simple.py) or create new scheduled task

Add CME collection to run periodically (every 4-6 hours):

```python
from cme_tracker_enhanced import EnhancedCMETracker
from datetime import datetime, timedelta

def sync_cmes_for_reports():
    """Sync CMEs for the last 7 days"""
    tracker = EnhancedCMETracker()

    # Fetch last 7 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # Use NASA API key from environment
    api_key = os.getenv('NASA_DONKI_API_KEY', 'DEMO_KEY')

    count = tracker.sync_cmes(start_date, end_date, api_key)
    logger.info(f"Synced {count} CMEs")

    return count
```

### 3. Environment Configuration
**No longer needed!** The CCMC endpoint doesn't require an API key.

~~Add NASA API key:~~
```
# NASA_DONKI_API_KEY=XTkp5hbrVeI3Y7mrflulsba12DyNlSqhxyhmtMgG  # Not needed
```

### 4. Test Complete Integration
After Claude prompt update, test with:
```bash
python3 space_weather_automation.py
```

Should produce report with:
- CME table showing all CMEs from last 24h
- Both LE and SH speeds for each CME
- Detailed arrival predictions with multiple model runs
- Kp estimates for geomagnetic forecasting

## Benefits of New System

### For Reports
✅ **Complete CME information** - Both LE and SH analyses shown
✅ **Multiple model runs** - Show range of predictions, not just one
✅ **Kp estimates** - Readers see expected geomagnetic activity level
✅ **Better forecasting** - ±7h uncertainty window captures more arrivals

### For Users
✅ **Transparency** - See all model predictions, not cherry-picked
✅ **Better understanding** - Explain LE vs SH, show speed differences
✅ **Storm preparation** - Kp 7-9 clearly indicates G3 storm potential

### For Accuracy
✅ **No missed CMEs** - Comprehensive DONKI API coverage
✅ **Complete data** - All analyses and model runs stored
✅ **Proper uncertainty** - ±7h window reflects forecast reality

## Example Output (What Reports Should Show)

### Recent CME Activity Section:
```
**Coronal Mass Ejections:**
- A halo CME erupted at 10:53 UTC on November 05 from N24E47 (AR 14274),
  associated with the M7.4 flare. Leading edge analysis shows 1123 km/s,
  while shock front analysis indicates 1529 km/s. Both analyses predict
  Earth impacts.

- A partial halo CME launched at 17:53 UTC on November 04 from N24E63
  (AR 14274), linked to the X1.8 flare. Shock front speed of 1224 km/s
  with predicted Earth arrival.
```

### CME Arrival Forecast Section:
```
**CME Arrival Predictions:**

*November 06 Arrivals:*
- November 04 X1.8 CME (shock front, 1224 km/s): Arrival predicted at
  approximately 08:55 UTC. Model forecasts Kp 7-9, indicating strong
  geomagnetic storm conditions (G3 potential).

- November 05 M7.4 CME (shock front, 1529 km/s): Earlier shock arrival
  at 17:50 UTC, ahead of main CME material.

*November 07 Arrivals:*
- November 05 M7.4 CME (leading edge, 1123 km/s): Three model runs
  converge on 03:17-03:22 UTC arrival window. Strong storm potential
  with Kp 7-9 forecast.

- November 04 CME (leading edge, 639 km/s): Later arrival around
  03:17-04:00 UTC. Moderate storm activity expected (Kp 5-7).
```

## Next Steps

1. **Update Claude prompt** in claude_integration_enhanced.py
2. **Add CME sync** to automated collection
3. **Test complete workflow** with November 4-5 data
4. **Generate sample report** to verify formatting
5. **Document for user** in main README

## Questions for User

1. Should CME table be included in every report, or only when CMEs occurred?
2. Should we always show both LE and SH, or only when both have Earth impacts?
3. Preferred format for multiple model runs - show all individually or as range?
4. Should spacecraft impacts (other than Earth) be mentioned in reports?

## Files Modified

✅ cme_tracker_enhanced.py - Complete enhanced tracker
✅ space_weather_automation.py - Integration with main script
✅ CME_TRACKING_ENHANCED_SUMMARY.md - Technical documentation
✅ CME_INTEGRATION_STATUS.md - This status document

🔧 claude_integration_enhanced.py - PENDING (Claude prompt update)
🔧 .env - PENDING (Add NASA API key)
🔧 Scheduled task - PENDING (Automated CME sync)
