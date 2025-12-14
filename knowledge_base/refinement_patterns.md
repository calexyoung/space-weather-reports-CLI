# Refinement Patterns

Common corrections and improvements identified through refinement sessions. This file helps Claude learn what types of changes are frequently needed.

## Pattern Categories

### Timing and Precision
*Examples will accumulate from sessions*

**Pattern:** Vague time references
- Issue: "a flare this morning"
- Fix: "M5.3 flare peaked at 06:24 UTC"
- Action: Always query flare database for exact times

### Data Completeness
*Examples will accumulate from sessions*

**Pattern:** Missing Kp forecasts
- Issue: "CME will impact Earth on November 7"
- Fix: "CME arriving November 7 at 03:18 UTC with Kp 7-9 (G3-G4 storms)"
- Action: Check CME model runs for Kp estimates

### Scientific Accuracy
*Examples will accumulate from sessions*

**Pattern:** Oversimplified classifications
- Issue: "AR4274 is active"
- Fix: "AR4274 has beta-gamma-delta magnetic configuration, indicating high flare probability"
- Action: Check region magnetic class in data sources

## Frequency Tracking

*Will be updated after each refinement session*

Most common corrections:
1. [Count] - [Pattern type]
2. [Count] - [Pattern type]
3. [Count] - [Pattern type]

## Learning Insights

*Accumulated wisdom from refinement sessions*

- When to add more detail vs keep concise
- Which technical terms need explanation
- Balance between dramatic and accurate headlines
- How to structure multi-day forecasts

## Session Statistics

Total sessions: 0
Total refinements: 0
Most common issues: TBD

*This file will grow with each refinement session*
