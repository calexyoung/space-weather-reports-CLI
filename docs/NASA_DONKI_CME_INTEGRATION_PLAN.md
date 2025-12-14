# NASA DONKI CME Integration Plan

## Overview

This document outlines the plan for integrating Coronal Mass Ejection (CME) data from NASA's DONKI (Database Of Notifications, Knowledge, Information) API into the space weather reporting system.

**Implementation Date:** November 3, 2025
**Status:** PLANNING PHASE

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Data Structure Analysis](#data-structure-analysis)
3. [Fields to Capture](#fields-to-capture)
4. [Database Schema Design](#database-schema-design)
5. [Implementation Strategy](#implementation-strategy)
6. [Integration Points](#integration-points)
7. [Usage Examples](#usage-examples)
8. [Code Implementation Plan](#code-implementation-plan)

---

## API Overview

### Endpoint

```
https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/notifications
```

### Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `startDate` | string | Start date (YYYY-MM-DD) | `2025-10-27` |
| `endDate` | string | End date (YYYY-MM-DD) | `2025-11-03` |
| `type` | string | Notification type | `CME` |

### Example Request

```
https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/notifications?startDate=2025-10-27&endDate=2025-11-03&type=CME
```

### Response Format

JSON array of CME notification objects.

---

## Data Structure Analysis

### JSON Schema

```json
[
  {
    "messageType": "CME",
    "messageID": "20251103-AL-003",
    "messageURL": "https://kauai.ccmc.gsfc.nasa.gov/DONKI/view/Alert/42338/1",
    "messageIssueTime": "2025-11-03T14:39Z",
    "messageBody": "## Community Coordinated Modeling Center...\n\n## Summary:\n\n..."
  }
]
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `messageType` | string | Always "CME" for CME notifications | `"CME"` |
| `messageID` | string | Unique alert identifier | `"20251103-AL-003"` |
| `messageURL` | string | Link to full alert details | `https://...` |
| `messageIssueTime` | string | ISO 8601 timestamp when alert was issued | `"2025-11-03T14:39Z"` |
| `messageBody` | string | Markdown-formatted detailed report | See below |

### messageBody Content Structure

The `messageBody` field contains all CME details in markdown format:

#### Header
```
## Community Coordinated Modeling Center
## Database Of Notifications, Knowledge, Information
```

#### Summary Section
```
## Summary:

O-type CME detected by STEREO A / GOES / SOHO.

Start time of the event: 2025-11-03T09:36Z.

Estimated speed: ~1034 km/s.

Estimated opening half-angle: 45 deg.

Direction (lon./lat.): -56/24 in Heliocentric Earth Equatorial coordinates.

Activity ID: 2025-11-03T09:36:00-CME-001
```

#### CME Speed Classification
- **S-type:** < 500 km/s (Slow)
- **C-type:** 500-999 km/s (Common)
- **O-type:** 1000-1999 km/s (Occasional)
- **R-type:** 2000-2999 km/s (Rare)
- **ER-type:** > 3000 km/s (Extremely Rare)

#### Impact Predictions (Optional)
```
## Predicted Impacts:

Model: WSA-ENLIL + Cone
Estimated Arrival Time: 2025-11-03T22:21Z ± 7 hr
Estimated Duration: 19 hr
Confidence: Medium
```

#### Notes Section
```
## Notes:

SOHO LASCO imagery: https://...
WSA-ENLIL visualization: https://...
```

---

## Fields to Capture

### Primary Fields (Direct from JSON)

1. **message_id** - Unique identifier (`messageID`)
2. **message_url** - Link to full alert (`messageURL`)
3. **issue_time** - When alert was issued (`messageIssueTime`)
4. **message_body** - Full text for reference (`messageBody`)

### Parsed Fields (Extracted from messageBody)

#### Essential CME Parameters

5. **cme_type** - Speed classification (S/C/O/R/ER-type)
6. **start_time** - When CME occurred (ISO 8601)
7. **speed** - Velocity in km/s (integer)
8. **half_angle** - Opening half-angle in degrees (integer)
9. **direction_lon** - Longitude coordinate (integer)
10. **direction_lat** - Latitude coordinate (integer)
11. **activity_id** - Unique event identifier
12. **detection_instruments** - Comma-separated list (e.g., "STEREO A, GOES, SOHO")

#### Impact Prediction Fields (if available)

13. **has_earth_impact** - Boolean (true if Earth prediction exists)
14. **arrival_time** - Predicted Earth arrival (ISO 8601)
15. **arrival_uncertainty** - Uncertainty window in hours (±7)
16. **impact_duration** - Duration in hours
17. **confidence_level** - Low/Medium/High
18. **affected_missions** - List of spacecraft in path

#### Metadata

19. **analysis_office** - Source (e.g., "Moon to Mars Space Weather Analysis Office")
20. **imagery_links** - JSON array of visualization URLs
21. **created_at** - When record was added to our database
22. **updated_at** - When record was last updated

---

## Database Schema Design

### Table: `cmes`

```sql
CREATE TABLE IF NOT EXISTS cmes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Primary identifiers
    message_id TEXT UNIQUE NOT NULL,
    activity_id TEXT,

    -- Timing
    start_time TEXT NOT NULL,              -- ISO 8601: 2025-11-03T09:36:00Z
    start_timestamp INTEGER,                -- Unix timestamp for queries
    issue_time TEXT NOT NULL,              -- When NASA issued alert
    issue_timestamp INTEGER,

    -- CME characteristics
    cme_type TEXT,                         -- S/C/O/R/ER-type
    speed INTEGER,                         -- km/s
    half_angle INTEGER,                    -- degrees
    direction_lon INTEGER,                 -- longitude
    direction_lat INTEGER,                 -- latitude
    detection_instruments TEXT,            -- comma-separated

    -- Earth impact prediction
    has_earth_impact INTEGER DEFAULT 0,    -- boolean
    arrival_time TEXT,                     -- ISO 8601
    arrival_timestamp INTEGER,
    arrival_uncertainty INTEGER,           -- hours (±)
    impact_duration INTEGER,               -- hours
    confidence_level TEXT,                 -- Low/Medium/High

    -- Reference data
    message_url TEXT,
    message_body TEXT,                     -- full markdown text
    imagery_links TEXT,                    -- JSON array
    analysis_office TEXT,

    -- Metadata
    created_at INTEGER NOT NULL,
    updated_at INTEGER,

    -- Indexes for common queries
    UNIQUE(message_id)
);

CREATE INDEX IF NOT EXISTS idx_cme_start_timestamp
    ON cmes(start_timestamp);

CREATE INDEX IF NOT EXISTS idx_cme_arrival_timestamp
    ON cmes(arrival_timestamp);

CREATE INDEX IF NOT EXISTS idx_cme_type
    ON cmes(cme_type);

CREATE INDEX IF NOT EXISTS idx_cme_earth_impact
    ON cmes(has_earth_impact);
```

### Rolling Window Strategy

Similar to flares, maintain CMEs within a configurable time window (e.g., 7-30 days):

```python
def cleanup_old_cmes(self, days: int = 30) -> int:
    """Remove CMEs older than specified days"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_timestamp = int(cutoff.timestamp())

    cursor.execute('''
        DELETE FROM cmes
        WHERE start_timestamp < ?
    ''', (cutoff_timestamp,))
```

---

## Implementation Strategy

### Phase 1: Core CME Tracking Module

**File:** `cme_tracker.py`

Create a new module similar to `flare_tracker_simple.py`:

```python
class CMETracker:
    def __init__(self, db_path='space_weather.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()

    def _init_database(self):
        """Initialize CME database table"""
        # Create table with schema above

    def fetch_cme_notifications(self, start_date, end_date):
        """Fetch CME data from NASA DONKI API"""
        # HTTP request to API

    def parse_cme_body(self, message_body):
        """Extract CME parameters from messageBody text"""
        # Regex parsing of markdown content

    def store_cmes(self, cme_list):
        """Store CMEs in database"""
        # INSERT OR REPLACE logic

    def get_recent_cmes(self, hours=168):
        """Get CMEs from last N hours"""
        # Query database

    def get_earth_directed_cmes(self, hours=168):
        """Get CMEs with Earth impact predictions"""
        # Query with has_earth_impact=1

    def export_monthly_cmes_csv(self, year_month):
        """Export CMEs to CSV file"""
        # Similar to flare export

    def export_monthly_cmes_markdown(self, year_month):
        """Export CMEs to Markdown table"""
        # Similar to flare export
```

### Phase 2: Parsing Logic

**Key Regex Patterns:**

```python
import re

def parse_cme_body(self, message_body: str) -> dict:
    """Extract structured data from CME messageBody"""
    parsed = {}

    # CME Type (S/C/O/R/ER-type)
    type_match = re.search(r'(S|C|O|R|ER)-type CME', message_body)
    if type_match:
        parsed['cme_type'] = type_match.group(1)

    # Start time
    start_match = re.search(r'Start time.*?:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', message_body)
    if start_match:
        parsed['start_time'] = start_match.group(1)

    # Speed
    speed_match = re.search(r'speed:\s*~?(\d+)\s*km/s', message_body)
    if speed_match:
        parsed['speed'] = int(speed_match.group(1))

    # Half-angle
    angle_match = re.search(r'half-angle:\s*(\d+)\s*deg', message_body)
    if angle_match:
        parsed['half_angle'] = int(angle_match.group(1))

    # Direction (lon/lat)
    dir_match = re.search(r'Direction.*?:\s*(-?\d+)/(-?\d+)', message_body)
    if dir_match:
        parsed['direction_lon'] = int(dir_match.group(1))
        parsed['direction_lat'] = int(dir_match.group(2))

    # Activity ID
    activity_match = re.search(r'Activity ID:\s*([\w\-:]+)', message_body)
    if activity_match:
        parsed['activity_id'] = activity_match.group(1)

    # Detection instruments
    inst_match = re.search(r'detected by\s*([\w\s/]+?)\.', message_body)
    if inst_match:
        parsed['detection_instruments'] = inst_match.group(1).strip()

    # Earth impact prediction
    if 'Predicted Impacts' in message_body or 'Earth' in message_body:
        parsed['has_earth_impact'] = True

        # Arrival time
        arrival_match = re.search(r'Arrival Time:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)', message_body)
        if arrival_match:
            parsed['arrival_time'] = arrival_match.group(1)

        # Uncertainty
        unc_match = re.search(r'±\s*(\d+)\s*hr', message_body)
        if unc_match:
            parsed['arrival_uncertainty'] = int(unc_match.group(1))

        # Duration
        dur_match = re.search(r'Duration:\s*(\d+)\s*hr', message_body)
        if dur_match:
            parsed['impact_duration'] = int(dur_match.group(1))

        # Confidence
        conf_match = re.search(r'Confidence:\s*(Low|Medium|High)', message_body)
        if conf_match:
            parsed['confidence_level'] = conf_match.group(1)
    else:
        parsed['has_earth_impact'] = False

    return parsed
```

### Phase 3: Integration with Report Generation

**File:** `space_weather_automation.py`

Add CME data collection to the report workflow:

```python
def collect_cme_data(self):
    """Collect recent CME data from NASA DONKI"""
    try:
        from cme_tracker import CMETracker

        tracker = CMETracker()

        # Fetch last 7 days of CMEs
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        # Fetch from API
        notifications = tracker.fetch_cme_notifications(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        # Parse and store
        cme_count = tracker.store_cmes(notifications)
        self.logger.info(f"Stored {cme_count} CME notifications")

        # Get recent CMEs for report
        recent_cmes = tracker.get_recent_cmes(hours=168)  # 7 days
        earth_cmes = tracker.get_earth_directed_cmes(hours=168)

        return {
            'all_cmes': recent_cmes,
            'earth_directed': earth_cmes,
            'count': len(recent_cmes),
            'earth_count': len(earth_cmes)
        }

    except Exception as e:
        self.logger.error(f"Failed to collect CME data: {e}", exc_info=True)
        return None
```

### Phase 4: Report Template Updates

Update report templates to include CME section:

#### HTML Template Addition

```html
<section id="cmes">
    <h2>Coronal Mass Ejections (CMEs)</h2>

    {% if cme_data and cme_data.count > 0 %}
        <p>
            <strong>Last 7 days:</strong> {{ cme_data.count }} CMEs detected<br>
            <strong>Earth-directed:</strong> {{ cme_data.earth_count }} CMEs
        </p>

        {% if cme_data.earth_count > 0 %}
        <div class="alert alert-warning">
            <h3>⚠️ Earth-Directed CMEs</h3>
            <table>
                <thead>
                    <tr>
                        <th>Start Time</th>
                        <th>Type</th>
                        <th>Speed</th>
                        <th>Arrival Time</th>
                        <th>Confidence</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {% for cme in cme_data.earth_directed %}
                    <tr>
                        <td>{{ cme.start_time }}</td>
                        <td>{{ cme.cme_type }}-type</td>
                        <td>{{ cme.speed }} km/s</td>
                        <td>{{ cme.arrival_time }} ± {{ cme.arrival_uncertainty }}h</td>
                        <td>{{ cme.confidence_level }}</td>
                        <td><a href="{{ cme.message_url }}">NASA Alert</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        <h3>All Recent CMEs</h3>
        <table>
            <thead>
                <tr>
                    <th>Start Time</th>
                    <th>Type</th>
                    <th>Speed</th>
                    <th>Half-Angle</th>
                    <th>Direction</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                {% for cme in cme_data.all_cmes %}
                <tr>
                    <td>{{ cme.start_time }}</td>
                    <td>{{ cme.cme_type }}-type</td>
                    <td>{{ cme.speed }} km/s</td>
                    <td>{{ cme.half_angle }}°</td>
                    <td>{{ cme.direction_lon }}/{{ cme.direction_lat }}</td>
                    <td><a href="{{ cme.message_url }}">NASA Alert</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <p>No CME data available.</p>
    {% endif %}
</section>
```

#### Markdown Template Addition

```markdown
## Coronal Mass Ejections (CMEs)

**Last 7 days:** {{ cme_data.count }} CMEs detected
**Earth-directed:** {{ cme_data.earth_count }} CMEs

{% if cme_data.earth_count > 0 %}
### ⚠️ Earth-Directed CMEs

| Start Time | Type | Speed | Arrival Time | Confidence | Details |
|------------|------|-------|--------------|------------|---------|
{% for cme in cme_data.earth_directed %}
| {{ cme.start_time }} | {{ cme.cme_type }}-type | {{ cme.speed }} km/s | {{ cme.arrival_time }} ± {{ cme.arrival_uncertainty }}h | {{ cme.confidence_level }} | [NASA Alert]({{ cme.message_url }}) |
{% endfor %}
{% endif %}

### All Recent CMEs

| Start Time | Type | Speed | Half-Angle | Direction | Details |
|------------|------|-------|------------|-----------|---------|
{% for cme in cme_data.all_cmes %}
| {{ cme.start_time }} | {{ cme.cme_type }}-type | {{ cme.speed }} km/s | {{ cme.half_angle }}° | {{ cme.direction_lon }}/{{ cme.direction_lat }} | [NASA Alert]({{ cme.message_url }}) |
{% endfor %}
```

---

## Integration Points

### 1. Configuration (config.yaml)

Add CME settings:

```yaml
cme:
  enabled: true
  api_base_url: "https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/notifications"
  fetch_days: 7              # How many days to fetch
  retention_days: 30         # How long to keep in database
  timeout: 30                # Request timeout in seconds

  # Report filtering
  show_earth_directed_only: false
  min_speed: 0               # Minimum speed to include (km/s)

  # Monthly export
  export_csv: true
  export_markdown: true
```

### 2. Database Integration

**Option A:** Separate `cme_database.db` file
- Pros: Keeps CME data isolated
- Cons: Multiple database connections

**Option B:** Add to existing `flare_database.db` (rename to `space_weather.db`)
- Pros: Single database, easier queries
- Cons: Mixing different data types

**Recommendation:** Option B - Rename to `space_weather.db` and include both flares and CMEs.

### 3. Scheduler Integration

Update `scheduler.py` to include CME collection:

```python
def run_full_collection():
    """Run both flare and CME collection"""
    # Collect flare data
    flare_tracker = SimpleFlareTracker()
    flare_tracker.scrape_and_update()

    # Collect CME data
    cme_tracker = CMETracker()
    cme_tracker.fetch_and_store_recent()

    # Generate report
    generator = SpaceWeatherReportGenerator()
    generator.generate_and_save()
```

---

## Usage Examples

### Manual CME Collection

```bash
# Fetch CMEs for date range
python3 -c "
from cme_tracker import CMETracker

tracker = CMETracker()
notifications = tracker.fetch_cme_notifications('2025-10-27', '2025-11-03')
count = tracker.store_cmes(notifications)
print(f'Stored {count} CMEs')
"
```

### Query Recent CMEs

```python
from cme_tracker import CMETracker

tracker = CMETracker()

# Get all CMEs from last 7 days
recent = tracker.get_recent_cmes(hours=168)
print(f"Total CMEs: {len(recent)}")

# Get only Earth-directed CMEs
earth_cmes = tracker.get_earth_directed_cmes(hours=168)
print(f"Earth-directed: {len(earth_cmes)}")

# Get high-speed CMEs (>1000 km/s)
fast_cmes = [c for c in recent if c['speed'] and c['speed'] >= 1000]
print(f"O/R/ER-type: {len(fast_cmes)}")
```

### Export Monthly CME Files

```python
from cme_tracker import CMETracker

tracker = CMETracker()

# Export November 2025 CMEs
csv_file = tracker.export_monthly_cmes_csv('2025-11')
md_file = tracker.export_monthly_cmes_markdown('2025-11')

print(f"Created: {csv_file}")
print(f"Created: {md_file}")
```

Output files:
- `reports/2025-11/cmes-2025-11.csv`
- `reports/2025-11/cmes-2025-11.md`

### CSV Format

```csv
#,NASA Alert,Start Time,Type,Speed (km/s),Half-Angle,Direction,Arrival Time,Uncertainty,Confidence,Detection
1,https://...,2025-11-03T09:36:00Z,O-type,1034,45,-56/24,2025-11-03T22:21Z,±7h,Medium,STEREO A/GOES/SOHO
2,https://...,2025-11-02T14:12:00Z,C-type,653,38,12/5,,,Low,SOHO
```

### Markdown Format

```markdown
# CMEs - November 2025

| # | Start Time | Type | Speed | Half-Angle | Direction | Arrival Time | Confidence | NASA Alert |
|---|------------|------|-------|------------|-----------|--------------|------------|------------|
| 1 | 2025-11-03T09:36:00Z | O-type | 1034 km/s | 45° | -56/24 | 2025-11-03T22:21Z ± 7h | Medium | [Link](https://...) |
| 2 | 2025-11-02T14:12:00Z | C-type | 653 km/s | 38° | 12/5 | - | - | [Link](https://...) |
```

---

## Code Implementation Plan

### Files to Create

1. **`cme_tracker.py`** - Core CME tracking module (~400 lines)
   - Database initialization
   - API fetching
   - Message body parsing
   - Storage and queries
   - Export methods

2. **`test_cme_tracker.py`** - Test script (~150 lines)
   - Test API fetching
   - Test parsing logic
   - Test database operations
   - Test export functionality

3. **`docs/CME_TRACKING.md`** - User documentation (~300 lines)
   - Feature overview
   - Usage examples
   - API details
   - Troubleshooting

### Files to Modify

1. **`space_weather_automation.py`**
   - Add `collect_cme_data()` method
   - Pass CME data to report templates
   - Update report generation workflow

2. **`config.yaml`**
   - Add `cme:` section with settings

3. **`scheduler.py`**
   - Include CME collection in scheduled runs

4. **`requirements.txt`**
   - No new dependencies needed (uses existing `requests`, `sqlite3`)

### Implementation Order

1. ✅ **Phase 1:** Create `cme_tracker.py` with database and basic fetching
2. ✅ **Phase 2:** Implement messageBody parsing logic
3. ✅ **Phase 3:** Add export methods (CSV, Markdown)
4. ✅ **Phase 4:** Create test script and verify functionality
5. ✅ **Phase 5:** Integrate with `space_weather_automation.py`
6. ✅ **Phase 6:** Update report templates (HTML, Markdown, JSON, Text)
7. ✅ **Phase 7:** Update configuration and documentation
8. ✅ **Phase 8:** Test full integration end-to-end

### Estimated Implementation Time

- **Phase 1-2:** 2-3 hours (database + parsing)
- **Phase 3-4:** 1-2 hours (export + testing)
- **Phase 5-6:** 2-3 hours (report integration)
- **Phase 7-8:** 1-2 hours (config + docs)

**Total:** 6-10 hours of development time

---

## Testing Strategy

### Unit Tests

```python
def test_parse_cme_body():
    """Test parsing of CME messageBody"""
    tracker = CMETracker()

    sample_body = """
    ## Summary:
    O-type CME detected by STEREO A / GOES / SOHO.
    Start time of the event: 2025-11-03T09:36Z.
    Estimated speed: ~1034 km/s.
    """

    parsed = tracker.parse_cme_body(sample_body)
    assert parsed['cme_type'] == 'O'
    assert parsed['speed'] == 1034
    assert parsed['start_time'] == '2025-11-03T09:36Z'
```

### Integration Tests

```python
def test_full_workflow():
    """Test complete fetch-parse-store-export workflow"""
    tracker = CMETracker()

    # Fetch from API
    notifications = tracker.fetch_cme_notifications('2025-10-27', '2025-11-03')
    assert len(notifications) > 0

    # Store in database
    count = tracker.store_cmes(notifications)
    assert count > 0

    # Query back
    recent = tracker.get_recent_cmes(hours=168)
    assert len(recent) == count

    # Export
    csv_file = tracker.export_monthly_cmes_csv('2025-11')
    assert os.path.exists(csv_file)
```

---

## Error Handling

### API Errors

```python
def fetch_cme_notifications(self, start_date, end_date):
    """Fetch with error handling"""
    try:
        url = f"{self.api_base_url}?startDate={start_date}&endDate={end_date}&type=CME"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        self.logger.error("NASA DONKI API timeout")
        return []
    except requests.RequestException as e:
        self.logger.error(f"Failed to fetch CMEs: {e}")
        return []
    except json.JSONDecodeError:
        self.logger.error("Invalid JSON response from DONKI")
        return []
```

### Parsing Errors

```python
def parse_cme_body(self, message_body):
    """Parse with graceful degradation"""
    parsed = {}
    try:
        # Attempt to parse each field
        # If any field fails, continue with others
        # Log warnings for missing fields
    except Exception as e:
        self.logger.warning(f"Error parsing CME body: {e}")
        # Return partial data
    return parsed
```

---

## Future Enhancements

### Phase 2 Features (Future)

1. **CME-Flare Association**
   - Link CMEs to their source flares
   - Track timing correlation
   - Enhance report context

2. **Historical Analysis**
   - Track CME frequency trends
   - Speed distribution statistics
   - Earth-impact frequency

3. **Alert System**
   - Email notifications for Earth-directed CMEs
   - SMS alerts for high-speed events
   - Integration with notification services

4. **Visualization**
   - CME speed timeline chart
   - Direction polar plot
   - Arrival prediction calendar

5. **Additional DONKI Data**
   - Geomagnetic Storms (GST)
   - Solar Energetic Particles (SEP)
   - Interplanetary Shocks (IPS)
   - Magnetopause Crossings (MPC)
   - Radiation Belt Enhancements (RBE)

---

## References

### NASA DONKI Resources

- **API Documentation:** https://ccmc.gsfc.nasa.gov/tools/DONKI/
- **Web Interface:** https://kauai.ccmc.gsfc.nasa.gov/DONKI/
- **Alert Archive:** https://kauai.ccmc.gsfc.nasa.gov/DONKI/search/
- **WSA-ENLIL Model:** https://ccmc.gsfc.nasa.gov/models/ENLIL~2.9/

### Related Documentation

- **[MONTHLY_FLARE_FILES.md](MONTHLY_FLARE_FILES.md)** - Similar export pattern
- **[flare_tracker_simple.py](../flare_tracker_simple.py)** - Similar code structure
- **[space_weather_automation.py](../space_weather_automation.py)** - Integration point

---

## Summary

This plan provides a comprehensive roadmap for integrating NASA DONKI CME data:

1. ✅ **Data Structure:** Fully analyzed and documented
2. ✅ **Fields Identified:** 22 fields covering all CME parameters
3. ✅ **Database Schema:** Designed with indexes and rolling window
4. ✅ **Parsing Strategy:** Regex patterns for all fields
5. ✅ **Integration Points:** Clear connection to existing system
6. ✅ **Export Formats:** CSV and Markdown like flare files
7. ✅ **Error Handling:** Robust fallback strategies
8. ✅ **Testing Plan:** Unit and integration tests defined

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 1 implementation (database + fetching)
3. Test with real API data
4. Integrate with report generation
5. Deploy and monitor

---

**Status:** ✅ PLAN COMPLETE - READY FOR IMPLEMENTATION
**Date:** November 3, 2025
**Estimated Effort:** 6-10 hours
