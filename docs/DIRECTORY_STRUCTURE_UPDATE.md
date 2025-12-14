# Directory Structure Update - YYYY-MM Organization

## Overview

As of November 3, 2025, the space weather report system has been updated to organize reports by year-month subdirectories (YYYY-MM format) instead of storing all reports in a single directory.

## Implementation Date

November 3, 2025

## New Directory Structure

```
reports/
├── 2025-10/                           # October 2025 reports
│   ├── space_weather_2025-10-31_2124.html
│   ├── space_weather_2025-10-31_2124.md
│   └── ...
├── 2025-11/                           # November 2025 reports
│   ├── space_weather_2025-11-01_0717.html
│   ├── space_weather_2025-11-03_0833.html
│   └── ...
├── 2025-12/                           # December 2025 reports (future)
└── archive/                           # Legacy reports (pre-Nov 2025)
    └── space_weather_*.{html,md,json,txt}
```

## Benefits

### 1. Better Organization
- Reports are grouped by month for easier navigation
- Reduces clutter in the base reports directory
- Makes it easier to find reports from specific time periods

### 2. Improved Performance
- File system operations are faster with fewer files per directory
- Less scrolling when browsing reports in a file manager

### 3. Easier Archival
- Can easily archive or back up entire months at once
- Empty month directories are automatically removed during cleanup

### 4. Better for Long-Term Use
- Scales well as the number of reports grows over time
- Standard YYYY-MM format is widely recognized

## Implementation Details

### Changes Made

**File:** [space_weather_automation.py](../space_weather_automation.py)

#### 1. Updated `save_reports()` Method (lines 296-303)

**Before:**
```python
output_dir = Path(self.config['output']['base_directory'])
output_dir.mkdir(parents=True, exist_ok=True)
```

**After:**
```python
year_month = timestamp.strftime('%Y-%m')  # e.g., "2025-11"

# Create year-month subdirectory
base_dir = Path(self.config['output']['base_directory'])
output_dir = base_dir / year_month
output_dir.mkdir(parents=True, exist_ok=True)
```

#### 2. Updated `cleanup_old_reports()` Method (lines 348-394)

**Enhanced to handle:**
- YYYY-MM subdirectories (new structure)
- Legacy files in base directory (backwards compatibility)
- Automatic removal of empty directories
- Logging of deleted directories

**Key features:**
```python
# YYYY-MM subdirectories
for year_month_dir in base_dir.glob('20*-*'):
    if not year_month_dir.is_dir():
        continue

    # Delete old reports in this directory
    for file in year_month_dir.glob('space_weather_*'):
        if file.is_file() and datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
            file.unlink()

    # Remove empty directories
    if year_month_dir.is_dir() and not list(year_month_dir.iterdir()):
        year_month_dir.rmdir()
```

## Backwards Compatibility

### Legacy File Support
The cleanup system still handles legacy files stored directly in the base `reports/` directory, ensuring smooth transition from the old structure.

### Archive Directory
Existing reports have been moved to the `archive/` subdirectory for preservation.

## Usage Examples

### Generate New Report
```bash
python3 space_weather_automation.py
```

**Output:**
```
Saved report: reports/2025-11/space_weather_2025-11-03_0833.html
Saved report: reports/2025-11/space_weather_2025-11-03_0833.md
Saved report: reports/2025-11/space_weather_2025-11-03_0833.json
Saved report: reports/2025-11/space_weather_2025-11-03_0833.txt
```

### Find Latest Report
```bash
# Current month
ls -t reports/$(date +%Y-%m)/*.html | head -1

# All months
find reports/20*/ -name "*.html" -type f | sort -r | head -1
```

### View Reports from Specific Month
```bash
# November 2025
ls reports/2025-11/

# October 2025
ls reports/2025-10/
```

### Archive Specific Month
```bash
# Compress October 2025 reports
tar -czf reports_2025-10.tar.gz reports/2025-10/

# Remove after archiving
rm -rf reports/2025-10/
```

## Test Results

### Test 1: Report Generation
```bash
$ python3 space_weather_automation.py

2025-11-03 08:32:36 - INFO - Starting report generation...
2025-11-03 08:33:19 - INFO - Saved report: .../reports/2025-11/space_weather_2025-11-03_0833.html
2025-11-03 08:33:19 - INFO - Saved report: .../reports/2025-11/space_weather_2025-11-03_0833.md
2025-11-03 08:33:19 - INFO - Saved report: .../reports/2025-11/space_weather_2025-11-03_0833.json
2025-11-03 08:33:19 - INFO - Saved report: .../reports/2025-11/space_weather_2025-11-03_0833.txt
```

✅ Reports successfully saved to `2025-11/` subdirectory

### Test 2: Directory Creation
```bash
$ ls -la reports/2025-11/
drwxr-xr-x  6 cayoung  staff  192 Nov  3 08:33 .
-rw-r--r--  2 cayoung  staff 8403 Nov  3 08:33 space_weather_2025-11-03_0833.html
-rw-r--r--  2 cayoung  staff 6460 Nov  3 08:33 space_weather_2025-11-03_0833.md
...
```

✅ Directory automatically created with proper permissions

### Test 3: Cleanup Behavior
The enhanced cleanup system:
- ✅ Removes old reports from YYYY-MM directories
- ✅ Removes old legacy files from base directory
- ✅ Deletes empty month directories
- ✅ Logs cleanup actions

## Configuration

No configuration changes are required. The system automatically uses the new directory structure based on the current date.

**Existing settings in `config.yaml` continue to work:**
```yaml
output:
  base_directory: "reports"
  max_archive_days: 30
  archive: true
```

## Migration Notes

### For Existing Installations

1. **No action required** - The system handles both old and new structures
2. **Legacy reports** - Move to `archive/` subdirectory manually if desired:
   ```bash
   mkdir -p reports/archive
   mv reports/space_weather_*.html reports/archive/
   mv reports/space_weather_*.md reports/archive/
   # etc.
   ```

3. **Cleanup will continue** - Old files in base directory are still cleaned up automatically

### For New Installations

New installations will automatically use the YYYY-MM structure from the first report generation.

## Future Considerations

### Potential Enhancements

1. **Year subdirectories** - Could organize as `reports/2025/11/` if annual archiving is needed
2. **Compression** - Automatically compress old months to save space
3. **External archival** - Upload old months to cloud storage
4. **Web interface** - Browse reports by year/month through a simple web UI

### Database Integration

If the system evolves to include a database, the YYYY-MM structure makes it easy to:
- Index reports by month for faster queries
- Archive database records monthly
- Generate monthly summary statistics

## Files Modified

1. **[space_weather_automation.py](../space_weather_automation.py)**
   - Updated `save_reports()` method (lines 296-303)
   - Updated `cleanup_old_reports()` method (lines 348-394)

2. **[reports/README.md](../reports/README.md)**
   - Added directory structure documentation
   - Updated example paths
   - Updated command examples

3. **[docs/DIRECTORY_STRUCTURE_UPDATE.md](DIRECTORY_STRUCTURE_UPDATE.md)** (this file)
   - Complete documentation of the change

## Support

For questions or issues related to the new directory structure:

1. **Check logs:**
   ```bash
   tail -f space_weather_automation.log
   ```

2. **Verify directory creation:**
   ```bash
   ls -la reports/$(date +%Y-%m)/
   ```

3. **Test report generation:**
   ```bash
   python3 space_weather_automation.py
   ```

## References

- **Implementation:** [space_weather_automation.py](../space_weather_automation.py)
- **Reports Directory:** [reports/README.md](../reports/README.md)
- **Configuration:** [config.yaml](../config.yaml)

---

**Status:** ✅ IMPLEMENTED AND TESTED
**Date:** November 3, 2025
**Backwards Compatible:** Yes
