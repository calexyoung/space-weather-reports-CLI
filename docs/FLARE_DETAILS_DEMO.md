# CME Table with Flare Details - Implementation Complete

## Enhancement Applied

The CME arrivals table now extracts and displays flare information from NASA DONKI notes.

## Example Output

### Before (Old Format):
```
CME #1: 2025-11-05T10:53:00-CME-001
Start: 2025-11-05T10:53Z | Associated Flare: 2025-11-05T10:36:00-FLR-001 | NASA DONKI Alert
```

### After (New Format):
```
CME #1: 2025-11-05T10:53:00-CME-001
Start: 2025-11-05T10:53Z | Associated Flare: 2025-11-05T10:36:00-FLR-001 (M7.4 from AR14274 (N24E47)) | NASA DONKI Alert
```

## How It Works

1. **Data Source**: NASA DONKI CME notifications include a "note" field with flare details
   - Example note: "...M7.4 class flare from AR 14274 (N24E47) that peaked at..."

2. **Extraction Pattern**: Uses regex to find:
   - Flare class (M7.4, C8.7, X2.3, etc.)
   - Active region number (AR 14274)
   - Heliographic location (N24E47)

3. **Display Format**: `(CLASS from ARREGION (LOCATION))`
   - Example: `(M7.4 from AR14274 (N24E47))`

## Implementation Details

### Helper Function Added
```python
@staticmethod
def _extract_flare_details_from_note(note: str) -> str:
    """Extract flare class and region from CME note field."""
    # Handles patterns like:
    # "M7.4 class flare from AR 14274 (N24E47)"
    # "C8.7 flare from AR 14274 (N24E59)"
```

### CME Table Updated
```python
if associated_flare:
    note = cme.get('note', '')
    flare_details = EnhancedClaudeReportGenerator._extract_flare_details_from_note(note)

    if flare_details:
        html += f""" | <strong>Associated Flare: {associated_flare} ({flare_details})</strong>"""
    else:
        html += f""" | <strong>Associated Flare: {associated_flare}</strong>"""
```

## Testing

The extraction function successfully parses real NASA DONKI notes:

**Input:**
```
CME first seen in real time to the E in STEREO A COR2 starting at 2025-11-05T10:53Z.
CME is also seen in GOES CCOR-1 as a halo with the bulk to the E. CME was missed by
SOHO LASCO C2/C3 in real time due to a scheduled gap between downlink periods. The CME
is most likely associated with a long-duration M7.4 class flare from AR 14274 (N24E47)
that peaked at 2025-11-05T11:19Z.
```

**Extracted:**
```
M7.4 from AR14274 (N24E47)
```

## Files Modified

- ✅ `claude_integration_enhanced.py` - Added `_extract_flare_details_from_note()` helper
- ✅ `claude_integration_enhanced.py` - Updated CME header display logic
- ✅ Backup created: `claude_integration_enhanced.py.backup2`

## Next Report Generation

The next time a report is generated with CME arrivals that have associated flares, the table will automatically display:

```
CME #1: 2025-11-05T10:53:00-CME-001
Start: 2025-11-05T10:53Z | Associated Flare: 2025-11-05T10:36:00-FLR-001 (M7.4 from AR14274 (N24E47))
```

This provides immediate context about:
- **What class flare** caused the CME (M7.4)
- **Which active region** (AR14274)
- **Where on the Sun** (N24E47 = North 24°, East 47°)

Perfect for quickly understanding CME origins!
