# Narrative Style Update - Hardcoded Prompts

Updated: 2025-11-08

## Summary

Modified the hardcoded prompt in `claude_integration_enhanced.py` to produce engaging, narrative-driven reports that prioritize reader experience over technical data sequence. The style now leads with observable phenomena (aurora) when present, then explains the technical details.

## Example of New Style

**Your Example (What We're Matching):**
> Auroras danced across the skies again last night as Earth remained under the influence of multiple solar eruptions. The geomagnetic field stayed active, producing colorful displays seen as far south as the northern U.S. and Europe. Solar wind speeds remained elevated near 600 km/s, and the magnetic field's southward orientation (Bz) opened the door for more charged particles to pour in, energizing Earth's upper atmosphere. Another round of geomagnetic activity is possible over the next couple of days as additional coronal mass ejections (CMEs) approach, potentially keeping aurora watchers busy into the weekend. Meanwhile, the Sun took a breather — flare production dropped from high and moderate levels earlier this week to low levels, with only C-class flares recorded.

**Old Style (What We Had):**
> Solar activity remained at moderate levels as the Sun produced 23 C-class flares over the past 24 hours, led by a C6.9 flare from AR4274 at 15:42 UTC... [technical details first]

## What Changed

### 1. Top Story Paragraph Structure (Lines 141-193)

**Added decision tree for opening:**

```
When aurora/geomagnetic activity is active (Kp 4+, G1+ storms):
  1. Observable phenomena (aurora, lights, geomagnetic effects)
  2. Cause (CMEs, solar eruptions, solar wind conditions)
  3. Technical details (Bz orientation, Kp values, speeds)
  4. Solar activity status (flare production, regions)
  5. Forward-looking statement (what's coming next)

When only solar activity (no significant geomagnetic effects):
  1. Most significant solar event
  2. Earth impact (actual or potential)
  3. Activity level and context
  4. Supporting details
  5. Forward outlook
```

**Added example opening:**
> "Auroras danced across the skies again last night as Earth remained under the influence of multiple solar eruptions..."

**Added engaging verb lists:**
- Aurora/storms: "danced", "lit up", "appeared", "swept across"
- Solar wind: "poured in", "flooded", "streamed toward"
- Magnetic field: "opened the door", "responded", "stayed active"
- Flares: "erupted", "unleashed" (strong) vs "took a breather", "quieted down" (weak)
- CMEs: "approached", "remained under the influence of", "headed toward"

**Added narrative elements list:**
- "Auroras danced across the skies..." (not "Aurora was observed")
- "...poured in, energizing Earth's upper atmosphere" (not "entered the magnetosphere")
- "The Sun took a breather" (not "Solar activity decreased")
- "...remained under the influence of..." (not "was affected by")
- "...opened the door for..." (not "allowed")
- "...keeping aurora watchers busy into the weekend" (not "aurora may continue")
- "Meanwhile, the Sun..." (transitions between Earth effects and solar activity)

### 2. Editorial Guidelines Update (Lines 204-242)

**Rewrote Guideline #1 (Headline Priority):**

```
OLD:
1. **Headline Priority**: If geomagnetic storms are occurring (G2+), lead with
   the storm story, NOT just the flare

NEW:
1. **Story Priority & Narrative Opening**: Prioritize by READER EXPERIENCE
   and observable phenomena

When aurora/geomagnetic activity is active (Kp 4+, any G-scale storm):
- Lead with AURORA/GEOMAGNETIC story using narrative, engaging language
- Start with observable phenomena: "Auroras danced...", "The night sky lit up..."
- Then explain cause: "...as Earth remained under the influence of solar eruptions"
- Add technical details: solar wind speeds, Bz orientation, Kp values
- Mention solar activity status: "Meanwhile, the Sun [took a breather/erupted]..."
```

**Updated Guideline #6 (Lead Paragraph Structure):**

```
OLD:
6. **Lead Paragraph Structure**: Prioritize by Earth impact

NEW:
6. **Lead Paragraph Structure & Transitions**: Use "Meanwhile" to smoothly
   transition from Earth effects to solar activity

- When leading with aurora/geomagnetic: Use "Meanwhile, the Sun..."
- Example: "Auroras danced... Meanwhile, the Sun took a breather..."
- This creates natural flow: Earth impacts first, then what the Sun is doing
```

### 3. Writing Style Requirements (Lines 512-527)

**Enhanced Guideline #9 (Engaging Language):**

Added aurora/geomagnetic verbs:
```
- **Aurora/geomagnetic:** "danced", "lit up", "appeared", "swept across",
  "poured in", "opened the door", "energized", "remained under the influence"
```

Added quiet period phrases:
```
- **Low/C-class:** "maintained", "showed", "continued", "modest activity",
  "took a breather", "quieted down"
```

**Added new Guideline #10 (Narrative Phrases):**

```
10. **Narrative phrases to use:**
   - "...remained under the influence of..." (not "was affected by")
   - "...opened the door for..." (not "allowed" or "permitted")
   - "...poured in, energizing..." (not "entered and affected")
   - "...keeping aurora watchers busy..." (not "aurora may continue")
   - "Meanwhile, the Sun..." (transition from Earth effects to solar activity)
   - "...took a breather..." (for quiet periods)
   - "Even so, our star remains restless..." (transition showing ongoing potential)
```

## Key Principles

### 1. Reader-First Ordering

**Old Approach:** Data sequence
```
Flares → CMEs → Solar Wind → Geomagnetic Effects → Aurora
(How we collect the data)
```

**New Approach:** Reader experience
```
Aurora → Geomagnetic Effects → Solar Wind/Bz → CME Story → Flare Activity
(What readers can see/experience first)
```

### 2. Narrative Transitions

**Key transition word: "Meanwhile"**

This word smoothly bridges from Earth effects to solar activity:
- "Auroras danced... [Earth details]... Meanwhile, the Sun took a breather..."
- "Earth's field responded... [geomagnetic details]... Meanwhile, AR4274 erupted..."

### 3. Engaging Verbs by Context

**Aurora/Geomagnetic:**
- Active: "danced", "lit up", "swept across", "appeared"
- Causation: "opened the door", "poured in", "energized", "remained under the influence"

**Solar Activity:**
- Strong: "unleashed", "exploded", "erupted", "fired off"
- Moderate: "produced", "generated", "continued"
- Weak: "took a breather", "quieted down", "maintained"

**Forward-Looking:**
- "keeping aurora watchers busy into the weekend"
- "potentially continuing through [timeframe]"
- "Even so, our star remains restless..."

### 4. Observable First, Technical Second

**Pattern:**
```
[Observable phenomenon] + [cause] + [technical details] + [forward look] + [Meanwhile, solar status]

Example:
"Auroras danced across the skies" [observable]
"as Earth remained under the influence of multiple solar eruptions" [cause]
"Solar wind speeds remained elevated near 600 km/s, and the magnetic field's southward orientation (Bz) opened the door" [technical]
"Another round of geomagnetic activity is possible over the next couple of days" [forward]
"Meanwhile, the Sun took a breather — flare production dropped to low levels" [solar status]
```

## When to Use Which Style

### Lead with Aurora/Geomagnetic (Narrative Style)

**Trigger:** Any of these conditions:
- Kp 4+ (Active geomagnetic conditions)
- Any G-scale storm (G1, G2, G3, etc.)
- Aurora visible at mid-latitudes
- Ongoing geomagnetic disturbance

**Opening pattern:**
> "Auroras [danced/lit up/swept across/appeared]... as Earth [remained under the influence of/responded to]... [CME/solar eruptions/solar wind]..."

### Lead with Solar Activity (Standard Style)

**Trigger:** Any of these conditions:
- No significant geomagnetic activity (Kp < 4, no storms)
- Major X-class or strong M-class flare
- Significant solar event with Earth impact potential

**Opening patterns:**
- Strong event: "The Sun EXPLODED with [X-class flare]..."
- Moderate event: "The Sun erupted with [M-class flare]..."
- Quiet period: "The Sun took a breather, with flare production dropping to..."

## Testing the New Style

### Generate a Report

```bash
# Standard generation (uses updated hardcoded prompts)
python3.11 space_weather_automation.py

# With modular prompts (if you want to use YAML version)
USE_MODULAR_PROMPTS=true python3.11 space_weather_automation.py
```

### Look for These Elements

**In reports with geomagnetic activity:**
- [ ] Opens with aurora/geomagnetic story
- [ ] Uses "danced", "poured in", "opened the door" style verbs
- [ ] "Meanwhile, the Sun..." transition appears
- [ ] Observable phenomena first, technical details second
- [ ] Forward-looking statement about continued activity
- [ ] "Even so, our star remains restless..." or similar

**In reports without geomagnetic activity:**
- [ ] Opens with strongest solar event
- [ ] Uses appropriate verbs ("unleashed" for strong, "took a breather" for quiet)
- [ ] Technical details explained with Earth impact context

## Examples by Scenario

### Scenario 1: Active Aurora (Kp 6, G2 Storm)

**Correct Opening:**
> Auroras danced across the skies last night as Earth remained under the influence of a solar eruption from November 7. The geomagnetic field stayed active at G2 (moderate) storm levels, producing colorful displays visible from Seattle, Minneapolis, Edinburgh, and Toronto. Solar wind speeds remained elevated near 650 km/s, and the magnetic field's southward orientation (Bz) opened the door for charged particles to pour in, energizing Earth's upper atmosphere to altitudes visible from mid-latitudes. Another round of geomagnetic activity is possible tomorrow as an additional CME approaches. Meanwhile, the Sun maintained moderate activity levels, producing several M-class flares from AR4274...

**Incorrect Opening:**
> Solar activity remained at moderate levels as the Sun produced an M3.2 flare from AR4274... [aurora mentioned later]

### Scenario 2: Quiet Period (Kp 2, No Storms, C-class Only)

**Correct Opening:**
> The Sun took a breather this period, with flare production dropping from the high activity levels seen earlier this week to modest C-class events. Only 12 C-class flares were recorded over the past 24 hours, led by a C4.8 event from AR4274 at N24E15. Earth's magnetic field remained quiet at Kp 1-2, with no significant geomagnetic activity. Even so, our star remains restless — AR4274 retains its magnetically complex beta-gamma-delta configuration and could produce stronger flares...

**Incorrect Opening:**
> Auroras may be visible tonight... [when Kp is only 2]

### Scenario 3: Major Flare + Geomagnetic Activity

**Correct Opening:**
> Earth's magnetic field responded vigorously to incoming solar material, reaching G3 (strong) geomagnetic storm levels and producing aurora displays visible as far south as New York, London, and northern France. Solar wind speeds surged to 750 km/s as a CME from November 6 swept past Earth, while the magnetic field's southward Bz orientation opened the door for maximum energy transfer. Aurora watchers across mid-latitudes were treated to rare displays. Meanwhile, the Sun exploded with an X2.3 flare from AR4274, the largest event of this solar rotation, triggering an R3 (strong) radio blackout...

## Updating the Style Further

### In Hardcoded Prompt

Edit `claude_integration_enhanced.py` around lines 141-193 (Top Story Paragraph) and 204-242 (Editorial Guidelines).

### In Modular YAML

If using modular prompts, edit:
- `prompt_config/instructions/editorial_guidelines.yaml` (guideline #1)
- `prompt_config/reference_data/activity_language.yaml` (add aurora verbs)

## Benefits of This Style

1. **More Engaging:** Readers connect with observable phenomena
2. **Better Flow:** Natural progression from what they see to why it happened
3. **Still Accurate:** All technical details included, just reordered
4. **Reader-Friendly:** Observable first, technical explanation second
5. **Compelling:** Narrative verbs make reports more interesting to read

## Notes

- This style is now the **default** for hardcoded prompts
- Works best when geomagnetic activity is present (Kp 4+)
- Automatically adapts for quiet periods (leads with solar activity instead)
- All technical accuracy maintained
- "Meanwhile" is the key transition word
