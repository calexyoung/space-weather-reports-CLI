"""
AI Report Generator with Detailed Prompting
Generates professional space weather reports matching the quality standard

Supports multiple AI providers through the model_providers abstraction layer.
"""

import os
import logging
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime, timedelta

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    pass

# Import the model providers system
try:
    from model_providers import get_provider, list_available_models, get_model_info
    from model_providers.base import ProviderError
    MODEL_PROVIDERS_AVAILABLE = True
except ImportError:
    MODEL_PROVIDERS_AVAILABLE = False

# Legacy: Check if Anthropic SDK is available (fallback)
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIReportGenerator:
    """
    Generate professional space weather reports using AI models.

    Supports multiple providers (Anthropic Claude, OpenAI GPT, Google Gemini) through
    a unified interface. Use the model_name parameter to select which
    model to use for report generation.

    Usage:
        # Use default model (from config.yaml)
        generator = AIReportGenerator()

        # Use specific model
        generator = AIReportGenerator(model_name="gpt-4o")

        # Generate report
        reports = generator.generate_report(data)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        use_modular_prompts: bool = False,
        model_name: Optional[str] = None
    ):
        """
        Initialize the report generator

        Args:
            api_key: API key for the provider (uses environment variable if not provided)
            use_modular_prompts: If True, use YAML-based modular prompts instead of hardcoded
            model_name: Name of the model to use (e.g., "claude-sonnet-4.5", "gpt-4o")
                       If None, uses default from config.yaml
        """
        self.use_modular_prompts = use_modular_prompts or os.getenv('USE_MODULAR_PROMPTS', '').lower() == 'true'
        self.model_name = model_name
        self._provider = None
        self._api_key = api_key

        # Try to initialize with model providers system
        if MODEL_PROVIDERS_AVAILABLE:
            try:
                self._provider = get_provider(model_name, api_key=api_key)
                self.enabled = True
                self.model_name = self._provider.model_name
                logger.info(f"Initialized with model provider: {self._provider}")
            except ProviderError as e:
                logger.warning(f"Could not initialize model provider: {e}")
                self._provider = None
                self.enabled = False

        # Fallback to legacy Anthropic-only mode
        if self._provider is None:
            self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if ANTHROPIC_AVAILABLE and self.api_key:
                self.client = Anthropic(api_key=self.api_key)
                self.enabled = True
                self.model_name = "claude-sonnet-4.5"
                logger.info("Initialized with legacy Anthropic client")
            else:
                self.client = None
                self.enabled = False
                logger.warning("No AI provider available - will use fallback templates")

    @property
    def provider_info(self) -> Dict:
        """Get information about the current provider/model"""
        if self._provider:
            return self._provider.get_model_info()
        elif hasattr(self, 'client') and self.client:
            return {
                'name': 'claude-sonnet-4.5',
                'provider': 'anthropic',
                'model_id': 'claude-sonnet-4-5-20250929',
                'description': 'Legacy Anthropic client'
            }
        return {'name': 'fallback', 'provider': 'none', 'description': 'No AI provider'}

    @staticmethod
    def list_available_models() -> Dict:
        """
        List all available models that can be used for report generation

        Returns:
            Dictionary of model name -> model info
        """
        if MODEL_PROVIDERS_AVAILABLE:
            models = list_available_models()
            return {name: config.to_dict() for name, config in models.items()}
        return {
            'claude-sonnet-4.5': {
                'provider': 'anthropic',
                'description': 'Default model (legacy mode)'
            }
        }
    
    def generate_report(self, data: Dict) -> Dict[str, str]:
        """
        Generate comprehensive space weather report using AI

        Args:
            data: Dictionary containing NOAA discussion and other source data

        Returns:
            Dictionary with report formats (html, markdown, json, text)
        """
        if not self.enabled:
            return self._generate_fallback_report(data)

        try:
            # Build comprehensive prompt (modular or hardcoded)
            if self.use_modular_prompts:
                prompt = self._build_modular_prompt(data)
            else:
                prompt = self._build_detailed_prompt(data)

            # Generate using the appropriate method
            if self._provider:
                # Use new model providers system
                html_report = self._generate_with_provider(prompt)
            else:
                # Legacy Anthropic-only path
                html_report = self._generate_with_legacy_client(prompt)

            # Append data tables after main report content
            html_report = self._append_data_tables(html_report, data)

            # Generate other formats
            return {
                'html': html_report,
                'markdown': self._convert_to_markdown(html_report),
                'json': self._convert_to_json(data),
                'text': self._convert_to_text(html_report)
            }

        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            print(f"Error generating report with AI: {e}")
            return self._generate_fallback_report(data)

    def _generate_with_provider(self, prompt: str) -> str:
        """
        Generate report content using the model providers system

        Args:
            prompt: The complete prompt to send to the model

        Returns:
            HTML report content
        """
        logger.info(f"Generating report with {self._provider.model_name}")

        response = self._provider.generate(
            prompt=prompt,
            max_tokens=16000,
            temperature=0.7  # Slightly creative for natural writing
        )

        logger.info(
            f"Report generated: {response.output_tokens} tokens, "
            f"finish_reason={response.finish_reason}"
        )

        return self._extract_html(response.content)

    def _generate_with_legacy_client(self, prompt: str) -> str:
        """
        Generate report content using legacy Anthropic client

        Args:
            prompt: The complete prompt to send to Claude

        Returns:
            HTML report content
        """
        logger.info("Generating report with legacy Anthropic client")

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return self._extract_html(message.content[0].text)
    
    def _build_detailed_prompt(self, data: Dict) -> str:
        """Build detailed prompt with comprehensive instructions and examples"""
        from datetime import timezone

        # Use UTC time for all dates
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)

        prompt = f"""You are an expert space weather forecaster creating a comprehensive daily report.

Generate a professional space weather report for {now.strftime('%B %d, %Y')} (UTC) covering the period from 11 UTC {yesterday.strftime('%B %d')} to 11 UTC {now.strftime('%B %d')}.

# PRIMARY DATA SOURCES

## NOAA SWPC Discussion (Most Authoritative)
{data.get('noaa_discussion', 'Not available')}

## UK Met Office Space Weather Forecast
{data.get('uk_met_office', 'Not available')}

## SIDC (Solar Influences Data analysis Center) Forecast
{data.get('sidc_forecast', 'Not available')}

## 24-Hour Flare Tracking Database
{self._format_flare_summary(data.get('flare_summary'))}

## CME Tracking Database (Enhanced with Analyses & Model Runs)
{self._format_cme_data(data.get('cmes_observed', []))}

## CME Arrival Predictions (Forecast Period)
{self._format_cme_data(data.get('cmes_predicted', []))}

## Alternative Sources (For Context)
{self._format_alternative_sources(data.get('alternative_sources', {}))}

# REPORT STRUCTURE AND REQUIREMENTS

Create an HTML report with this EXACT structure:

## Header Section
```html
<h3>Sun news {now.strftime('%B %d')} (UTC): [Compelling 3-7 word headline summarizing main story]</h3>
<h4>(11 UTC {yesterday.strftime('%B %d')} → 11 UTC {now.strftime('%B %d')})</h4>
```

## Top Story Paragraph

🎯 CRITICAL: Prioritize by READER EXPERIENCE, not data sequence!

**When geomagnetic activity/aurora is occurring (Kp 4+, G1+ storms):**

Lead with aurora/geomagnetic story using NARRATIVE, STORYTELLING language:

Structure:
1. Observable phenomena (aurora, lights in sky, geomagnetic effects)
2. Cause (CMEs, solar eruptions, solar wind conditions)
3. Technical details (Bz orientation, Kp values, speeds)
4. Solar activity status (flare production, regions)
5. Forward-looking statement (what's coming next)

Example opening:
"Auroras danced across the skies again last night as Earth remained under the influence of multiple solar eruptions. The geomagnetic field stayed active, producing colorful displays seen as far south as the northern U.S. and Europe. Solar wind speeds remained elevated near 600 km/s, and the magnetic field's southward orientation (Bz) opened the door for more charged particles to pour in, energizing Earth's upper atmosphere. Another round of geomagnetic activity is possible over the next couple of days as additional coronal mass ejections (CMEs) approach, potentially keeping aurora watchers busy into the weekend. Meanwhile, the Sun took a breather — flare production dropped from high and moderate levels earlier this week to low levels, with only C-class flares recorded."

Engaging verbs to use:
- Aurora/storms: "danced", "lit up", "appeared", "swept across"
- Solar wind: "poured in", "flooded", "streamed toward"
- Magnetic field: "opened the door", "responded", "stayed active"
- Flares: "erupted", "unleashed", "fired off" (for strong), "took a breather", "quieted down" (for weak)
- CMEs: "approached", "remained under the influence of", "headed toward"

**When only solar activity (no significant geomagnetic activity):**

Lead with most significant solar event:
- X-class or strong M-class flare → Lead with the explosive event
- Multiple moderate flares → Lead with activity level and strongest event
- Quiet period → Lead with the calm ("The Sun took a breather...")

Structure:
1. Most significant solar event
2. Earth impact (actual or potential)
3. Activity level and context
4. Supporting details (regions, additional flares)
5. Forward outlook

**Narrative elements - USE THESE:**
- "Auroras danced across the skies..." (not "Aurora was observed")
- "...poured in, energizing Earth's upper atmosphere" (not "entered the magnetosphere")
- "The Sun took a breather" (not "Solar activity decreased")
- "...remained under the influence of..." (not "was affected by")
- "...opened the door for..." (not "allowed")
- "...keeping aurora watchers busy into the weekend" (not "aurora may continue")
- "Meanwhile, the Sun..." (transitions between Earth effects and solar activity)

**Tone:** Engaging science storytelling, not dry technical report
**Voice:** Active, vivid, accessible
**Perspective:** Reader-first (what they can see/experience), then technical details

**Writing Style Requirements:**
- **Accessible technicality**: Use technical terms correctly (e.g., "coronal mass ejection", "interplanetary magnetic field") but explain implications for general readers (e.g., "disrupting high-frequency communications", "enhancing aurora displays")
- **Geographic specificity**: For radio blackouts, mention real, specific places affected (e.g., "disrupting aviation communications across the Atlantic", "affecting maritime radio in the Pacific", "impacting HF communications over South America")
- **Sentence variety**: Mix short impact statements with longer explanatory sentences for rhythm and emphasis
- **Engaging language**: Use vivid verbs and descriptive language proportional to activity level
  - High activity: "unleashed", "exploded", "erupted", "blasted"
  - Moderate activity: "produced", "generated", "released"
  - Low activity: "continued", "maintained", "showed"

**CRITICAL EDITORIAL IMPROVEMENTS - APPLY THESE:**

1. **Story Priority & Narrative Opening**: Prioritize by READER EXPERIENCE and observable phenomena

   **When aurora/geomagnetic activity is active (Kp 4+, any G-scale storm):**
   - Lead with AURORA/GEOMAGNETIC story using narrative, engaging language
   - Start with observable phenomena: "Auroras danced...", "The night sky lit up...", "Colorful displays swept across..."
   - Then explain cause: "...as Earth remained under the influence of solar eruptions"
   - Add technical details: solar wind speeds, Bz orientation, Kp values
   - Mention solar activity status: "Meanwhile, the Sun [took a breather/erupted/maintained activity]..."
   - Good: "Auroras danced across the skies again last night as Earth remained under the influence of multiple solar eruptions..."
   - Avoid: "Solar activity remained at moderate levels as the Sun produced 23 C-class flares..." (when aurora is the bigger story)

   **When only solar activity (no significant geomagnetic effects):**
   - Lead with most significant solar event (X-class flare, strong M-class, or activity level)
   - Use engaging verbs: "unleashed", "erupted", "fired off" (strong) or "took a breather", "quieted down" (weak)
   - Good: "The Sun took a breather this period, with flare production dropping to low levels..."
   - Good: "The Sun EXPLODED with an X2.3 flare from AR4274, triggering widespread radio blackouts..."

2. **Aurora Visibility Specificity**: Use SPECIFIC CITY NAMES from aurora visibility table:
   - Kp 7-9 (G3): "Aurora may be visible as far south as New York, London, Paris, and possibly southern Australia"
   - Kp 5-7 (G2): "Aurora expected across Seattle, Minneapolis, Edinburgh, Toronto, Chicago, and northern England"
   - Kp 4-5 (G1): "Aurora likely from Seattle, Oslo, Reykjavik, Anchorage"
   - NEVER use vague terms like "northern regions" when you have specific city data

3. **CME Arrival Details in Narrative**: When mentioning a CME, include the specific arrival predictions
   - Instead of: "Analysis is ongoing..."
   - Write: "Initial analysis suggests Earth arrival on November 9 around 13:47-18:00 UTC (Shock/Leading Edge), with Kp indices potentially reaching 5-7"

4. **Multi-CME Context**: When multiple CMEs are affecting Earth simultaneously, explain the overlap
   - Example: "Complex geomagnetic conditions result from overlapping influences of two CMEs from November 5 (arriving November 7-8) and a coronal hole high-speed stream"

5. **Radio Blackout Details**: Add duration and affected users
   - Instead of: "briefly disrupted high-frequency communications"
   - Write: "caused a ~30-minute disruption to high-frequency radio communications, primarily affecting aviation and amateur radio operators"

6. **Lead Paragraph Structure & Transitions**: Use "Meanwhile" to smoothly transition from Earth effects to solar activity
   - When leading with aurora/geomagnetic: Use "Meanwhile, the Sun..." to transition to solar activity
   - Example: "Auroras danced... Solar wind speeds remained elevated... Another round of activity is possible... Meanwhile, the Sun took a breather — flare production dropped to low levels..."
   - Example: "Earth's field responded vigorously... Kp indices reached 7... Meanwhile, the Sun erupted with an M7.4 flare..."
   - This creates natural flow: Earth impacts first, then what the Sun is doing

7. **Forecast Specificity**: For days with predicted CME arrivals, include exact times and Kp ranges
   - Example: "November 09: G1-G3 storms possible with M1.8 CME arrival (Shock: 13:47 UTC, Leading Edge: 18:00 UTC). Aurora from Seattle, Minneapolis, Edinburgh, possibly Toronto/Chicago"

8. **Active Region Consistency**: Use AR4274 format consistently (NOT AR14274)
   - Current active region numbering starts with '1' (e.g., AR14274), but the '1' is usually dropped to shorten it (AR14274 → AR4274)
   - Full format: AR14274 (5-digit, with leading 1)
   - Short format: AR4274 (4-digit, leading 1 dropped)
   - ALWAYS use the 4-digit short format in reports (AR4274)
   - Examples: AR14274 → AR4274, AR14283 → AR4283, AR14290 → AR4290

## Detailed Sections (in <ul> tags)

### 1. Flare Activity
```html
<li><strong>Flare activity:</strong> Solar activity [was/remained at/increased to] [low/moderate/high] levels, with [X] flares observed.
  <ul>
    <li><strong>Strongest flare:</strong> [Class and value] from [region or location] at <a href="https://earthsky.org/astronomy-essentials/universal-time/" target="_blank" rel="noopener">[time UTC]</a> on [date]. [If M1+ and caused radio blackout: It triggered an <a href="https://www.swpc.noaa.gov/noaa-scales-explanation" target="_blank" rel="noopener">R1</a> (minor) <a href="https://www.swpc.noaa.gov/phenomena/solar-flares-radio-blackouts" target="_blank" rel="noopener">radio blackout</a> affecting [region].]</li>
    <li>Other notable flares: [List other significant flares with times]</li>
    <li>[Region X] was the top flare producer, responsible for [Y] flares including [types].</li>
  </ul>
</li>
```

CRITICAL FLARE DETAILS:
- Always include exact UTC times with links
- Specify the active region number (AR####) or location (e.g., "northeast limb")
- For M-class or above: mention R-scale radio blackouts and affected Earth regions with **geographic specificity**
  - R3 (Strong): "disrupting high-frequency communications across [ocean/continent] and affecting aviation routes over [region]"
  - R2 (Moderate): "causing temporary radio blackouts for [specific activities] in the [hemisphere/region]"
  - R1 (Minor): "briefly affecting HF communications over the sunlit [specific region]"
- Use proper terminology: C-class (common), M-class (moderate), X-class (strong)
- Include all flares above C5.0, and all M/X flares
- **Use engaging language proportional to flare strength**: X-class gets dramatic language, C-class gets measured language

🔴 MANDATORY FLARE ANALYSIS INSTRUCTIONS 🔴

1. **HEADLINE REQUIREMENTS:**
   - Your headline MUST reference the STRONGEST flare from the 24-hour tracking database
   - The strongest flare is explicitly marked in the flare summary above
   - Title format based on strongest flare:
     * X-class: "The Sun EXPLODES with [X#.#] flare — [major impact description]!"
     * M5.0+: "The Sun erupts with M[#] flare — activity levels surge to high!"
     * M1.0-M4.9: "M[#] flare marks [return of/continuation of] solar activity"
     * C8.0+: "Strong C-class flare as solar activity [continues/increases]"
     * C5.0-C7.9: "Moderate solar activity continues with C-class flares"
   - Use the activity level provided in the flare summary: very high/high/moderate/low
   - Use exciting, engaging language proportional to flare strength

2. **ACTIVITY LEVEL CLASSIFICATION:**
   - Use the EXACT activity level provided in the "ACTIVITY LEVEL" section of flare summary
   - X-class: "very high" activity
   - M5.0+: "high" activity
   - M1.0-M4.9: "moderate to high" activity
   - C5.0+: "moderate" activity
   - C1.0-C4.9: "low to moderate" activity
   - Never contradict the provided activity level

3. **STRONGEST FLARE PROMINENCE:**
   - The "STRONGEST FLARE" section gives you ALL details for your opening paragraph
   - Include: flare class, exact time, region number, location, radio blackout level
   - This should be the FIRST event mentioned in your top story paragraph

4. **RADIO BLACKOUT MAPPING (R-SCALE):**
   - Radio blackouts (R-scale) are determined ONLY by flare class
   - ⚠️ CRITICAL: C-class flares do NOT cause radio blackouts
   - Flare Class → R-Scale Mapping:
     * C1.0 to C9.9: None (No radio blackout)
     * M1.0 to just before M5.0: R1 (Minor radio blackout)
     * M5.0 to just before X1.0: R2 (Moderate radio blackout)
     * X1.0 to just before X10.0: R3 (Strong radio blackout)
     * X10.0 to just before X20.0: R4 (Severe radio blackout)
     * X20.0 and above: R5 (Extreme radio blackout)
   - Examples:
     * C9.2: No radio blackout (C-class flares do not cause blackouts)
     * M3.5: R1 (Minor) radio blackout
     * M7.4: R2 (Moderate) radio blackout
     * X2.3: R3 (Strong) radio blackout
     * X12.5: R4 (Severe) radio blackout
     * X28.0: R5 (Extreme) radio blackout

5. **FLARE PRIORITIZATION:**
   - List ALL M-class and X-class flares individually with times
   - For C-class flares: group by region if there are many from same region
   - Order flares chronologically when listing them
   - Pay special attention to flares from the past 6 hours (most current)
   - The flare list is sorted newest-first - recent flares are at the top

6. **DATA SOURCE ACKNOWLEDGMENT:**
   - Flares marked [LMSAL] have precise timing from LMSAL table
   - Flares marked [NOAA] come from NOAA discussion text
   - LMSAL data includes exact start, peak, and end times
   - You may note "precise timing from LMSAL observations" for accuracy

7. **AVOID THESE MISTAKES:**
   - ❌ Don't use old M1.0 flares as strongest when newer M5.0 exists
   - ❌ Don't call it "moderate" activity when flare summary says "high"
   - ❌ Don't miss recently numbered regions (check NOAA for AR#### assignments)
   - ❌ Don't ignore the strongest flare marker in your headline
   - ❌ Don't describe R2 blackouts as "minor" (R2 = Moderate)

### 2. Sunspot Regions
```html
<li><strong>Sunspot regions:</strong> The Earth-facing solar disk displayed [X] numbered active regions.
  <ul>
    <li><strong>AR####</strong> (<a href="https://en.wikipedia.org/wiki/Solar_coordinate_systems" target="_blank" rel="noopener">[location like N10W29]</a>, <a href="https://www.spaceweatherlive.com/en/help/the-classification-of-sunspots-after-malde.html" target="_blank" rel="noopener">[spot type]</a>, <a href="https://www.spaceweatherlive.com/en/help/the-magnetic-classification-of-sunspots.html" target="_blank" rel="noopener">[magnetic class]</a>) [maintained/gained/lost] its [configuration] and [activity summary].</li>
    <li>[Continue for each significant region]</li>
    <li>The remaining regions [description of other regions].</li>
  </ul>
</li>
```

CRITICAL REGION DETAILS:
- List ALL numbered regions on Earth-facing disk
- Include magnetic classification (alpha, beta, beta-gamma, beta-gamma-delta, etc.)
- Note any regions that rotated off the limb or newly appeared
- Mention regions that decayed to plage
- Highlight any delta configurations (high flare potential)

### 3. CMEs (Coronal Mass Ejections)
```html
<li><strong>Blasts from the sun?</strong> [If CMEs detected: Describe each CME with complete analysis data. If no CMEs: No Earth-directed coronal mass ejections were observed during the period.]
  <ul>
    [For each CME with Earth impact:]
    <li>A [halo/partial halo] <a href="https://earthsky.org/sun/what-are-coronal-mass-ejections/" target="_blank" rel="noopener">coronal mass ejection (CME)</a> erupted at <a href="time-link">[time UTC]</a> on [date] from <a href="coord-link">[source location]</a> (<strong>AR [region]</strong>), associated with the [flare class/magnitude] flare. Analysis shows:
      <ul>
        <li><strong>Leading Edge (LE) analysis ([speed] km/s):</strong> [Number] model run(s) predict Earth arrival [timing details]. [If Kp estimates available: Kp indices forecast to reach [range], indicating <a href="G-scale-link">G[#] ([severity])</a> geomagnetic storm potential.]</li>
        [If Shock Front analysis exists:]
        <li><strong>Shock Front (SH) analysis ([speed] km/s):</strong> [Number] model run(s) predict earlier shock arrival [timing details]. [If Kp estimates available: Kp [range] forecast.]</li>
      </ul>
    </li>
    [Repeat for each CME]
    [For non-Earth-directed CMEs:]
    <li>[Brief mention of far-sided or non-geoeffective CMEs if significant]</li>
  </ul>
</li>
```

CRITICAL CME DETAILS:
- **Show ALL analyses for each CME** - Both Leading Edge (LE) and Shock Front (SH) when available
- **Include ALL model run results** - Show ranges or specify number of runs
- **Kp estimates are crucial** - They tell readers expected geomagnetic activity (Kp 7-9 = G3 storms)
- **Explain LE vs SH difference**:
  - Shock Front (SH) arrives first (faster, earlier), creates initial disturbance
  - Leading Edge (LE) is main CME material (slower, later), produces sustained effects
- **Timing precision**:
  - Multiple runs: show range (e.g., "03:17-03:22 UTC")
  - Single run: show specific time (e.g., "08:55 UTC")
  - Include date and approximate time window
- **Source linking**: Link CME to associated flare when available
- **Geographic terms**: "Halo CME" = full circle (Earth-directed), "Partial halo" = partial circle
- **Type classifications**: Link to R-scale for radio emissions if Type II or Type IV detected
- **Model uncertainty**: Mention "±7 hour uncertainty window" if helpful for context

🚨 MANDATORY CME ARRIVAL REPORTING 🚨

When CME arrival predictions exist in "## CME Arrival Predictions (Forecast Period)" section:
1. **NEVER write "Analysis is ongoing..."** - You have the complete prediction data
2. **ALWAYS include specific arrival times** from the model runs
3. **ALWAYS include Kp estimates** when available (they're in the data!)
4. Format: "Initial WSA-ENLIL+Cone modeling predicts Earth arrival on [date] around [time range] UTC, with Kp indices potentially reaching [range], indicating G[#] geomagnetic storm potential"
5. Example: "Analysis predicts Earth arrival on November 9 around 13:47-18:00 UTC (Shock Front/Leading Edge), with Kp indices reaching 5-7, suggesting G1-G2 storm conditions"

ENHANCED CME DATA STRUCTURE:
Each CME in the data includes:
- activity_id, start_time, source_location, source_region, associated_flare
- analyses[] array with:
  - analysis_type: 'LE' (Leading Edge) or 'SH' (Shock Front)
  - speed, direction_lon, direction_lat, half_angle
  - model_runs[] array with:
    - run_number, earth_arrival_time
    - kp_90, kp_135, kp_180 (Kp estimates at different angles)
    - rmin_earth_radii, impact_duration

ARRIVAL PREDICTION FORMATTING:
- If multiple model runs converge (within 30 minutes): "Three model runs predict arrival between [earliest] and [latest] UTC"
- If runs diverge significantly: "Model runs show arrival window from [earliest] to [latest] UTC"
- Always include Kp range when available: "Kp 7-9" indicates G3 storm potential
- **ALWAYS include specific aurora visibility locations based on predicted Kp:**

AURORA VISIBILITY BY KP LEVEL (USE THIS TABLE):
- Kp 0-2 (Quiet): Auroral zone only - Alaska, northern Canada, Iceland, northern Scandinavia
- Kp 3 (Unsettled): Northern Canada, northern Scandinavia, occasionally Oslo/Stockholm
- Kp 4 (Active): Calgary, Edmonton, Oslo, Stockholm, southern Scandinavia
- Kp 5 (G1 Minor): Seattle, Minneapolis, Edinburgh, Scottish Highlands, Hobart (Tasmania)
- Kp 6 (G2 Moderate): Toronto, Chicago, Boston, northern England, Melbourne, New Zealand South Island
- Kp 7 (G3 Strong): New York, London, northern France/Germany, Adelaide, Christchurch (NZ)
- Kp 8 (G4 Severe): Mid-Atlantic US, Paris, Berlin, southern Australia
- Kp 9 (G5 Extreme): Florida, Mediterranean, Sydney, southern US/Europe/Australia

EXAMPLES:
- "Kp 6-7 forecast" → "aurora may be visible from Toronto, Chicago, Boston, London, and northern France"
- "Kp 8-9 possible" → "aurora could reach as far south as Paris, Berlin, the Mid-Atlantic US, and southern Australia"

### 4. Solar Wind
```html
<li><strong>Solar wind:</strong> Solar wind speeds [increased/decreased/remained steady], averaging [speed] km/s with a peak of [speed] km/s at [time UTC]. The <a href="https://www.spaceweatherlive.com/en/help/the-interplanetary-magnetic-field-imf.html" target="_blank" rel="noopener">interplanetary magnetic field (IMF)</a> [was/remained] [weak/moderate/strong] at [value] nT. The <a href="https://icelandatnight.is/bz-level" target="_blank" rel="noopener">Bz</a> component [fluctuated/remained] [northward/southward], with [description]. A southward Bz favors auroras.</li>
```

CRITICAL SOLAR WIND DETAILS:
- Provide actual speed values (average, peak, current)
- Include IMF strength (Bt value in nT)
- Describe Bz behavior (north/south, range)
- Note any coronal hole high-speed streams (CH HSS)
- Mention if conditions favor aurora visibility

### 5. Earth's Magnetic Field
```html
<li><strong>Earth's magnetic field:</strong> Earth's magnetic field ranged from [quiet/unsettled/active/stormy] levels, reaching Kp = [value]. [If G-scale storms: with G[#] ([minor/moderate/strong]) geomagnetic storm levels for [X] consecutive three-hour periods, including [times].] [Current Kp at report time].</li>
```

CRITICAL GEOMAGNETIC DETAILS:
- Provide Kp range for the period
- Note any G-scale storm levels reached
- Specify duration of storm conditions (number of 3-hour periods)
- Include specific times when storm levels occurred
- State current Kp at report generation time

## Forecast Section

```html
<h3>What's ahead? Sun–Earth forecast</h3>
<ul>
  <li><strong>Flare activity forecast:</strong> [Low/Moderate/High] levels are expected, with a [X]% chance of <a href="https://en.wikipedia.org/wiki/Solar_flare" target="_blank" rel="noopener">M-class</a> (<a href="https://www.swpc.noaa.gov/noaa-scales-explanation" target="_blank" rel="noopener">R1-R2</a>) flares from [regions]. A [slight/moderate] ([Y]%) chance remains for an <a href="https://earthsky.org/sun/x-flares-most-powerful-solar-flare/" target="_blank" rel="noopener">X-class</a> event, mainly from [regions].</li>
  <li><strong>Geomagnetic activity forecast:</strong>
    <ul>
      <li><strong>[Date]:</strong> [Forecast with specific conditions and G-scale probabilities]</li>
      <li><strong>[Date+1]:</strong> [Forecast]</li>
      <li><strong>[Date+2]:</strong> [Forecast]</li>
    </ul>
  </li>
</ul>
```

CRITICAL FORECAST DETAILS:
- **Flare probabilities:** Use specific percentages from NOAA sources (e.g., "65% chance for R1-R2" and "15% for R3")
- **Source regions:** Name specific AR numbers likely to produce activity
- **Region evolution:** Note if regions are rotating toward/away from geoeffective positions
- **Geomagnetic drivers:** Be explicit about causes:
  - "CME arrival expected [date/time]"
  - "Coronal hole high-speed stream (CH HSS) arrival [date]"
  - "Combined CME/HSS effects"
  - "Waning influences from [previous driver]"
  - "Transition to background conditions"
- **Confidence language:** Appropriately use:
  - High confidence: "expected", "likely", "forecast"
  - Moderate confidence: "possible", "chance", "potential"
  - Low confidence: "slight chance", "cannot be ruled out", "uncertain"
- **Day-by-day structure:** Provide at least 3 days forward with specific dates
- **G-scale specificity:** When storms expected:
  - Specify level: G1, G2, G3, etc.
  - Include descriptor: Minor, Moderate, Strong
  - Note probability if less than certain
  - Mention possibility of higher levels if conditions align
- **Timing precision:**
  - "late on [date]" (18:00-23:59 UTC)
  - "early [date]" (00:00-06:00 UTC)
  - "during [date]" (anytime that day)
  - "by the end of [date]" (before 23:59 UTC)
  - Use specific UTC times when modeling provides them

# WRITING STYLE REQUIREMENTS

1. **Tone:** Professional yet accessible, like Nature or Science journalism

2. **Voice:** Active voice primarily, passive only when appropriate

3. **Technical precision:** Use exact values from data sources

4. **Natural flow:** Write as a coherent narrative, not just bullet points

5. **Context:** Provide solar cycle context, seasonal effects, comparisons

6. **Accessible technicality:**
   - Use technical terms correctly (CME, IMF, Bz, plasma, magnetic reconnection)
   - ALWAYS explain implications for general readers immediately after technical terms
   - Example: "The Bz component turned southward to -6 nT, opening Earth's magnetic field and allowing solar wind energy to penetrate deeper, enhancing aurora displays"
   - Example: "A coronal mass ejection (plasma cloud from the Sun) erupted at 500 km/s, fast enough to reach Earth in 3-4 days"

7. **Geographic specificity for impacts:**
   - Radio blackouts: Name specific regions/oceans (Atlantic, Pacific, European sector, North American continent)
   - Aurora visibility: Name latitude bands and specific locations (northern Canada, Scandinavia, Tasmania, New Zealand's South Island)
   - Communication disruptions: Mention specific activities (aviation routes, maritime operations, amateur radio)
   - Example: "The R3 blackout disrupted high-frequency aviation communications across the Atlantic and Pacific air routes"
   - Example: "Aurora may be visible as far south as northern Scotland, southern Alaska, and the northern tier of the contiguous United States"

8. **Sentence variety for rhythm:**
   - Mix short impact statements: "Activity surged." "The Sun exploded." "Earth's field responded."
   - With longer explanatory sentences: "The powerful X1.8 flare erupted from the magnetically complex beta-gamma-delta region AR4274, triggering an R3 radio blackout that disrupted high-frequency communications across the sunlit hemisphere for over an hour."
   - Use this for emphasis and to maintain reader engagement

9. **Engaging language proportional to activity:**
   - **Very high/X-class:** "unleashed", "exploded", "blasted", "erupted violently", "powerful outburst"
   - **High/M5+:** "erupted", "produced", "generated", "fired off", "significant event"
   - **Moderate/M1-M4:** "produced", "generated", "released", "continued activity"
   - **Low/C-class:** "maintained", "showed", "continued", "modest activity", "took a breather", "quieted down"
   - **Aurora/geomagnetic:** "danced", "lit up", "appeared", "swept across", "poured in", "opened the door", "energized", "remained under the influence"
   - Scale your descriptive language to match the data - don't oversell quiet periods or undersell major events

10. **Narrative phrases to use:**
   - "...remained under the influence of..." (not "was affected by")
   - "...opened the door for..." (not "allowed" or "permitted")
   - "...poured in, energizing..." (not "entered and affected")
   - "...keeping aurora watchers busy..." (not "aurora may continue")
   - "Meanwhile, the Sun..." (transition from Earth effects to solar activity)
   - "...took a breather..." (for quiet periods)
   - "Even so, our star remains restless..." (transition showing ongoing potential)

# CRITICAL LINKING REQUIREMENTS

**ALWAYS use these exact link formats, organized by category:**

## Solar Phenomena

- UTC times: `<a href="https://earthsky.org/astronomy-essentials/universal-time/" target="_blank" rel="noopener">[time] UTC</a>`
- Solar flares (general): `<a href="https://en.wikipedia.org/wiki/Solar_flare" target="_blank" rel="noopener">C-class/M-class [flare/flares]</a>`
- Solar flare classification: `<a href="https://earthsky.org/sun/solar-flares-classification-m-x-c-b-a/" target="_blank" rel="noopener">M-class flares</a>` (when discussing the classification system)
- X-class flares: `<a href="https://earthsky.org/sun/x-flares-most-powerful-solar-flare/" target="_blank" rel="noopener">X-class [flare/flares/X#.#]</a>`
- Coronal mass ejections: `<a href="https://earthsky.org/sun/what-are-coronal-mass-ejections/" target="_blank" rel="noopener">coronal mass ejection[s] (CME[s])</a>`
- Coronal dimming: `<a href="https://en.wikipedia.org/wiki/Coronal_mass_ejection#Coronal_signatures" target="_blank" rel="noopener">coronal dimming</a>`
- Solar wind: `<a href="https://www.swpc.noaa.gov/phenomena/solar-wind" target="_blank" rel="noopener">solar wind</a>`
- Coronal holes: `<a href="https://www.swpc.noaa.gov/phenomena/coronal-holes" target="_blank" rel="noopener">coronal hole[s]</a>`

## NOAA Scales and Products

- NOAA R-scale (radio blackouts): `<a href="https://www.swpc.noaa.gov/noaa-scales-explanation" target="_blank" rel="noopener">R1/R2/R3/R4/R5</a>` with descriptor in parentheses
- NOAA G-scale (geomagnetic storms): `<a href="https://www.swpc.noaa.gov/noaa-scales-explanation" target="_blank" rel="noopener">G1/G2/G3/G4/G5</a>` with descriptor in parentheses
- Radio blackouts phenomenon: `<a href="https://www.swpc.noaa.gov/phenomena/solar-flares-radio-blackouts" target="_blank" rel="noopener">radio blackout[s]</a>`
- Geomagnetic storms: `<a href="https://www.swpc.noaa.gov/phenomena/geomagnetic-storms" target="_blank" rel="noopener">geomagnetic storm[s]</a>`
- Kp index: `<a href="https://www.swpc.noaa.gov/products/planetary-k-index" target="_blank" rel="noopener">Kp</a>`
- SUVI instrument: `<a href="https://www.swpc.noaa.gov/products/goes-solar-ultraviolet-imager-suvi" target="_blank" rel="noopener">SUVI</a>`

## Sunspot Classifications

- Solar coordinates: `<a href="https://en.wikipedia.org/wiki/Solar_coordinate_systems" target="_blank" rel="noopener">[location like N24E53]</a>`
- Magnetic classification: `<a href="https://www.spaceweatherlive.com/en/help/the-magnetic-classification-of-sunspots.html" target="_blank" rel="noopener">[alpha/beta/beta-gamma/beta-gamma-delta]</a>`
- McIntosh classification: `<a href="https://www.spaceweatherlive.com/en/help/the-classification-of-sunspots-after-malde.html" target="_blank" rel="noopener">[Axx/Bxo/Cao/Dao/Ekc/etc.]</a>`

## Interplanetary Medium

- Interplanetary Magnetic Field: `<a href="https://www.spaceweatherlive.com/en/help/the-interplanetary-magnetic-field-imf.html" target="_blank" rel="noopener">interplanetary magnetic field (IMF)</a>`
- Bz component: `<a href="https://icelandatnight.is/bz-level" target="_blank" rel="noopener">Bz</a>`

## Spacecraft and Missions

- Solar Dynamics Observatory: `<a href="https://sdo.gsfc.nasa.gov/" target="_blank" rel="noopener">SDO</a>` or `<a href="https://sdo.gsfc.nasa.gov/" target="_blank" rel="noopener">NASA/SDO</a>`
- SOHO mission: `<a href="https://soho.nascom.nasa.gov/" target="_blank" rel="noopener">SOHO</a>` or `<a href="https://soho.nascom.nasa.gov/" target="_blank" rel="noopener">NASA/SOHO</a>`
- GOES satellites: `<a href="https://www.nasa.gov/content/goes" target="_blank" rel="noopener">GOES-[#]</a>`

## Special Resources

- Radio burst data: `<a href="https://www.ncei.noaa.gov/products/space-weather/legacy-data/solar-radio-datasets" target="_blank" rel="noopener">[Type II/Type IV] radio burst</a>`
- Solar cycle tracking: `<a href="https://www.swpc.noaa.gov/products/solar-cycle-progression" target="_blank" rel="noopener">Solar Cycle [#]</a>`

# FORMATTING REQUIREMENTS

## Bold Text (<strong> tags)

IMPORTANT: Always use HTML `<strong>` tags, NEVER use markdown `**` syntax.

Use bold for:
- **Section headers:** "Today's top story:", "Flare activity:", "Sunspot regions:", "Blasts from the sun?", "Solar wind:", "Earth's magnetic field:", "Flare activity forecast:", "Geomagnetic activity forecast:"
- **Subsection headers:** "Strongest flare:", "Lead flare producer:", "Other notable C flares:", dates in forecast (e.g., "November 06:", "November 07:")
- **Active region numbers:** All AR#### mentions (e.g., `<strong>AR4274</strong>`, not `**AR4274**`)
- **First introduction of key concepts** in opening paragraph (e.g., first mention of X-class flare, first mention of storm level)

Examples:
- Correct: `<strong>AR4274</strong> produced an M7.5 flare`
- WRONG: `**AR4274** produced an M7.5 flare`

## Italics (<em> tags)

Use italics for:
- **Activity levels:** <em>very high levels</em>, <em>high levels</em>, <em>moderate to high levels</em>, <em>moderate levels</em>, <em>low to moderate levels</em>
- **Emphasis on unusual conditions:** <em>unprecedented</em>, <em>remarkably stable</em>, <em>exceptionally quiet</em>
- Use sparingly for maximum impact

## Nested Lists

- Primary `<ul>` contains main sections (Flare activity, Sunspot regions, etc.)
- Secondary `<ul>` contains detailed bullet points under each section
- Maintain consistent 2-space indentation for readability
- Ensure proper closing tags: every `<ul>` needs `</ul>`, every `<li>` needs `</li>`

Example structure:
```html
<ul>
  <li><strong>Flare activity:</strong> [Summary text]
    <ul>
      <li><strong>Strongest flare:</strong> [Details]</li>
      <li>Other notable flares: [Details]</li>
    </ul>
  </li>
</ul>
```

# QUALITY CHECKLIST

Before finalizing, verify:

## Data Accuracy:
- [ ] All flare times fall within 11:00 UTC [previous day] to 11:00 UTC [current day]
- [ ] Total flare count matches sum of X + M + C class counts
- [ ] Strongest flare is correctly identified and prominently featured in headline and opening
- [ ] Activity level description matches flare data (very high for X-class, etc.)
- [ ] All active regions on visible disk are listed
- [ ] Solar wind speeds, IMF values, and Kp ranges are precisely quoted from sources
- [ ] Forecast probabilities match NOAA predictions

## Content Completeness:
- [ ] Headline captures most significant event or overall story
- [ ] "Today's top story" paragraph is 5-8 sentences with narrative flow
- [ ] Historical or solar cycle context included where relevant
- [ ] All X-class and M-class flares individually detailed with times and regions
- [ ] Radio blackout impacts include specific geographic locations (not just "Pacific")
- [ ] CME Earth-impact assessments are clear and appropriately cautious
- [ ] Geomagnetic conditions include Kp range and any G-scale storms
- [ ] Forecast provides day-by-day breakdown for at least 3 days
- [ ] Forecast includes specific probabilities and identified source regions

## Technical Quality:
- [ ] All UTC times properly linked
- [ ] All technical terms correctly linked on first mention
- [ ] Magnetic and McIntosh classifications provided for main regions
- [ ] Geographic specificity maximized (specific oceans/regions, not generic)
- [ ] CME directionality clearly stated (miss/hit/glancing)
- [ ] Solar wind regime and trends described
- [ ] Bz orientation and aurora implications explained

## Style and Format:
- [ ] Active voice used throughout except where passive more appropriate
- [ ] Sentence variety creates engaging rhythm (mix short and long sentences)
- [ ] En-dashes (–) used for all ranges, not hyphens
- [ ] "Earth-facing" used consistently (not "Earth-viewed")
- [ ] HTML well-formed with proper nesting and closing tags
- [ ] All links have target="_blank" rel="noopener"
- [ ] Proper indentation (2 spaces per level)
- [ ] Report flows as cohesive narrative, not data dump

## Final Read:
- [ ] Headline is engaging and accurate
- [ ] Opening paragraph tells complete story with context
- [ ] Technical accuracy maintained while remaining accessible
- [ ] No contradictions between sections
- [ ] Appropriate level of caution for uncertain predictions
- [ ] Professional, engaging tone throughout

# OUTPUT REQUIREMENTS

1. Output ONLY the HTML content (from <h3> to final </ul>)
2. Do NOT include explanations, markdown code blocks, or meta-commentary
3. Do NOT add <!DOCTYPE>, <html>, <head>, or <body> tags
4. Use proper HTML entities if needed (e.g., → for arrows)
5. Ensure all links have target="_blank" rel="noopener"

Generate the complete report now, following all requirements above.
"""
        return prompt

    def _build_modular_prompt(self, data: Dict) -> str:
        """
        Build detailed prompt from modular YAML configuration files

        This is the new modular approach that loads prompts from external files.
        Eventually this will replace _build_detailed_prompt().

        To use this method instead of the hardcoded one, set use_modular_prompts=True
        in the config or environment.
        """
        try:
            from prompt_config.prompt_loader import PromptConfigLoader
            loader = PromptConfigLoader()

            # Build prompt sections
            prompt_parts = []

            # Header
            prompt_parts.append("You are a professional space weather forecaster creating a daily report.")
            prompt_parts.append("Use the data provided below to generate an engaging, accurate report.\n")

            # Primary data sources
            prompt_parts.append("# PRIMARY DATA SOURCES\n")
            prompt_parts.append(f"## NOAA SWPC Discussion\n{data.get('noaa_discussion', 'Not available')}\n")
            prompt_parts.append(f"## UK Met Office Space Weather Forecast\n{data.get('uk_met_office', 'Not available')}\n")
            prompt_parts.append(f"## SIDC Forecast\n{data.get('sidc_forecast', 'Not available')}\n")

            # Flare data
            if 'flares_detailed' in data:
                prompt_parts.append(f"## 24-Hour Flare Tracking Database\n{self._format_flare_summary(data.get('flare_summary', {}))}\n")

            # CME data
            if 'cmes_observed' in data:
                prompt_parts.append(f"## CME Tracking Database (Enhanced with Analyses & Model Runs)\n{self._format_cme_data(data.get('cmes_observed', []))}\n")

            if 'cmes_predicted' in data:
                prompt_parts.append(f"## CME Arrival Predictions (Forecast Period)\n{self._format_cme_data(data.get('cmes_predicted', []))}\n")

            # Alternative sources
            if data.get('alternative_sources'):
                prompt_parts.append(f"## Alternative Sources\n{self._format_alternative_sources(data['alternative_sources'])}\n")

            # Report structure requirements
            prompt_parts.append("# REPORT STRUCTURE AND REQUIREMENTS\n")
            prompt_parts.append("## Header Section\n```html\n<h1>Space Weather Report — [Current Date]</h1>\n<p class=\"subtitle\">[Compelling headline]</p>\n```\n")
            prompt_parts.append("**Top Story Paragraph**\nOpen with an engaging summary paragraph that captures the most significant space weather event or trend of the past 24 hours.\n")

            # Editorial guidelines
            prompt_parts.append(loader.build_editorial_guidelines_text())

            # Detailed sections (keeping existing templates for now - can be modularized later)
            prompt_parts.append("## Detailed Sections (in <ul> tags)\n")
            prompt_parts.append("### 1. Flare Activity\n")
            prompt_parts.append(loader.build_flare_analysis_text())

            prompt_parts.append("\n### 3. Coronal Mass Ejections (CMEs)\n")
            prompt_parts.append(loader.build_cme_analysis_text())
            prompt_parts.append("\n" + loader.build_aurora_visibility_text())

            # Writing style
            prompt_parts.append("\n# WRITING STYLE REQUIREMENTS\n")
            prompt_parts.append("1. **Tone:** Professional yet accessible\n")
            prompt_parts.append("2. **Voice:** Active voice primarily\n")
            prompt_parts.append("3. **Technical precision:** Use exact values\n")
            prompt_parts.append("4. **Natural flow:** Coherent narrative\n")
            prompt_parts.append("5. **Context:** Solar cycle context when relevant\n")
            prompt_parts.append("6. **Accessible technicality:** Explain technical terms\n")
            prompt_parts.append("7. **Geographic specificity:** Name actual locations\n")
            prompt_parts.append("8. **Sentence variety:** Mix short and long sentences\n")
            prompt_parts.append(loader.build_activity_language_text())

            # Reference links
            prompt_parts.append("\n" + loader.build_reference_links_text())

            # Formatting requirements
            prompt_parts.append("\n# FORMATTING REQUIREMENTS\n")
            prompt_parts.append("## Bold Text (<strong> tags)\n")
            prompt_parts.append("- Section labels: \"Solar activity:\", \"Sunspot regions:\", etc.\n")
            prompt_parts.append("- Key metrics: \"X2.3\", \"Kp 7\", \"G3 (Strong)\"\n")
            prompt_parts.append("## Links (see CRITICAL LINKING REQUIREMENTS above)\n")
            prompt_parts.append("## Lists\n- Use <ul> and <li> tags\n- One event per list item\n- Include times in UTC\n")

            # Output requirements
            prompt_parts.append("\n# OUTPUT REQUIREMENTS\n")
            prompt_parts.append("Generate ONLY the complete HTML report.\n")
            prompt_parts.append("Do NOT include explanations, commentary, or meta-text.\n")
            prompt_parts.append("Start directly with <h1>Space Weather Report...\n")
            prompt_parts.append("\nGenerate the complete report now, following all requirements above.")

            return "\n\n".join(prompt_parts)

        except Exception as e:
            # If modular loading fails, fall back to original method
            print(f"Warning: Modular prompt loading failed ({e}), using hardcoded prompt")
            return self._build_detailed_prompt(data)

    def _format_flare_summary(self, flare_summary: Dict) -> str:
        """Format flare summary from 24-hour tracking database with activity level guidance"""
        import re

        if not flare_summary or flare_summary.get('total_count', 0) == 0:
            return "No flare data available from tracking database"

        output = []

        # Determine activity level based on strongest flare
        strongest = flare_summary.get('strongest_flare')
        activity_level = "low"
        radio_blackout = None

        if strongest:
            flare_class = strongest['flare_class']
            if flare_class.startswith('X'):
                activity_level = "very high"
                radio_blackout = "R3 (Strong)"
            elif flare_class.startswith('M'):
                # Extract magnitude
                try:
                    flare_mag = float(re.sub(r'[^0-9.]', '', flare_class[1:]))
                    if flare_mag >= 5.0:
                        activity_level = "high"
                        radio_blackout = "R2 (Moderate)"
                    else:
                        activity_level = "moderate to high"
                        radio_blackout = "R1 (Minor)"
                except:
                    activity_level = "moderate to high"
                    radio_blackout = "R1 (Minor)"
            elif flare_class.startswith('C'):
                try:
                    flare_mag = float(re.sub(r'[^0-9.]', '', flare_class[1:]))
                    if flare_mag >= 5.0:
                        activity_level = "moderate"
                    else:
                        activity_level = "low to moderate"
                except:
                    activity_level = "low to moderate"

        # Add prominent activity level indicator
        output.append(f"**🔴 ACTIVITY LEVEL: {activity_level.upper()} 🔴**")
        output.append("")
        output.append(f"**Rolling 24-Hour Flare Database Summary:**")
        output.append(f"- Total flares tracked: {flare_summary['total_count']}")
        output.append(f"- X-class: {flare_summary['x_class_count']}")
        output.append(f"- M-class: {flare_summary['m_class_count']}")
        output.append(f"- C-class: {flare_summary['c_class_count']}")

        # Enhanced strongest flare section
        if strongest:
            output.append(f"\n**⚡ STRONGEST FLARE (USE THIS FOR YOUR HEADLINE) ⚡**")

            time_str = f"{strongest['event_date']} {strongest.get('event_time', '')}"
            region_str = f"AR{strongest.get('region', '????')}"
            location_str = strongest.get('location', 'unknown location')

            output.append(f"- Flare class: **{strongest['flare_class']}**")
            output.append(f"- Time: {time_str} UTC")
            output.append(f"- Region: {region_str}")
            output.append(f"- Location: {location_str}")

            if radio_blackout:
                output.append(f"- Radio blackout: **{radio_blackout}**")

            # Add source information
            source = strongest.get('raw_text', '')
            if 'LMSAL' in source:
                output.append(f"- Data source: LMSAL (precise timing)")
            elif 'NOAA' in source:
                output.append(f"- Data source: NOAA discussion")

        # Sort flares by timestamp (newest first)
        flares_list = sorted(
            flare_summary.get('flares_list', []),
            key=lambda f: f.get('event_timestamp', 0),
            reverse=True
        )

        output.append("\n**Complete Flare List (Last 24 Hours, newest first):**")
        for idx, flare in enumerate(flares_list[:20], 1):
            time_str = f"{flare['event_date']} {flare['event_time']}" if flare.get('event_time') else flare['event_date']
            region_str = f"AR{flare['region']}" if flare.get('region') else "Unknown"

            # Mark M-class and X-class flares prominently
            marker = ""
            if flare['flare_class'].startswith('X'):
                marker = " 🔴"
            elif flare['flare_class'].startswith('M'):
                marker = " 🟠"

            # Add source label
            source = flare.get('raw_text', '')
            source_label = "[LMSAL]" if "LMSAL" in source else "[NOAA]"

            output.append(f"{idx}. {flare['flare_class']}{marker} at {time_str} UTC from {region_str} {source_label}")

        return "\n".join(output)

    def _format_alternative_sources(self, sources: Dict) -> str:
        """Format alternative sources for the prompt"""
        if not sources:
            return "No alternative sources available"

        formatted = []
        for name, content in sources.items():
            if content:
                # Truncate long content
                truncated = content[:1000] + "..." if len(content) > 1000 else content
                formatted.append(f"### {name}\n{truncated}\n")

        return "\n".join(formatted) if formatted else "No alternative sources available"

    def _format_cme_data(self, cmes: list) -> str:
        """Format CME data from enhanced tracker with all analyses and model runs"""
        if not cmes or len(cmes) == 0:
            return "No CME data available"

        output = []
        output.append("**Enhanced CME Database (with Multiple Analyses & Model Runs):**")
        output.append(f"- Total CMEs tracked: {len(cmes)}")

        earth_impact_count = sum(1 for cme in cmes if any(
            any(mr.get('earth_arrival_timestamp') for mr in analysis.get('model_runs', []))
            for analysis in cme.get('analyses', [])
        ))
        output.append(f"- CMEs with Earth impact predictions: {earth_impact_count}")
        output.append("")

        for idx, cme in enumerate(cmes, 1):
            output.append(f"**CME #{idx}: {cme['activity_id']}**")
            output.append(f"- Start time: {cme['start_time']}")
            output.append(f"- Source: {cme.get('source_location', 'Unknown')} (Region {cme.get('source_region', 'Unknown')})")

            if cme.get('associated_flare'):
                output.append(f"- Associated flare: {cme['associated_flare']}")

            analyses = cme.get('analyses', [])
            if analyses:
                output.append(f"- Analyses: {len(analyses)} ({'LE' if any(a['analysis_type'] == 'LE' for a in analyses) else ''}{'+SH' if any(a['analysis_type'] == 'SH' for a in analyses) else ''})")

                for analysis in analyses:
                    atype = analysis['analysis_type']
                    speed = analysis.get('speed', 'Unknown')
                    output.append(f"  - **{atype} Analysis:** {speed} km/s")

                    model_runs = analysis.get('model_runs', [])
                    if model_runs:
                        earth_arrivals = [mr for mr in model_runs if mr.get('earth_arrival_time')]
                        if earth_arrivals:
                            output.append(f"    - Model runs with Earth impact: {len(earth_arrivals)}")
                            for mr in earth_arrivals:
                                output.append(f"      - Run {mr.get('run_number')}: Arrival {mr.get('earth_arrival_time')}")
                                if mr.get('kp_90'):
                                    output.append(f"        Kp estimates: 90°={mr.get('kp_90')}, 135°={mr.get('kp_135')}, 180°={mr.get('kp_180')}")
                                if mr.get('rmin_earth_radii'):
                                    output.append(f"        Rmin: {mr.get('rmin_earth_radii')} Earth radii")
                        else:
                            output.append(f"    - Model runs: {len(model_runs)} (no Earth impacts predicted)")

            output.append("")  # Blank line between CMEs

        output.append("**IMPORTANT CME REPORTING INSTRUCTIONS:**")
        output.append("- Show BOTH LE and SH analyses when both are present")
        output.append("- Include ALL model run results for each analysis")
        output.append("- Kp estimates indicate geomagnetic storm severity:")
        output.append("  - Kp 4-5: Minor activity")
        output.append("  - Kp 6-7: G1-G2 storms (moderate)")
        output.append("  - Kp 8-9: G3-G4 storms (strong/severe)")
        output.append("- Explain that SH (shock) arrives before LE (main material)")
        output.append("- For multiple runs close together, show range (e.g., '03:17-03:22 UTC')")

        return "\n".join(output)

    def _extract_html(self, content: str) -> str:
        """Extract HTML from AI model's response"""
        # Remove markdown code blocks if present
        if '```html' in content:
            content = content.split('```html')[1].split('```')[0]
        elif '```' in content:
            content = content.split('```')[1].split('```')[0]
        
        return content.strip()
    
    def _convert_to_markdown(self, html: str) -> str:
        """Convert HTML report to Markdown"""
        import re
        
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
        
        # Clean up extra whitespace
        md = re.sub(r'\n\s*\n', '\n\n', md)
        
        return md.strip()
    
    def _convert_to_json(self, data: Dict) -> str:
        """Convert data to JSON format"""
        import json
        from datetime import timezone
        output = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sources': {
                'noaa_discussion': bool(data.get('noaa_discussion')),
                'uk_met_office': bool(data.get('uk_met_office')),
                'sidc_forecast': bool(data.get('sidc_forecast')),
                'alternative_sources': list(data.get('alternative_sources', {}).keys())
            },
            'raw_data': data
        }
        return json.dumps(output, indent=2)
    
    def _convert_to_text(self, html: str) -> str:
        """Convert HTML to plain text"""
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        
        # Decode HTML entities
        text = text.replace('→', '->')
        text = text.replace('&nbsp;', ' ')
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'  +', ' ', text)
        
        return text.strip()
    
    def _append_data_tables(self, html_report: str, data: Dict) -> str:
        """
        Append flare and CME data tables to the main report

        Args:
            html_report: Main HTML report content from Claude
            data: Data dictionary containing flares and CMEs

        Returns:
            Complete HTML report with data tables appended
        """
        # Add separator before data tables
        tables_html = """

<hr style="margin: 30px 0; border: none; border-top: 2px solid #bdc3c7;">

<h2 style="color: #2c3e50; margin-top: 30px;">Detailed Activity Data</h2>
"""

        # Add flares table
        flares = data.get('flares_detailed', [])
        if flares:
            tables_html += "\n" + self.generate_flares_html_table(flares)

        # Add observed CMEs table
        cmes = data.get('cmes_observed', [])
        if cmes:
            tables_html += "\n" + self.generate_cmes_observed_html_table(cmes)

        # Add predicted CME arrivals table
        arrivals = data.get('cmes_predicted', [])
        if arrivals:
            tables_html += "\n" + self.generate_cme_arrivals_html_table(arrivals)

        # If no data at all, add a note
        if not flares and not cmes and not arrivals:
            tables_html += """
<div style="padding: 20px; background-color: #ecf0f1; border-radius: 5px; text-align: center;">
<p style="margin: 0; color: #7f8c8d;"><em>No detailed flare or CME data available for this period.</em></p>
</div>
"""

        return html_report + tables_html

    def _generate_fallback_report(self, data: Dict) -> Dict[str, str]:
        """Generate basic template when AI API is not available"""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)

        html = f"""<h3>Space Weather Report - {now.strftime('%B %d, %Y')} (UTC)</h3>
<h4>(11 UTC {yesterday.strftime('%B %d')} → 11 UTC {now.strftime('%B %d')})</h4>

<p><em>Note: Full report generation requires AI API integration.</em></p>

<h4>Data Status:</h4>
<ul>
  <li>NOAA SWPC Discussion: {'✓ Available' if data.get('noaa_discussion') else '✗ Not available'}</li>
  <li>UK Met Office: {'✓ Available' if data.get('uk_met_office') else '✗ Not available'}</li>
  <li>Alternative Sources: {len(data.get('alternative_sources', {}))} sources checked</li>
</ul>

<h4>To enable full reports:</h4>
<ol>
  <li>Get an API key from your AI provider (Anthropic, OpenAI, or Google)</li>
  <li>Add to .env file: ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY</li>
  <li>Install: pip3 install anthropic openai google-generativeai python-dotenv</li>
  <li>Re-run: python3 space_weather_automation.py</li>
</ol>
"""

        # Append data tables even in fallback mode
        html = self._append_data_tables(html, data)

        return {
            'html': html,
            'markdown': self._convert_to_markdown(html),
            'json': self._convert_to_json(data),
            'text': self._convert_to_text(html)
        }

    @staticmethod
    def generate_flares_html_table(flares: list) -> str:
        """
        Generate HTML table of flares observed during analysis period

        Args:
            flares: List of flare dictionaries from database

        Returns:
            HTML table string
        """
        if not flares or len(flares) == 0:
            return """<div style="padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
<p><em>No flare data available for this period.</em></p>
</div>"""

        html = """
<h3>Solar Flares - Analysis Period</h3>
<table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
  <thead>
    <tr style="background-color: #3498db; color: white;">
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">#</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Class</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Date</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Start Time (UTC)</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Peak Time (UTC)</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">End Time (UTC)</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Region</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Location</th>
    </tr>
  </thead>
  <tbody>
"""

        for idx, flare in enumerate(flares, start=1):
            flare_class = flare.get('flare_class', 'Unknown')
            event_date = flare.get('event_date', '')
            start_time = flare.get('event_time', '')
            peak_time = flare.get('peak_time', '')
            end_time = flare.get('end_time', '')
            region = f"AR{flare['region']}" if flare.get('region') else 'Unknown'
            location = flare.get('location', '')

            # Color code by flare class
            if flare_class.startswith('X'):
                row_color = '#ffcccc'  # Light red
            elif flare_class.startswith('M'):
                row_color = '#ffe6cc'  # Light orange
            else:
                row_color = '#ffffff'  # White

            html += f"""    <tr style="background-color: {row_color};">
      <td style="padding: 8px; border: 1px solid #ddd;">{idx}</td>
      <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">{flare_class}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{event_date}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{start_time}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{peak_time}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{end_time}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{region}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{location}</td>
    </tr>
"""

        html += """  </tbody>
</table>
"""

        # Add summary
        x_count = sum(1 for f in flares if f.get('flare_class', '').startswith('X'))
        m_count = sum(1 for f in flares if f.get('flare_class', '').startswith('M'))
        c_count = sum(1 for f in flares if f.get('flare_class', '').startswith('C'))

        html += f"""<p style="margin-top: 10px; font-size: 0.9em; color: #555;">
<strong>Summary:</strong> {len(flares)} total flares |
X-class: {x_count} | M-class: {m_count} | C-class: {c_count}
</p>
"""

        return html

    @staticmethod
    def generate_cmes_observed_html_table(cmes: list) -> str:
        """
        Generate HTML table of CMEs observed during analysis period
        Updated for enhanced CME tracker with multiple analyses per CME

        Args:
            cmes: List of CME dictionaries from enhanced tracker

        Returns:
            HTML table string
        """
        if not cmes or len(cmes) == 0:
            return """<div style="padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
<p><em>No CME data available for this period.</em></p>
</div>"""

        html = """
<h3>Coronal Mass Ejections (CMEs) - Analysis Period</h3>
<table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
  <thead>
    <tr style="background-color: #e74c3c; color: white;">
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">#</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Start Time (UTC)</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Type</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Speed</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Direction</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Earth Impact</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Associated Flare</th>
      <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">NASA Alert</th>
    </tr>
  </thead>
  <tbody>
"""

        earth_impact_count = 0

        for idx, cme in enumerate(cmes, start=1):
            start_time = cme.get('start_time', '')
            associated_flare = cme.get('associated_flare', '')
            donki_url = cme.get('donki_url', '')

            # Get analyses (LE and/or SH)
            analyses = cme.get('analyses', [])

            # Check if CME has Earth impacts across all analyses
            has_earth_impact = any(
                any(mr.get('earth_arrival_timestamp') for mr in analysis.get('model_runs', []))
                for analysis in analyses
            )

            if has_earth_impact:
                earth_impact_count += 1

            # Get primary analysis (prefer LE, fall back to SH)
            primary_analysis = None
            for analysis in analyses:
                if analysis.get('analysis_type') == 'LE':
                    primary_analysis = analysis
                    break
            if not primary_analysis and analyses:
                primary_analysis = analyses[0]

            # Extract fields from primary analysis
            if primary_analysis:
                cme_type = primary_analysis.get('type', '?')
                speed = primary_analysis.get('speed')
                direction_lon = primary_analysis.get('direction_lon')
                direction_lat = primary_analysis.get('direction_lat')
            else:
                cme_type = '?'
                speed = None
                direction_lon = None
                direction_lat = None

            # Format direction
            if direction_lon is not None and direction_lat is not None:
                direction = f"{int(direction_lon)}° / {int(direction_lat)}°"
            else:
                direction = "—"

            # Format speed (show LE/SH if both available)
            if len(analyses) > 1:
                speeds = []
                for analysis in analyses:
                    if analysis.get('speed'):
                        speeds.append(f"{analysis['analysis_type']}: {int(analysis['speed'])}")
                speed_str = " / ".join(speeds) + " km/s" if speeds else "—"
            elif speed:
                speed_str = f"{int(speed)} km/s"
            else:
                speed_str = "—"

            # Earth impact indicator
            earth_impact = "✓ Yes" if has_earth_impact else "No"
            impact_color = "#ffcccc" if has_earth_impact else "#ffffff"

            # Associated flare or blank
            flare_str = associated_flare if associated_flare else "—"

            # NASA DONKI link
            alert_link = f'<a href="{donki_url}" target="_blank" rel="noopener">View</a>' if donki_url else "—"

            html += f"""    <tr style="background-color: {impact_color};">
      <td style="padding: 8px; border: 1px solid #ddd;">{idx}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{start_time}</td>
      <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">{cme_type}-type</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{speed_str}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{direction}</td>
      <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">{earth_impact}</td>
      <td style="padding: 8px; border: 1px solid #ddd; font-size: 0.85em;">{flare_str}</td>
      <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{alert_link}</td>
    </tr>
"""

        html += """  </tbody>
</table>
"""

        # Add summary
        html += f"""<p style="margin-top: 10px; font-size: 0.9em; color: #555;">
<strong>Summary:</strong> {len(cmes)} CME(s) observed |
Earth-directed: {earth_impact_count} | Multi-CME notifications: 0
</p>
"""

        return html

    @staticmethod
    def _extract_flare_details_from_note(note: str) -> str:
        """
        Extract flare class and region from CME note field.

        Example notes:
        - "...M7.4 class flare from AR 14274 (N24E47)..."
        - "...M1.7 flare from Active Region 14274 (N27E27)..."
        - "...M8.6 flare and subsequent eruption from Active Region 14274 (N30E41)..."

        Returns: "M7.4 from AR14274 (N24E47)"
        """
        import re

        if not note:
            return ""

        # Pattern 1: "flare from Active Region XXXXX (location)"
        # Example: "M1.7 flare from Active Region 14274 (N27E27)"
        pattern1 = r'([CBMX]\d+\.\d+)\s+(?:class\s+)?flare\s+(?:and\s+subsequent\s+eruption\s+)?from\s+Active\s+Region\s+(\d+)\s*\(([NS]\d+[EW]\d+)\)'
        match1 = re.search(pattern1, note, re.IGNORECASE)

        if match1:
            flare_class = match1.group(1)
            region = match1.group(2)
            location = match1.group(3)
            return f"{flare_class} from AR{region} ({location})"

        # Pattern 2: "flare from AR XXXXX (location)" (abbreviated form)
        # Example: "M7.4 class flare from AR 14274 (N24E47)"
        pattern2 = r'([CBMX]\d+\.\d+)\s+(?:class\s+)?flare\s+from\s+AR\s*(\d+)\s*\(([NS]\d+[EW]\d+)\)'
        match2 = re.search(pattern2, note)

        if match2:
            flare_class = match2.group(1)
            region = match2.group(2)
            location = match2.group(3)
            return f"{flare_class} from AR{region} ({location})"

        # Pattern 3: "flare from Active Region XXXXX" (no location)
        pattern3 = r'([CBMX]\d+\.\d+)\s+(?:class\s+)?flare\s+(?:and\s+subsequent\s+eruption\s+)?from\s+Active\s+Region\s+(\d+)'
        match3 = re.search(pattern3, note, re.IGNORECASE)

        if match3:
            flare_class = match3.group(1)
            region = match3.group(2)
            return f"{flare_class} from AR{region}"

        # Pattern 4: "flare from AR XXXXX" (no location, abbreviated)
        pattern4 = r'([CBMX]\d+\.\d+)\s+(?:class\s+)?flare\s+from\s+AR\s*(\d+)'
        match4 = re.search(pattern4, note)

        if match4:
            flare_class = match4.group(1)
            region = match4.group(2)
            return f"{flare_class} from AR{region}"

        return ""

    @staticmethod
    def generate_cme_arrivals_html_table(arrivals: list) -> str:
        """
        Generate HTML table of predicted CME arrivals grouped by CME event
        Updated to show CME-level organization with associated flares

        Each CME may have multiple analyses (LE=Leading Edge, SH=Shock), and each
        analysis may have multiple model runs predicting arrivals at different targets.

        Args:
            arrivals: List of CME dictionaries from enhanced tracker with arrival predictions

        Returns:
            HTML string with organized CME arrival predictions
        """
        if not arrivals or len(arrivals) == 0:
            return """<div style="padding: 10px; background-color: #e8f5e9; border-radius: 5px;">
<p><em>No CME arrivals predicted for the forecast period.</em></p>
</div>"""

        html = """
<h3>Predicted CME Arrivals - Forecast Period</h3>
<p style="font-size: 0.9em; color: #555; margin-bottom: 15px;">
Each CME may have multiple analysis types (LE=Leading Edge, SH=Shock) with multiple model runs per target.
</p>
"""

        cme_num = 0
        total_earth_arrivals = 0
        total_spacecraft_arrivals = 0

        for cme in arrivals:
            cme_num += 1
            start_time = cme.get('start_time', '')
            activity_id = cme.get('activity_id', '')
            donki_url = cme.get('donki_url', '')
            associated_flare = cme.get('associated_flare', '')

            # Count arrivals for this CME
            analyses = cme.get('analyses', [])
            cme_earth_count = 0
            cme_spacecraft_count = 0

            for analysis in analyses:
                model_runs = analysis.get('model_runs', [])
                for mr in model_runs:
                    if mr.get('earth_arrival_timestamp'):
                        cme_earth_count += 1
                    spacecraft_impacts = mr.get('spacecraft_impacts', [])
                    for impact in spacecraft_impacts:
                        if impact.get('spacecraft_name', '').lower() != 'earth':
                            cme_spacecraft_count += 1

            total_earth_arrivals += cme_earth_count
            total_spacecraft_arrivals += cme_spacecraft_count

            # CME header section
            html += f"""
<div style="margin-bottom: 20px; border: 2px solid #2c3e50; border-radius: 8px; overflow: hidden;">
  <div style="background-color: #34495e; color: white; padding: 12px;">
    <h4 style="margin: 0; font-size: 1.1em;">CME #{cme_num}: {activity_id}</h4>
    <p style="margin: 5px 0 0 0; font-size: 0.9em;">
      Start: {start_time}"""

            if associated_flare:
                # Extract flare details from note
                note = cme.get('note', '')
                flare_details = AIReportGenerator._extract_flare_details_from_note(note)

                if flare_details:
                    html += f""" | <strong>Associated Flare: {associated_flare} ({flare_details})</strong>"""
                else:
                    html += f""" | <strong>Associated Flare: {associated_flare}</strong>"""

            html += f"""
      | <a href="{donki_url}" target="_blank" rel="noopener" style="color: #3498db;">NASA DONKI Alert</a>
    </p>
  </div>
"""

            # Analysis sections
            for analysis_idx, analysis in enumerate(analyses):
                analysis_type = analysis.get('analysis_type', 'LE')
                speed = analysis.get('speed')
                speed_str = f"{int(speed)} km/s" if speed else "Unknown"

                model_runs = analysis.get('model_runs', [])

                # Count Earth and spacecraft arrivals for this analysis
                earth_runs = [mr for mr in model_runs if mr.get('earth_arrival_timestamp')]
                spacecraft_runs = []
                for mr in model_runs:
                    for impact in mr.get('spacecraft_impacts', []):
                        if impact.get('spacecraft_name', '').lower() != 'earth':
                            spacecraft_runs.append((mr, impact))

                total_predictions = len(earth_runs) + len(spacecraft_runs)

                if total_predictions == 0:
                    continue  # Skip analyses with no predictions

                # Analysis header
                bg_color = "#3498db" if analysis_type == "LE" else "#e67e22"
                html += f"""
  <div style="background-color: {bg_color}; color: white; padding: 8px 12px; font-weight: bold;">
    {analysis_type} Analysis: {speed_str} | {total_predictions} arrival prediction(s)
  </div>
  <table style="width: 100%; border-collapse: collapse;">
    <thead>
      <tr style="background-color: #ecf0f1;">
        <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Run #</th>
        <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Target</th>
        <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Predicted Arrival</th>
        <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Kp Est.</th>
        <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Details</th>
      </tr>
    </thead>
    <tbody>
"""

                # Earth arrivals
                for mr in earth_runs:
                    run_num = mr.get('run_number', '—')
                    arrival_time = mr.get('earth_arrival_time', '—')

                    # Kp estimates
                    kp_90 = mr.get('kp_90')
                    kp_135 = mr.get('kp_135')
                    kp_180 = mr.get('kp_180')

                    if kp_90 and kp_180:
                        kp_str = f"{kp_90}-{kp_180}"
                    elif kp_90:
                        kp_str = str(kp_90)
                    else:
                        kp_str = "—"

                    # Additional details
                    details = []
                    if kp_90 and kp_135 and kp_180:
                        details.append(f"Kp 90°={kp_90}, 135°={kp_135}, 180°={kp_180}")
                    rmin = mr.get('rmin_earth_radii')
                    if rmin:
                        details.append(f"Rmin={rmin} RE")
                    details_str = " | ".join(details) if details else "—"

                    html += f"""      <tr style="background-color: #ffe6e6;">
        <td style="padding: 8px; border: 1px solid #bdc3c7;">{run_num}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7; font-weight: bold;">Earth</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7; font-weight: bold;">{arrival_time}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7;">{kp_str}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7; font-size: 0.85em;">{details_str}</td>
      </tr>
"""

                # Spacecraft arrivals
                for mr, impact in spacecraft_runs:
                    run_num = mr.get('run_number', '—')
                    spacecraft_name = impact.get('spacecraft_name', 'Unknown')
                    arrival_time = impact.get('arrival_time', '—')

                    html += f"""      <tr style="background-color: #fff9e6;">
        <td style="padding: 8px; border: 1px solid #bdc3c7;">{run_num}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7; font-weight: bold;">{spacecraft_name}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7;">{arrival_time}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7;">—</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7;">—</td>
      </tr>
"""

                html += """    </tbody>
  </table>
"""

            html += "</div>\n"  # Close CME container

        # Overall summary
        html += f"""
<p style="margin-top: 15px; padding: 10px; background-color: #ecf0f1; border-radius: 5px; font-size: 0.9em;">
<strong>Summary:</strong> {cme_num} CME event(s) with arrival predictions |
Earth arrivals: {total_earth_arrivals} | Spacecraft arrivals: {total_spacecraft_arrivals}
</p>
<p style="font-size: 0.85em; color: #777; font-style: italic;">
Note: LE (Leading Edge) = bulk CME material, SH (Shock) = shock wave ahead of CME. Shock arrives first.
</p>
"""

        return html



# Main integration function
def generate_reports_with_ai(data: Dict, api_key: Optional[str] = None, model_name: Optional[str] = None) -> Dict[str, str]:
    """
    Generate professional space weather reports using AI

    Args:
        data: Space weather data dictionary with keys:
              - noaa_discussion: NOAA SWPC discussion text
              - uk_met_office: UK Met Office forecast
              - alternative_sources: dict of additional source data
        api_key: Optional API key (uses environment variable if not provided)
        model_name: Optional model name (e.g., 'gpt-5.1', 'claude-sonnet-4.5', 'gemini-2.5-pro')

    Returns:
        Dictionary with keys: html, markdown, json, text
    """
    generator = AIReportGenerator(api_key=api_key, model_name=model_name)
    return generator.generate_report(data)


# Backwards compatibility alias
generate_reports_with_claude = generate_reports_with_ai
