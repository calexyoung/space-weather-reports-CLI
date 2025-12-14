# Space Weather Report Generation - Complete Flow

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  User runs: python3.11 space_weather_automation.py             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Flare Collection (Pre-Report)                         │
│  • Collect latest flares before generating report               │
│  • Update 24-hour rolling database                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Data Fetching (Parallel HTTP Requests)                │
│  • NOAA SWPC Discussion                                         │
│  • UK Met Office Forecast                                       │
│  • SIDC Forecast                                                │
│  • Alternative sources (spaceweather.com, etc.)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Database Queries                                       │
│  • Query flare_database.db (last 24 hours)                      │
│  • Sync CMEs from NASA DONKI API                                │
│  • Query CMEs observed (last 24 hours)                          │
│  • Query CME arrivals (next 3 days forecast)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Data Package Assembly                                  │
│  • Combine all fetched data into single dictionary              │
│  • Format for Claude API consumption                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Report Generation (Claude API)                         │
│  • Build detailed prompt with all data                          │
│  • Call Claude Sonnet 4 API                                     │
│  • Generate narrative HTML report                               │
│  • (OR fallback templates if API unavailable)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Data Table Generation (Post-Processing)                │
│  • Generate Solar Flares HTML table                             │
│  • Generate CMEs Observed HTML table                            │
│  • Generate CME Arrivals HTML table                             │
│  • Append all three tables to report                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: Format Conversion                                      │
│  • Convert HTML → Markdown                                      │
│  • Convert data → JSON                                          │
│  • Convert HTML → Plain Text                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: File Output                                            │
│  • Save to reports/YYYY-MM/ directory                           │
│  • 4 files: .html, .md, .json, .txt                             │
│  • Monthly exports: flares-YYYY-MM.csv, cmes-YYYY-MM.csv        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 9: Cleanup                                                │
│  • Delete reports older than 30 days                            │
│  • Log completion                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Step-by-Step Execution

### STEP 1: Pre-Report Flare Collection
**File:** `space_weather_automation.py`
**Method:** `main()` → calls flare collection before report

```python
# Line ~602-610
def main():
    try:
        generator = SpaceWeatherReportGenerator()

        # Pre-report flare collection
        if generator.config.get('flare_tracking', {}).get('enabled', True):
            generator.collect_flares_before_report()  # ← STEP 1

        # Generate and save reports
        generator.generate_and_save_reports()
```

**What happens:**
1. Import `FlareTracker` from `flare_tracker_simple.py`
2. Call `collect_recent_flares()`
3. Fetch from LMSAL latest events table (20 most recent)
4. Cross-reference with NOAA SWPC discussion
5. Store in `flare_database.db` with duplicate prevention
6. Delete flares older than 24 hours
7. Log: "Pre-report flare collection successful: X new flares added, Y total in 24h window"

**Database:** `flare_database.db`
```sql
INSERT OR IGNORE INTO flares (event_date, event_time, flare_class, region, location, ...)
VALUES (?, ?, ?, ?, ?, ...)
```

---

### STEP 2: Data Fetching (HTTP Requests)
**File:** `space_weather_automation.py`
**Method:** `generate_report_data()`

#### 2A. Calculate Time Windows
```python
# Lines ~117-124
now = datetime.now(timezone.utc)
analysis_start = now - timedelta(hours=24)  # 24 hours ago
forecast_end = now + timedelta(days=3)      # 3 days ahead
```

#### 2B. Fetch Primary Sources (Sequential)
```python
# Lines ~126-138
def generate_report_data(self):
    data = {}

    # Fetch NOAA SWPC Discussion
    data['noaa_discussion'] = self.fetch_noaa_discussion()  # ← HTTP GET

    # Fetch UK Met Office
    data['uk_met_office'] = self.fetch_uk_met_office()     # ← HTTP GET

    # Fetch SIDC Forecast
    data['sidc_forecast'] = self.fetch_sidc_forecast()     # ← HTTP GET
```

**HTTP Requests:**
- **NOAA**: `https://services.swpc.noaa.gov/text/3-day-forecast.txt`
- **UK Met Office**: URL from `config.yaml`
- **SIDC**: URL from `config.yaml`
- **Timeout**: 30 seconds per request
- **Error handling**: Logs error, continues with None value

#### 2C. Fetch Alternative Sources
```python
# Lines ~140-142
data['alternative_sources'] = self.fetch_alternative_sources()
```

**Alternative URLs** (from `config.yaml`):
- spaceweather.com
- earthsky.org
- spaceweatherlive.com

---

### STEP 3: Database Queries
**File:** `space_weather_automation.py`
**Methods:** Multiple query methods

#### 3A. Flare Summary Query
```python
# Line ~144
data['flare_summary'] = self.get_flare_summary()
```

**What it does:**
```python
# Lines ~157-165
def get_flare_summary(self):
    conn = sqlite3.connect('flare_database.db')
    cursor = conn.cursor()

    # Get flares from last 24 hours
    cursor.execute('''
        SELECT * FROM flares
        WHERE event_timestamp >= ?
        ORDER BY event_timestamp DESC
    ''', (cutoff_timestamp,))

    flares = cursor.fetchall()
    # Returns: {'total': 23, 'strongest': 'M1.8', 'activity_level': 'moderate', ...}
```

#### 3B. Detailed Flares Query
```python
# Line ~147
data['flares_detailed'] = self.get_flares_for_report_period(analysis_start, now)
```

**Returns:** List of flare dictionaries with full details:
```python
[
    {
        'event_date': '2025-11-07',
        'event_time': '07:16',
        'flare_class': 'M1.8',
        'region': 'AR4274',
        'location': 'N22E27',
        'source': 'LMSAL'
    },
    # ... more flares
]
```

#### 3C. CME Sync from NASA DONKI
```python
# Line ~148-149
data['cmes_observed'] = self.get_cmes_for_report_period(analysis_start, now)
```

**What happens internally:**
```python
# Lines ~231-249
def get_cmes_for_report_period(self, start_time, end_time):
    from cme_tracker_enhanced import EnhancedCMETracker

    tracker = EnhancedCMETracker()

    # Fetch from NASA DONKI API (last 7 days)
    tracker.sync_cmes(
        (now - timedelta(days=7)).strftime('%Y-%m-%d'),
        now.strftime('%Y-%m-%d')
    )

    # Query database for analysis period
    cmes = tracker.get_cmes_for_period(start_time, end_time)
    return cmes
```

**NASA DONKI API Call:**
```
GET https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/CMEAnalysis
    ?startDate=2025-10-31
    &endDate=2025-11-07
    &mostAccurateOnly=true
```

**Database:** `space_weather.db`
```sql
-- CMEs stored in enhanced structure
INSERT OR REPLACE INTO cmes_enhanced (
    activity_id, start_time, source_region, source_location,
    associated_flare, note, catalog, instruments, donki_url, ...
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ...)

-- Analyses (LE and SH)
INSERT INTO cme_analyses (
    cme_id, analysis_type, speed, half_angle, direction_lon, direction_lat, ...
) VALUES (?, ?, ?, ?, ?, ?, ...)

-- Model runs with arrival predictions
INSERT INTO cme_model_runs (
    analysis_id, run_number, earth_arrival_timestamp, earth_arrival_time,
    kp_90, kp_135, kp_180, rmin_earth_radii, ...
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ...)
```

#### 3D. CME Arrival Predictions Query
```python
# Line ~151
data['cmes_predicted'] = self.get_predicted_cme_arrivals(now, forecast_end)
```

**What it does:**
```python
# Lines ~251-284
def get_predicted_cme_arrivals(self, start_time, end_time, uncertainty_hours=7):
    tracker = EnhancedCMETracker()

    # Query CMEs with Earth arrivals in forecast window (±7 hours)
    arrivals = tracker.get_cmes_with_arrivals_in_window(
        start_time, end_time, uncertainty_hours
    )

    # Returns CMEs with model_runs that have earth_arrival_timestamp
    # in the specified window
```

**SQL Query:**
```sql
SELECT DISTINCT c.*
FROM cmes_enhanced c
JOIN cme_analyses a ON c.id = a.cme_id
JOIN cme_model_runs m ON a.id = m.analysis_id
WHERE m.earth_arrival_timestamp >= ?
  AND m.earth_arrival_timestamp <= ?
ORDER BY c.start_timestamp DESC
```

---

### STEP 4: Data Package Assembly
**File:** `space_weather_automation.py`
**Method:** `generate_report_data()`

```python
# Lines ~153-154
data['timestamp'] = now.isoformat()
return data  # ← Complete data package
```

**Data structure:**
```python
{
    'noaa_discussion': "...",              # Primary text source
    'uk_met_office': "...",                # Forecast text
    'sidc_forecast': "...",                # Forecast text
    'alternative_sources': {...},          # Dict of alt sources
    'flare_summary': {...},                # Summary stats
    'flares_detailed': [...],              # List of flare dicts
    'cmes_observed': [...],                # CMEs in analysis period
    'cmes_predicted': [...],               # CMEs arriving in forecast
    'analysis_period': {                   # Time windows
        'start': '2025-11-06T21:06:00+00:00',
        'end': '2025-11-07T21:06:00+00:00'
    },
    'forecast_period': {
        'start': '2025-11-07T21:06:00+00:00',
        'end': '2025-11-10T21:06:00+00:00'
    },
    'timestamp': '2025-11-07T21:06:00+00:00'
}
```

---

### STEP 5: Report Generation (Claude API)
**File:** `claude_integration_enhanced.py`
**Method:** `generate_report(data)`

#### 5A. Check API Availability
```python
# Lines ~50-51
def generate_report(self, data):
    if not self.enabled:  # Check if API key present
        return self._generate_fallback_report(data)  # ← Fallback templates
```

#### 5B. Build Comprehensive Prompt
```python
# Lines ~54-55
prompt = self._build_detailed_prompt(data)
```

**Prompt structure** (Lines 94-500+):
```python
f"""You are an expert space weather forecaster creating a comprehensive daily report.

Generate a professional space weather report for {now.strftime('%B %d, %Y')} (UTC)...

# PRIMARY DATA SOURCES

## NOAA SWPC Discussion (Most Authoritative)
{data.get('noaa_discussion', 'Not available')}

## UK Met Office Space Weather Forecast
{data.get('uk_met_office', 'Not available')}

## SIDC Forecast
{data.get('sidc_forecast', 'Not available')}

## 24-Hour Flare Tracking Database
{self._format_flare_summary(data.get('flare_summary'))}

## CME Tracking Database (Enhanced with Analyses & Model Runs)
{self._format_cme_data(data.get('cmes_observed', []))}

## CME Arrival Predictions (Forecast Period)
{self._format_cme_data(data.get('cmes_predicted', []))}

# REPORT STRUCTURE AND REQUIREMENTS
[... detailed instructions for HTML structure ...]

# CRITICAL EDITORIAL IMPROVEMENTS - APPLY THESE:
[... aurora visibility, CME details, etc. ...]

# DETAILED SECTIONS
[... instructions for each section ...]

# HYPERLINK REQUIREMENTS
[... all required links and formats ...]

# FORMATTING REQUIREMENTS
[... HTML tags, bold text rules ...]
"""
```

**Formatted flare data example:**
```
**24-Hour Flare Tracking Database:**
- Total flares in 24h window: 23
- Strongest flare: M1.8 at 07:16 UTC from AR4274 (N22E27)
- Activity level: moderate
- M-class: 1, C-class: 22

Flare #1: M1.8 [LMSAL]
- Date: 2025-11-07
- Times: Start 06:31 UTC, Peak 07:16 UTC, End 07:27 UTC
- Region: AR4274
- Location: N22E27

[... more flares ...]
```

**Formatted CME data example:**
```
**CME #1: 2025-11-07T07:23:00-CME-001**
- Start time: 2025-11-07T07:23Z
- Source: N27E27 (Region 4274)
- Associated flare: 2025-11-07T06:31:00-FLR-001
- Analyses: 2 (LE+SH)
  - **LE Analysis:** 617 km/s
    - Model runs with Earth impact: 1
      - Run 1: Arrival 2025-11-09T18:00Z
        Kp estimates: 90°=4, 135°=6, 180°=6
        Rmin: 0.5 Earth radii
  - **SH Analysis:** 636 km/s
    - Model runs with Earth impact: 1
      - Run 1: Arrival 2025-11-09T13:47Z
        Kp estimates: 90°=5, 135°=7, 180°=7
```

#### 5C. Call Claude API
```python
# Lines ~58-66
message = self.client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    temperature=0.7,
    messages=[{
        "role": "user",
        "content": prompt
    }]
)

# Extract HTML from response
html_report = self._extract_html(message.content[0].text)
```

**What Claude generates:**
- Complete narrative HTML report
- Headline with prioritization
- Top story paragraph
- Detailed sections (flares, sunspots, CMEs, solar wind, geomagnetic)
- 3-day forecast
- All hyperlinks and formatting
- **Does NOT include data tables** (added next)

#### 5D. Fallback Templates (if API fails)
```python
# Lines ~838-900+
def _generate_fallback_report(self, data):
    # Basic HTML structure with minimal narrative
    # Just data display, no AI-generated content
```

---

### STEP 6: Data Table Generation
**File:** `claude_integration_enhanced.py`
**Method:** `_append_data_tables(html_report, data)`

```python
# Lines ~71-72
html_report = self._append_data_tables(html_report, data)
```

#### 6A. Add Separator and Header
```python
# Lines ~519-530
html = report_html
html += """
<hr style="margin: 30px 0; border: none; border-top: 2px solid #bdc3c7;">

<h2 style="color: #2c3e50; margin-top: 30px;">Detailed Activity Data</h2>
"""
```

#### 6B. Generate Solar Flares Table
```python
# Lines ~533-538
flares = data.get('flares_detailed', [])
if flares:
    html += "\n" + self.generate_flares_html_table(flares)
```

**Table structure:**
```html
<h3>Solar Flares - Analysis Period</h3>
<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Class</th>
      <th>Date</th>
      <th>Start Time (UTC)</th>
      <th>Peak Time (UTC)</th>
      <th>End Time (UTC)</th>
      <th>Region</th>
      <th>Location</th>
    </tr>
  </thead>
  <tbody>
    <!-- X-class: red background -->
    <tr style="background-color: #ffcccc;">...</tr>
    <!-- M-class: orange background -->
    <tr style="background-color: #ffe6cc;">...</tr>
    <!-- C-class: white background -->
    <tr style="background-color: #ffffff;">...</tr>
  </tbody>
</table>
```

#### 6C. Generate CMEs Observed Table
```python
# Lines ~541-546
cmes_observed = data.get('cmes_observed', [])
if cmes_observed:
    html += "\n" + self.generate_cmes_observed_html_table(cmes_observed)
```

**Table structure:**
```html
<h3>Coronal Mass Ejections (CMEs) - Analysis Period</h3>
<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Start Time</th>
      <th>Type</th>
      <th>Speed (km/s)</th>
      <th>Direction</th>
      <th>Earth Impact</th>
      <th>Associated Flare</th>
      <th>NASA Alert</th>
    </tr>
  </thead>
  <tbody>
    <!-- Earth-directed: light red background -->
    <tr style="background-color: #ffe6e6;">...</tr>
    <!-- Non-Earth: white background -->
    <tr style="background-color: #ffffff;">...</tr>
  </tbody>
</table>
```

#### 6D. Generate CME Arrivals Table
```python
# Lines ~549-554
cmes_predicted = data.get('cmes_predicted', [])
if cmes_predicted:
    html += "\n" + self.generate_cme_arrivals_html_table(cmes_predicted)
```

**Card-based layout:**
```html
<h3>Predicted CME Arrivals - Forecast Period</h3>

<!-- CME Card -->
<div style="border: 2px solid #2c3e50; border-radius: 8px;">
  <!-- CME Header -->
  <div style="background-color: #34495e; color: white;">
    <h4>CME #1: 2025-11-07T07:23:00-CME-001</h4>
    <p>Start: 2025-11-07T07:23Z |
       Associated Flare: 2025-11-07T06:31:00-FLR-001 (M1.7 from AR4274 (N27E27)) |
       NASA DONKI Alert</p>
  </div>

  <!-- LE Analysis Section -->
  <div style="background-color: #3498db; color: white;">
    LE Analysis: 617 km/s | 5 arrival prediction(s)
  </div>
  <table>
    <thead>
      <tr>
        <th>Run #</th>
        <th>Target</th>
        <th>Predicted Arrival</th>
        <th>Kp Est.</th>
        <th>Details</th>
      </tr>
    </thead>
    <tbody>
      <!-- Earth arrival: light red -->
      <tr style="background-color: #ffe6e6;">
        <td>1</td>
        <td>Earth</td>
        <td>2025-11-09T18:00Z</td>
        <td>4-6</td>
        <td>Kp 90°=4, 135°=6, 180°=6 | Rmin=0.5 RE</td>
      </tr>
      <!-- Spacecraft: light yellow -->
      <tr style="background-color: #fff9e6;">
        <td>1</td>
        <td>BepiColombo</td>
        <td>2025-11-09T15:00Z</td>
        <td>—</td>
        <td>—</td>
      </tr>
    </tbody>
  </table>

  <!-- SH Analysis Section -->
  <div style="background-color: #e67e22; color: white;">
    SH Analysis: 636 km/s | 1 arrival prediction(s)
  </div>
  <table>
    <!-- Same structure -->
  </table>
</div>

<!-- Summary -->
<p>Summary: 3 CME event(s) with arrival predictions |
   Earth arrivals: 8 | Spacecraft arrivals: 5</p>
```

#### 6E. Extract Flare Details from CME Notes
**Method:** `_extract_flare_details_from_note(note)` (Lines 1094-1151)

```python
# Regex patterns to extract from NASA notes:
# Pattern 1: "M7.4 flare and subsequent eruption from Active Region 14274 (N30E41)"
# Pattern 2: "M1.7 flare from Active Region 14274 (N27E27)"
# Pattern 3: "M7.4 class flare from AR 14274 (N24E47)"

# Extracts → "M7.4 from AR14274 (N30E41)"
```

---

### STEP 7: Format Conversion
**File:** `claude_integration_enhanced.py`
**Methods:** Multiple conversion methods

#### 7A. HTML → Markdown
```python
# Lines ~779-803
def _convert_to_markdown(self, html: str) -> str:
    md = html

    # Convert headers
    md = re.sub(r'<h3>(.*?)</h3>', r'## \1', md)
    md = re.sub(r'<h4>(.*?)</h4>', r'### \1', md)

    # Convert formatting
    md = re.sub(r'<strong>(.*?)</strong>', r'**\1**', md)
    md = re.sub(r'<em>(.*?)</em>', r'*\1*', md)

    # Convert lists
    md = md.replace('<ul>', '')
    md = md.replace('</ul>', '')
    md = re.sub(r'<li>(.*?)</li>', r'- \1', md, flags=re.DOTALL)

    # Convert links
    md = re.sub(r'<a href="(.*?)"[^>]*>(.*?)</a>', r'[\2](\1)', md)

    # Clean up whitespace
    md = re.sub(r'\n\s*\n', '\n\n', md)

    return md.strip()
```

#### 7B. Data → JSON
```python
# Lines ~805-812
def _convert_to_json(self, data: Dict) -> str:
    import json

    # Structure data with metadata
    output = {
        'timestamp': data.get('timestamp'),
        'sources': {
            'noaa_discussion': 'available' if data.get('noaa_discussion') else 'unavailable',
            'uk_met_office': 'available' if data.get('uk_met_office') else 'unavailable',
            'sidc_forecast': 'available' if data.get('sidc_forecast') else 'unavailable',
            'alternative_sources': len(data.get('alternative_sources', {}))
        },
        'raw_data': data
    }

    return json.dumps(output, indent=2, default=str)
```

#### 7C. HTML → Plain Text
```python
# Lines ~814-836
def _convert_to_text(self, html: str) -> str:
    import re

    text = html

    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities
    text = text.replace('&quot;', '"')
    text = text.replace('&apos;', "'")
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')

    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()
```

#### 7D. Return All Formats
```python
# Lines ~74-79
return {
    'html': html_report,
    'markdown': self._convert_to_markdown(html_report),
    'json': self._convert_to_json(data),
    'text': self._convert_to_text(html_report)
}
```

---

### STEP 8: File Output
**File:** `space_weather_automation.py`
**Method:** `save_reports(reports, timestamp)`

#### 8A. Create Directory Structure
```python
# Lines ~547-552
def save_reports(self, reports, timestamp):
    # Create monthly subdirectory
    year_month = timestamp.strftime('%Y-%m')
    output_dir = Path(self.config['output']['directory']) / year_month
    output_dir.mkdir(parents=True, exist_ok=True)
```

**Directory structure:**
```
reports/
└── 2025-11/
    ├── space_weather_2025-11-07_2106.html
    ├── space_weather_2025-11-07_2106.md
    ├── space_weather_2025-11-07_2106.json
    ├── space_weather_2025-11-07_2106.txt
    ├── flares-2025-11.csv
    ├── flares-2025-11.md
    ├── cmes-2025-11.csv
    └── cmes-2025-11.md
```

#### 8B. Save Each Format
```python
# Lines ~554-578
# Filename pattern
base_filename = f"space_weather_{timestamp.strftime('%Y-%m-%d_%H%M')}"

# Save HTML
if reports.get('html'):
    html_path = output_dir / f"{base_filename}.html"
    html_path.write_text(reports['html'])
    self.logger.info(f"Saved report: {html_path}")

# Save Markdown
if reports.get('markdown'):
    md_path = output_dir / f"{base_filename}.md"
    md_path.write_text(reports['markdown'])
    self.logger.info(f"Saved report: {md_path}")

# Save JSON
if reports.get('json'):
    json_path = output_dir / f"{base_filename}.json"
    json_path.write_text(reports['json'])
    self.logger.info(f"Saved report: {json_path}")

# Save Text
if reports.get('text'):
    txt_path = output_dir / f"{base_filename}.txt"
    txt_path.write_text(reports['text'])
    self.logger.info(f"Saved report: {txt_path}")
```

#### 8C. Monthly Exports
```python
# Lines ~580-585
# Export monthly flare CSV/MD
if flares in last 30 days:
    export_monthly_flares_csv(year_month)
    export_monthly_flares_markdown(year_month)

# Export monthly CME CSV/MD
if cmes in last 30 days:
    export_monthly_cmes_csv(year_month)
    export_monthly_cmes_markdown(year_month)
```

---

### STEP 9: Cleanup
**File:** `space_weather_automation.py`
**Method:** `cleanup_old_reports()`

```python
# Lines ~587-595
def cleanup_old_reports(self):
    max_age_days = self.config['output'].get('max_archive_days', 30)
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)

    reports_dir = Path(self.config['output']['directory'])

    for report_file in reports_dir.glob('**/*.*'):
        if report_file.stat().st_mtime < cutoff.timestamp():
            report_file.unlink()
            self.logger.info(f"Deleted old report: {report_file}")
```

---

## Error Handling Throughout

### HTTP Fetch Errors
```python
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text
except requests.RequestException as e:
    self.logger.error(f"Failed to fetch {source}: {e}")
    return None  # Continue with other sources
```

### Database Errors
```python
try:
    conn = sqlite3.connect('flare_database.db')
    # ... query ...
except sqlite3.Error as e:
    self.logger.error(f"Database error: {e}", exc_info=True)
    return []  # Return empty list, don't crash
```

### API Errors
```python
try:
    message = self.client.messages.create(...)
except Exception as e:
    print(f"Error generating report with Claude: {e}")
    return self._generate_fallback_report(data)  # ← Fallback templates
```

### File Write Errors
```python
try:
    path.write_text(content)
    self.logger.info(f"Saved report: {path}")
except IOError as e:
    self.logger.error(f"Failed to save {path}: {e}")
    # Continue - don't crash entire report generation
```

---

## Performance Characteristics

### Timing
- **Flare collection**: ~2-5 seconds
- **Data fetching**: ~5-10 seconds (parallel-ish)
- **Database queries**: ~0.5-1 second
- **Claude API call**: ~40-60 seconds (largest bottleneck)
- **Table generation**: ~0.5-1 second
- **Format conversion**: ~0.5-1 second
- **File writing**: ~0.1 second
- **Total**: ~50-80 seconds per report

### API Token Usage
- **Prompt**: ~12,000 tokens (input)
- **Response**: ~3,000-4,000 tokens (output)
- **Cost**: ~$0.18-0.24 per report (Sonnet 4 pricing)

### Data Volumes
- **Flares/day**: ~20-50 events
- **CMEs/week**: ~5-15 events
- **Database size**: ~5-10 MB (with 30-day retention)
- **Report size**: ~50-70 KB HTML

---

## Configuration Points

All configurable via `config.yaml`:

```yaml
output:
  directory: "reports"
  formats:
    html: true
    markdown: true
    json: true
    text: true
  max_archive_days: 30

flare_tracking:
  enabled: true
  database: "flare_database.db"
  retention_hours: 24

schedule:
  interval_hours: 6
```

---

## Summary Diagram

```
┌──────────────┐
│  User runs   │
│  automation  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  1. COLLECT FLARES (pre-report)              │
│     • LMSAL fetch → flare_database.db        │
│     • 24h rolling window                      │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  2. FETCH DATA (HTTP)                        │
│     • NOAA SWPC                              │
│     • UK Met Office                          │
│     • SIDC                                   │
│     • Alternative sources                    │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  3. QUERY DATABASES                          │
│     • Flare summary (last 24h)               │
│     • Flares detailed (last 24h)             │
│     • CMEs observed (last 24h)               │
│     • CME arrivals (next 3 days)             │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  4. ASSEMBLE DATA PACKAGE                    │
│     • Combine all data into single dict      │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  5. GENERATE REPORT (Claude API)             │
│     • Build detailed prompt (~12K tokens)    │
│     • Call Claude Sonnet 4                   │
│     • Generate narrative HTML (~3-4K tokens) │
│     • OR fallback templates if no API        │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  6. GENERATE DATA TABLES (post-process)      │
│     • Flares table (color-coded)             │
│     • CMEs observed table                    │
│     • CME arrivals table (card layout)       │
│     • Append all to HTML                     │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  7. CONVERT FORMATS                          │
│     • HTML → Markdown                        │
│     • Data → JSON                            │
│     • HTML → Text                            │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  8. SAVE FILES                               │
│     • reports/YYYY-MM/*.{html,md,json,txt}   │
│     • Monthly exports: *.csv, *.md           │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  9. CLEANUP                                  │
│     • Delete reports > 30 days old           │
│     • Log completion                         │
└──────────────────────────────────────────────┘
```

This is the complete end-to-end flow!
