# Space Weather Science Context

This file accumulates scientific knowledge and explanations for space weather phenomena. It helps Claude understand context when refining reports.

## Solar Flares

**Classification:**
- C-class: Minor flares, minimal Earth effects
- M-class: Medium flares, can cause brief radio blackouts
- X-class: Major flares, cause radio blackouts and radiation storms

**CRITICAL - Notation Understanding:**
- "M1.1" = ONE M-class flare with magnitude 1.1 (NOT 11 flares!)
- "M8.6" = ONE M-class flare with magnitude 8.6
- "X2.3" = ONE X-class flare with magnitude 2.3
- The decimal number is the flare's MAGNITUDE, not a count
- Example: "2 M-class flares: M8.6 and M1.1" means TWO total flares

**Timing:**
- Peak time: Moment of maximum X-ray emission
- Duration: Typically 10-60 minutes from start to end
- Multiple flares can occur from same region

**Effects:**
- R-scale (Radio blackouts): R1 (minor) to R5 (extreme)
- M5+ flares typically cause R2 (moderate) radio blackouts
- X-class flares can cause R3-R5 blackouts

## Coronal Mass Ejections (CMEs)

**Analysis Types:**
- Leading Edge (LE): Bulk CME material, slower, sustained effects
- Shock Front (SH): Shock wave ahead of CME, faster, initial disturbance
- SH arrives before LE (hours to day difference)

**Speed Classifications:**
- <400 km/s: Slow, unlikely Earth-directed effect
- 400-800 km/s: Moderate, possible minor effects
- 800-1200 km/s: Fast, likely geomagnetic storm
- >1200 km/s: Very fast, strong storm potential

**Earth Impact:**
- Travel time: Typically 1-3 days from Sun to Earth
- Uncertainty: ±7 hours typical for arrival predictions
- Models: WSA-ENLIL+Cone provides multiple runs

**Geomagnetic Effects:**
- Kp index: 0-9 scale of geomagnetic activity
- G-scale: G1 (minor) to G5 (extreme) geomagnetic storms

**Aurora Visibility by Kp Level:**

| Kp Level | Storm Level | Where Aurora Is Visible |
|----------|-------------|-------------------------|
| Kp 0-2 | Quiet | Auroral zone only: Alaska, northern Canada, Iceland, northern Scandinavia |
| Kp 3 | Unsettled | Northern Canada, northern Scandinavia, occasionally Oslo/Stockholm |
| Kp 4 | Active | Calgary, Edmonton, Oslo, Stockholm, southern Scandinavia |
| Kp 5 | G1 Minor storm | Seattle, Minneapolis, Edinburgh, Scottish Highlands, Hobart (Tasmania) |
| Kp 6 | G2 Moderate storm | Toronto, Chicago, Boston, northern England, Melbourne, New Zealand South Island |
| Kp 7 | G3 Strong storm | New York, London, northern France/Germany, Adelaide, Christchurch (NZ) |
| Kp 8 | G4 Severe storm | Mid-Atlantic US, Paris, Berlin, southern Australia |
| Kp 9 | G5 Extreme storm | Florida, Mediterranean, Sydney, southern US/Europe/Australia |

**IMPORTANT for Reports:** When mentioning predicted Kp values, ALWAYS include specific locations where aurora may be visible based on this table. For example:
- "Kp 6 predicted" → "aurora visible from Toronto, Chicago, Boston, northern England, and possibly Melbourne"
- "Kp 7-8 possible" → "aurora could be visible as far south as New York, London, Paris, and southern Australia"

## Active Regions

**Magnetic Classifications:**
- Alpha: Simple, single polarity
- Beta: Bipolar, simple sunspot group
- Beta-Gamma: Complex, mixed polarities
- Beta-Gamma-Delta: Highly complex, high flare probability
- Delta: Umbrae of opposite polarity within single penumbra

**Numbering:**
- NOAA assigns AR#### numbers
- Regions tracked across solar disk
- Regions can persist multiple solar rotations (~27 days)

**Location:**
- Heliographic coordinates (e.g., N24E45)
- N/S: Latitude (degrees from equator)
- E/W: Longitude (degrees from central meridian)
- E (East): Region rotating into view
- W (West): Region rotating out of view

## Forecasting

**Time Horizons:**
- 24-hour: Immediate activity expected
- 3-day: Near-term forecast with good confidence
- 7-day+: Longer-term, lower confidence

**Data Sources:**
- NOAA SWPC: Official US forecasts and alerts
- UK Met Office: European perspective
- SIDC: International collaboration
- LMSAL: Real-time flare observations
- NASA DONKI: Comprehensive CME analysis

## Common Patterns

*This section will be populated from refinement sessions*

**To be learned from usage:**
- Typical writing preferences
- How to describe complex events
- What level of technical detail to include
- When to explain vs assume knowledge
