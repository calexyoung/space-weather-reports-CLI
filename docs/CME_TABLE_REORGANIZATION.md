# CME Arrivals Table Reorganization

## Problem Identified

The current CME arrivals table shows **individual model runs** as separate rows, making it difficult to see that multiple predictions belong to the same CME event.

### Current Structure (WRONG):
- Row 1-25: Actually ONE CME (M7.4 flare) with LE+SH analyses for 5 targets × 3 runs
- Row 26-34: Actually ONE CME (M1.7 flare) with LE analysis for 5 targets × 2 runs

Users see 34 "CMEs" when there are actually only 2 CME events.

## Solution: CME-Grouped Display

### New Structure (CORRECT):

```
CME #1: [Activity ID]
Start: [time] | Associated Flare: M7.4 | NASA DONKI Alert [link]

  LE Analysis: XXX km/s | 15 arrival prediction(s)
  ┌─────────┬────────┬───────────────┬─────────┬─────────┐
  │ Run #   │ Target │ Arrival Time  │ Kp Est. │ Details │
  ├─────────┼────────┼───────────────┼─────────┼─────────┤
  │ Run 1   │ Earth  │ 2025-11-07... │ 4-6     │ ...     │
  │ Run 2   │ Earth  │ 2025-11-07... │ 4-6     │ ...     │
  │ Run 3   │ Earth  │ 2025-11-07... │ 4-6     │ ...     │
  │ Run 1   │ Mars   │ 2025-11-10... │ —       │ —       │
  │ Run 2   │ Mars   │ 2025-11-10... │ —       │ —       │
  ...
  └─────────┴────────┴───────────────┴─────────┴─────────┘

  SH Analysis: YYY km/s | 10 arrival prediction(s)
  ┌─────────┬────────┬───────────────┬─────────┬─────────┐
  │ Run #   │ Target │ Arrival Time  │ Kp Est. │ Details │
  ├─────────┼────────┼───────────────┼─────────┼─────────┤
  │ Run 1   │ Earth  │ 2025-11-06... │ 5-7     │ ...     │
  ...
  └─────────┴────────┴───────────────┴─────────┴─────────┘

CME #2: [Activity ID]
Start: [time] | Associated Flare: M1.7 | NASA DONKI Alert [link]

  LE Analysis: ZZZ km/s | 9 arrival prediction(s)
  ┌─────────┬────────┬───────────────┬─────────┬─────────┐
  │ Run #   │ Target │ Arrival Time  │ Kp Est. │ Details │
  ...
  └─────────┴────────┴───────────────┴─────────┴─────────┘
```

### Key Features:

1. **CME-Level Grouping**: Each CME gets its own container with:
   - CME number
   - Activity ID
   - Start time
   - **Associated flare** (M7.4, M1.7, etc.)
   - Link to NASA DONKI alert

2. **Analysis-Level Organization**: Within each CME:
   - LE (Leading Edge) analysis in blue
   - SH (Shock) analysis in orange
   - Shows speed and prediction count

3. **Model Run Details**: Each table row shows:
   - Run number (Run 1, Run 2, Run 3...)
   - Target (Earth, Mars, etc.)
   - Predicted arrival time
   - Kp estimates (Earth only)
   - Additional details (Rmin, full Kp breakdown)

4. **Visual Distinction**:
   - Earth arrivals: Light red background (#ffe6e6)
   - Spacecraft arrivals: Light yellow background (#fff9e6)
   - LE sections: Blue header
   - SH sections: Orange header

5. **Summary**: At bottom:
   - Total CME events
   - Total Earth arrivals
   - Total spacecraft arrivals

## Implementation

The new `generate_cme_arrivals_html_table()` function is in:
- `/Users/cayoung/Documents/Obsidian/CAY-power-vault/space-weather-reports/cme_arrivals_table_new.py`

To apply:
1. Replace the function in `claude_integration_enhanced.py` (lines 1094-1250)
2. The new function maintains the same signature and return type
3. No changes needed to calling code

## Benefits

1. **Clarity**: Users immediately see how many CME events there are
2. **Context**: Associated flare information is prominently displayed
3. **Organization**: LE and SH analyses are clearly separated
4. **Detail Preservation**: All model run data is still accessible
5. **Professional**: Looks like official space weather forecast products

## Technical Notes

- Function signature unchanged: `generate_cme_arrivals_html_table(arrivals: list) -> str`
- Input format: Same enhanced CME tracker data structure
- Output: HTML string with new grouped layout
- Backward compatible: Works with existing data pipeline
