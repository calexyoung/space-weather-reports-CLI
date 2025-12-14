# LMSAL Parser Update Guide

## Current Situation

The LMSAL `latest_events` page (https://www.lmsal.com/solarsoft/last_events/) contains a table with flare data in the following HTML structure:

```html
<tr align=center><td>16</td>
<td><A HREF="...">gev_20251102_1233</A></td>
<td>2025/11/02 12:33:00</td>
<td>12:56:00</td>
<td>12:46:00</td>
<td>C8.2</td>
<td>N00W60 ( 4267 )</td>
```

## Table Structure

Each row contains 7 columns:
1. Row number (1, 2, 3...)
2. Event ID (gev_YYYYMMDD_HHMM)
3. Start time (YYYY/MM/DD HH:MM:SS)
4. End time (HH:MM:SS)
5. Peak time (HH:MM:SS)
6. Flare class (C8.2, M1.1, etc.)
7. Location and region (N00W60 ( 4267 ))

## Recommended Parser Implementation

```python
def parse_lmsal_table(html_content: str) -> List[Dict]:
    """Parse LMSAL events table"""
    import re
    from datetime import datetime, timezone

    flares = []

    # Find all table rows
    # Pattern: Row starts with <tr align=center><td>N</td>
    # Followed by 6 more <td> elements

    pattern = r'<tr align=center><td>(\d+)</td>\s*' \
              r'<td><A HREF="[^"]+">gev_(\d{8})_(\d{4})</A></td>\s*' \
              r'<td>([\d/]+\s+[\d:]+)</td>\s*' \
              r'<td>([\d:]+)</td>\s*' \
              r'<td>([\d:]+)</td>\s*' \
              r'<td>([A-Z][\d.]+)</td>\s*' \
              r'<td>([^<]+)'

    for match in re.finditer(pattern, html_content, re.DOTALL):
        row_num = match.group(1)
        date_str = match.group(2)  # YYYYMMDD
        time_str = match.group(3)  # HHMM
        start_full = match.group(4)  # YYYY/MM/DD HH:MM:SS
        end_time = match.group(5)  # HH:MM:SS
        peak_time = match.group(6)  # HH:MM:SS
        flare_class = match.group(7)  # C8.2
        location_raw = match.group(8)  # N00W60 ( 4267 ) or just N00W60

        # Extract region from location
        region_match = re.search(r'\(\s*(\d{4})\s*\)', location_raw)
        region = region_match.group(1) if region_match else None

        # Extract location coordinates
        loc_match = re.search(r'([NS]\d{2}[EW]\d{2})', location_raw)
        location = loc_match.group(1) if loc_match else None

        # Parse datetime
        try:
            event_dt = datetime.strptime(start_full, "%Y/%m/%d %H:%M:%S")
            event_dt = event_dt.replace(tzinfo=timezone.utc)

            flare = {
                'event_time': event_dt.strftime("%Y-%m-%d %H:%M:%S"),
                'event_time_utc': int(event_dt.timestamp()),
                'flare_class': flare_class,
                'region': region,
                'location': location,
                'peak_time': peak_time,
                'end_time': end_time
            }
            flares.append(flare)
        except ValueError as e:
            continue

    return flares
```

## Alternative: Simple Line-by-Line Parser

```python
def parse_lmsal_simple(html_content: str) -> List[Dict]:
    """Simpler parser that processes line by line"""
    import re
    from datetime import datetime, timezone

    flares = []
    lines = html_content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i]

        # Look for start of table row
        if '<tr align=center><td>' in line and 'gev_202' in lines[i+1]:
            try:
                # Row number in current line
                # Event ID in next line
                event_line = lines[i+1]
                start_line = lines[i+2]
                end_line = lines[i+3]
                peak_line = lines[i+4]
                class_line = lines[i+5]
                location_line = lines[i+6]

                # Extract data
                start_match = re.search(r'<td>([\d/]+\s+[\d:]+)</td>', start_line)
                class_match = re.search(r'<td>([A-Z][\d.]+)</td>', class_line)
                location_match = re.search(r'<td>([^<]+)', location_line)

                if start_match and class_match:
                    start_full = start_match.group(1)
                    flare_class = class_match.group(1)
                    location_raw = location_match.group(1) if location_match else ""

                    # Extract region
                    region_match = re.search(r'\(\s*(\d{4})\s*\)', location_raw)
                    region = region_match.group(1) if region_match else None

                    # Parse datetime
                    event_dt = datetime.strptime(start_full, "%Y/%m/%d %H:%M:%S")
                    event_dt = event_dt.replace(tzinfo=timezone.utc)

                    flare = {
                        'event_time': event_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        'event_time_utc': int(event_dt.timestamp()),
                        'flare_class': flare_class,
                        'region': region
                    }
                    flares.append(flare)

                i += 7  # Skip to next row
                continue
            except (ValueError, IndexError):
                pass

        i += 1

    return flares
```

## Implementation Steps

1. **Update `flare_tracker.py`** - Replace `parse_lmsal_html()` with one of the above parsers

2. **Test the parser:**
   ```bash
   python3 -c "
   from flare_tracker import FlareTracker
   tracker = FlareTracker()
   html = tracker.fetch_lmsal_flares()
   if html:
       flares = tracker.parse_lmsal_html(html)
       print(f'Found {len(flares)} flares')
       for f in flares[:5]:
           print(f'{f[\"flare_class\"]} at {f[\"event_time\"]} from AR{f.get(\"region\", \"????\")}')
   "
   ```

3. **Update the scrape workflow** - In `flare_tracker.py`, update `scrape_and_update()` to use LMSAL as primary source

## Implementation Status: ✅ COMPLETE

The LMSAL parser has been **successfully implemented** in [flare_tracker_simple.py](../flare_tracker_simple.py):

### What's Working:
- ✅ Fetches LMSAL latest_events page
- ✅ Parses all 20 flares from HTML table
- ✅ Handles HTML variations (font tags, links, plain text)
- ✅ Extracts: flare class, time, region, location, peak time, end time
- ✅ Stores in database with source='LMSAL'
- ✅ LMSAL as primary source, NOAA as cross-reference
- ✅ Integrated into 4-hour collection cycle
- ✅ Included in report generation
- ✅ All tests passing

### Current Implementation:

The system uses **dual-source approach**:
1. **LMSAL** (primary): Comprehensive 20-flare table with precise timing
2. **NOAA** (secondary): Cross-reference and flare context

Benefits:
- Complete flare coverage (all 20 LMSAL flares)
- Precise timing data (start, peak, end times)
- Exact heliographic locations
- Cross-validated with NOAA mentions

## Testing

After implementing, test with:
```bash
python3 test_flare_tracking.py
```

Expected result:
- 20 flares extracted from LMSAL table
- All with proper timestamps
- Region numbers correctly parsed
- No duplicates in database

## Note

The current NOAA-based solution is production-ready and working. The LMSAL parser is an enhancement for when you need:
- Complete flare coverage (all 20+ flares)
- Precise timing data
- Exact locations

Both approaches can coexist - LMSAL for comprehensive list, NOAA for cross-reference.
