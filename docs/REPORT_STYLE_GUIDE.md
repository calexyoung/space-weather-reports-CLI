# Space Weather Report Style Guide

## Overview

The space weather reports are generated using Claude API with a detailed prompt that produces EarthSky.org-style reports with engaging, educational content.

## What Changed to Produce Better Reports

### Before (Basic Reports)
- Simple bullet points
- Technical jargon without links
- Basic template structure
- Minimal context
- Dry, clinical tone

### After (Enhanced Reports)
- Nested bullet points for better organization
- All technical terms linked to educational resources
- Engaging headlines and storytelling
- Rich context about solar cycle, returning regions, forecasts
- Conversational yet authoritative tone

## Key Components in `claude_integration.py`

### Location of Prompt
File: [claude_integration.py:87-196](claude_integration.py#L87-L196)

The `_build_prompt()` method contains the comprehensive prompt that instructs Claude how to write reports.

### Style Guide Elements

1. **Tone Instructions**
   - Conversational but authoritative
   - Use "our sun" not just "the sun"
   - Make readers feel like they're watching together

2. **Educational Approach**
   - Link all technical terms
   - Explain acronyms on first use
   - Provide context for measurements

3. **Specificity Requirements**
   - Use actual region numbers (AR4267, AR4246)
   - Include precise UTC times
   - Cite specific flare classes
   - Mention exact Kp values and wind speeds

4. **Structure Requirements**
   - Nested bullet points for details
   - Bold for region numbers and headers
   - Italics for activity levels (low, moderate, high)

### Required Links

The prompt specifies exact URLs for every technical term:

**Solar Activity Terms:**
- C-class flares → https://en.wikipedia.org/wiki/Solar_flare
- M-class flares → https://en.wikipedia.org/wiki/Solar_flare
- X-class flares → https://earthsky.org/sun/x-flares-most-powerful-solar-flare/
- CMEs → https://earthsky.org/sun/what-are-coronal-mass-ejections/
- Prominences → https://earthsky.org/sun/solar-filaments-prominences-arcs-hot-plasma/
- Plage → https://en.wikipedia.org/wiki/Solar_plage

**Magnetic Classifications:**
- Alpha, Beta, etc. → https://www.spaceweatherlive.com/en/help/the-magnetic-classification-of-sunspots.html

**Measurements:**
- UTC times → https://earthsky.org/astronomy-essentials/universal-time/
- Kp index → https://www.swpc.noaa.gov/products/planetary-k-index
- Solar wind → https://www.swpc.noaa.gov/phenomena/solar-wind
- Magnetic field (Bt) → https://www.swpc.noaa.gov/products/real-time-solar-wind
- Bz component → https://icelandatnight.is/bz-level
- CH HSS → https://www.swpc.noaa.gov/news/coronal-hole-high-speed-streams-ch-hss

All links must include: `target="_blank" rel="noopener"`

## Report Structure

### Header Section
```html
<h3>Sun news [Month Day]: [Engaging headline]</h3>
<h4>(11 UTC [Yesterday] – 11 UTC [Today])</h4>

<strong>Today's top story:</strong> [3-5 engaging sentences setting the scene]
```

### Main Activity Section
```html
<ul>
 <li><strong>Flare activity on the near side:</strong> [Overview]
  <ul>
   <li><strong>Strongest flare:</strong> [Details with time and region]
    <ul>
     <li><strong>Other activity:</strong> [Additional flares]</li>
     <li>[M-class or X-class notes if relevant]</li>
    </ul>
   </li>
  </ul>
 </li>
 <li><strong>Sunspot regions:</strong> [Count and overview]
  <ul>
   <li><strong>AR####:</strong> [Details with magnetic classification]</li>
  </ul>
 </li>
 <li><strong>Blasts from the sun?</strong> [CME activity]</li>
 <li><strong>Solar wind:</strong>
  <ul>
   <li>[Speed ranges with links]</li>
   <li>[Bz behavior and aurora implications]</li>
  </ul>
 </li>
 <li><strong>Earth's magnetic field:</strong> [Conditions with Kp]</li>
</ul>
```

### Forecast Section
```html
<h3>What's ahead? Sun–Earth forecast</h3>
<ul>
 <li><strong>Flare activity forecast:</strong> [Activity level and percentages]</li>
 <li><strong>Geomagnetic activity forecast:</strong>
  <ul>
   <li><strong>[Date]:</strong> [Forecast with reasoning]</li>
   <li><strong>[Date]:</strong> [Forecast with reasoning]</li>
   <li><strong>[Date]:</strong> [Forecast with Kp range]</li>
  </ul>
 </li>
</ul>
```

## Customization Options

### Changing the Style

To modify the report style, edit the prompt in [claude_integration.py:96-196](claude_integration.py#L96-L196).

**Example modifications:**

1. **More technical style:**
   ```python
   1. **Tone**: Technical and precise. Use scientific terminology without simplification.
   ```

2. **Different audience:**
   ```python
   You are writing for professional space weather forecasters who need detailed technical analysis.
   ```

3. **Different date format:**
   ```python
   <h4>(11:00 UTC {yesterday_date} to 11:00 UTC {today_date})</h4>
   ```

### Adding New Links

To add new reference links, update the "Important Linking Rules" section:

```python
- Link [term] to https://example.com/reference
```

### Changing Output Format

The prompt produces HTML by default. To change format preferences:

1. Modify the "# Output Format" section
2. Update HTML structure templates
3. Adjust nesting rules for bullets

## Testing Changes

After modifying the prompt:

```bash
# Generate a test report
python3 space_weather_automation.py

# Check the latest report
ls -lt space_weather_*.html | head -1

# View the report
cat space_weather_2025-11-01_HHMM.html
```

## Common Adjustments

### More Engaging Headlines

Current: Claude generates creative headlines based on data

To make headlines more conservative:
```python
<h3>Sun news {month_day}: [Brief factual headline]</h3>
```

### Longer/Shorter Reports

Adjust the opening paragraph instruction:
```python
[Opening paragraph: 2-3 sentences]  # Shorter
[Opening paragraph: 5-7 sentences]  # Longer
```

### Different Link Domains

If you prefer different educational resources, change the URLs in the linking rules section.

### Forecast Period

Currently forecasts 3 days ahead. To change:

```python
tomorrow = now + timedelta(days=1)
day_after = now + timedelta(days=2)
day_3 = now + timedelta(days=3)
# Add more days as needed
```

## Troubleshooting

### Reports Too Technical
Adjust tone instruction to be more conversational:
```python
1. **Tone**: Very conversational and friendly. Explain everything in simple terms.
```

### Reports Too Casual
Make tone more formal:
```python
1. **Tone**: Professional and formal. Use technical terminology appropriately.
```

### Missing Links
Check that the linking rules section is complete and Claude is following instructions.

### Wrong Format
Ensure the "Output Format" section explicitly states HTML-only output.

## Example Comparison

### Basic Template (Old)
```html
<li><strong>Flare activity:</strong> Low activity with C7.1 at 31/2043 UTC.</li>
```

### Enhanced Report (New)
```html
<li><strong>Flare activity on the near side:</strong> <em>Low</em> activity dominated
 <ul>
  <li><strong>Strongest flare:</strong> C7.1 long-duration event at
      <a href="https://earthsky.org/astronomy-essentials/universal-time/">20:43 UTC</a>
      October 31, from just over the northeast limb
   <ul>
    <li><strong>Other activity:</strong> <strong>AR4271</strong> produced a C2.3/Sf flare</li>
   </ul>
  </li>
 </ul>
</li>
```

## Files Modified

1. **space_weather_automation.py** (lines 116-146)
   - Added Claude API integration
   - Automatic fallback to templates

2. **claude_integration.py** (lines 87-196)
   - Enhanced prompt with style guide
   - Comprehensive linking rules
   - Date formatting
   - Structure templates

3. **No changes needed to:**
   - config.yaml
   - scheduler.py
   - requirements.txt (already had anthropic)

## Best Practices

1. **Always test after changes** - Generate a report and review it
2. **Check logs** - Verify API key is being used: `grep "API key found" space_weather_automation.log`
3. **Keep examples updated** - If you find a great report style, save it as an example
4. **Document customizations** - Note any personal style preferences
5. **Version control** - Keep backups before major prompt changes

## Future Enhancements

Potential improvements to consider:

- Add image generation for sunspot diagrams
- Include historical context (compare to previous days)
- Add aurora forecast section
- Include satellite health implications
- Add space weather alerts/warnings section
- Multi-language support

## Support

If reports aren't matching the desired style:

1. Check the log file for errors
2. Verify API key is active
3. Review the prompt template
4. Generate multiple reports to see consistency
5. Adjust prompt instructions iteratively

---

**Current Status:** ✅ Reports now generate in EarthSky.org style with nested bullets, educational links, and engaging narrative.
