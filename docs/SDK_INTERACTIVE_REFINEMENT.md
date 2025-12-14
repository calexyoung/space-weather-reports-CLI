# Claude Agent SDK Interactive Refinement

Complete guide to using the Claude Agent SDK for conversational report refinement.

## Overview

The SDK integration enables you to refine space weather reports through natural conversation with Claude, building up a science knowledge base that improves over time. This replaces the need for ChatGPT in your daily workflow while maintaining conversation context and learning from each session.

## Why SDK Instead of Direct API?

**Current Automation (Unchanged):**
- Single API call generates complete report
- Stateless, deterministic, reliable
- Perfect for scheduled automation

**SDK Refinement (New Feature):**
- Multi-turn conversations with context retention
- Claude can query databases to verify facts
- Tool use for reading files and executing commands
- Builds knowledge base from refinement patterns
- Human-in-the-loop for quality control

**They work together:** Automation generates base reports, SDK refines them conversationally.

## Installation

### Requirements
- **Python 3.10+** (installed as python3.11)
- **Node.js** (for Claude Code CLI)
- **Claude Code CLI**
- **Claude Agent SDK Python package**

### Setup Steps

```bash
# 1. Python 3.11 already installed via Homebrew
python3.11 --version  # Should show 3.11.x

# 2. Install Claude Code CLI (already done)
npm install -g @anthropic-ai/claude-code

# 3. Install Python SDK (already done)
python3.11 -m pip install claude-agent-sdk

# 4. Verify installation
which claude-code  # Should show path to CLI
```

### Configuration

SDK settings in `config.yaml`:

```yaml
sdk_integration:
  enabled: true
  permission_mode: "plan"  # Ask before making edits
  allowed_tools:
    - "Read"
    - "Write"
    - "Bash"
    - "Grep"
    - "Glob"
  knowledge_base:
    enabled: true
    directory: "knowledge_base"
```

## Daily Workflow

### Morning Routine

**Step 1: Generate Automated Report**
```bash
# Your normal automation (runs every 6 hours or on-demand)
python3 space_weather_automation.py
```

This creates: `reports/2025-11/space_weather_2025-11-07_0600.html`

**Step 2: Review and Refine**
```bash
# Quick review mode (default)
python3.11 report_refine_sdk.py
```

**What happens:**
1. Claude automatically finds latest report
2. Reads report and associated data files
3. Provides numbered list of specific improvements
4. Offers to enter interactive mode

**Example output:**
```
📄 Report: space_weather_2025-11-07_0600.html
🔍 Claude is analyzing the report...
======================================================================

🤖 Claude: I've analyzed the report. Here are specific improvements:

1. Headline lacks impact
   Current: "Solar activity moderate"
   Suggestion: "M5.3 flare signals uptick in solar activity"

2. M5.3 flare timing vague
   Current: "occurred this morning"
   Database shows: Peak at 06:24 UTC from AR4274
   Fix: Add specific UTC time

3. CME Earth-impact incomplete
   Current: "Expected to arrive November 7"
   Model data shows: 03:18 UTC ±7h, Kp 7-9 (G3-G4 storms)
   Fix: Add arrival time and Kp forecast

4. AR4274 description too generic
   Current: "active region"
   Data shows: Beta-gamma-delta configuration
   Fix: Mention magnetic class and high flare probability

======================================================================

Would you like to refine the report interactively? (y/n):
```

**Step 3: Interactive Refinement (Optional)**

If you type `y`, enters conversation mode:

```
👤 You: Fix items 1-3

🤖 Claude: I'll update the headline, add M5.3 timing, and include Kp forecast.
   Let me check the databases first...
   🔧 Using Bash: sqlite3 flare_database.db...
   🔧 Using Read: reports/2025-11/space_weather_2025-11-07_0600_data.json

   Updated sections:
   - Headline: "M5.3 flare at 06:24 UTC signals uptick in solar activity"
   - Flare detail: "...peaked at 06:24 UTC from AR4274 (N24E45)..."
   - CME forecast: "...arriving November 7 at 03:18 UTC (±7 hours) with
                    Kp 7-9, indicating G3-G4 geomagnetic storm potential"

   Shall I write these changes to a refined version?

👤 You: Yes, and add more detail about AR4274

🤖 Claude: I'll enhance the AR4274 description...
   🔧 Using Grep: Searching for AR4274 magnetic class...

   Added: "AR4274, a beta-gamma-delta magnetic configuration located at
          N24E45, continues to show high flare probability..."

   Writing updated report to:
   reports/2025-11/space_weather_2025-11-07_0600_refined.html

👤 You: done

✅ Refinement session complete (3 turns)
📝 Session log saved to: knowledge_base/conversation_logs/20251107_0624.md
📄 Refined report: reports/2025-11/space_weather_2025-11-07_0600_refined.html
```

## Usage Modes

### Mode 1: Quick Review (Default)
```bash
python3.11 report_refine_sdk.py
```

**Best for:** Morning checks, finding what needs attention
**Output:** Numbered list of improvements
**Time:** ~30-60 seconds

### Mode 2: Interactive Conversation
```bash
python3.11 report_refine_sdk.py --interactive
```

**Best for:** Detailed refinement, iterative improvements
**Output:** Full conversational session
**Time:** 2-5 minutes (human-in-loop)

### Mode 3: Review Only (No Changes)
```bash
python3.11 report_refine_sdk.py --review-only
```

**Best for:** Just getting suggestions to apply manually
**Output:** Suggestions only, no conversation
**Time:** ~30 seconds

### Mode 4: Specific Report
```bash
python3.11 report_refine_sdk.py --file reports/2025-11/space_weather_2025-11-06_1200.html
```

**Best for:** Refining older reports
**Output:** Same options as default

## What Claude Can Do

### Tool Capabilities

**Read Files:**
- Report files (HTML, MD, JSON, TXT)
- Data package JSON files
- Knowledge base documents

**Query Databases:**
```bash
# Example: Verify M5.3 flare timing
sqlite3 flare_database.db "SELECT * FROM flares WHERE flare_class = 'M5.3'"

# Example: Check CME arrival predictions
sqlite3 space_weather.db "SELECT * FROM cme_model_runs WHERE earth_arrival_time IS NOT NULL"
```

**Search Content:**
```bash
# Find specific terms in reports
grep "AR4274" reports/2025-11/*.html

# Find all M-class flares mentioned
grep -E "M[0-9]\." reports/2025-11/*.md
```

**Write Files:**
- Create refined report versions
- Update knowledge base files
- Save conversation logs

## Knowledge Base

### Structure

```
knowledge_base/
├── science_context.md         # Physics and terminology
├── writing_guidelines.md      # Style preferences
├── refinement_patterns.md     # Common corrections
└── conversation_logs/         # Session histories
    ├── 20251107_0624.md
    ├── 20251107_0624.json
    └── ...
```

### How It Grows

**1. Science Context** (`science_context.md`)
- Physics explanations
- Data source descriptions
- Common relationships (CME speed → Kp forecast)

**2. Writing Guidelines** (`writing_guidelines.md`)
- Your style preferences
- Headline formats
- Technical detail level
- Tone and voice

**3. Refinement Patterns** (`refinement_patterns.md`)
- Common mistakes and fixes
- Frequency tracking
- Learning insights

**4. Conversation Logs** (`conversation_logs/`)
- Complete session transcripts
- Markdown for reading
- JSON for programmatic analysis

### Building the Knowledge Base

Claude loads knowledge base content at the start of each session. Over time:

1. **Patterns emerge:** "Always include UTC times for M+ flares"
2. **Preferences captured:** "User prefers dramatic headlines"
3. **Context deepens:** "CME >1000 km/s usually means strong storm"
4. **Quality improves:** Future automated reports get better prompts

## Advanced Usage

### Custom Prompts

Start conversation with specific requests:

```bash
python3.11 report_refine_sdk.py --interactive

# Then:
👤 You: Check all CME arrival times against the database and fix any discrepancies

👤 You: Make the forecast section more detailed, breaking out each day clearly

👤 You: The headline needs to be more dramatic but still accurate

👤 You: Verify all active region numbers and locations are correct
```

### Database Queries

Claude can verify facts:

```bash
👤 You: Is the M5.3 flare time correct? Check the database

🤖 Claude: Let me verify...
   🔧 Bash: sqlite3 flare_database.db "SELECT event_date, event_time,
            peak_time FROM flares WHERE flare_class = 'M5.3'"

   Database shows:
   - Event start: 05:48 UTC
   - Peak time: 06:24 UTC

   Report currently says "06:24 UTC" which matches the peak time.
   This is correct! ✓
```

### Multi-Turn Refinement

Build on previous exchanges:

```bash
👤 You: Fix the headline

🤖 Claude: Updated to "M5.3 flare signals uptick in solar activity"

👤 You: Actually make it more dramatic

🤖 Claude: How about: "The Sun erupts with M5.3 flare — activity surges!"

👤 You: Good but remove the exclamation point

🤖 Claude: Updated to: "The Sun erupts with M5.3 flare as activity surges"
```

## Best Practices

### DO:

✅ **Be specific:** "Add UTC time for M5.3 flare" not "improve timing"
✅ **Verify facts:** Ask Claude to check databases when uncertain
✅ **Iterate:** Make multiple small refinements in conversation
✅ **Learn patterns:** Let knowledge base accumulate over time
✅ **Review suggestions:** Quick review mode catches most issues

### DON'T:

❌ **Replace automation:** Keep using automated generation for base reports
❌ **Skip verification:** Always fact-check against databases
❌ **Make vague requests:** "Make it better" doesn't help Claude
❌ **Ignore knowledge base:** It improves future refinements
❌ **Over-refine:** Sometimes automated output is good enough

## Troubleshooting

### SDK Not Working

**Error:** `claude-code not found`
```bash
# Install CLI
npm install -g @anthropic-ai/claude-code

# Verify
which claude-code
```

**Error:** `ModuleNotFoundError: No module named 'claude_agent_sdk'`
```bash
# Install with Python 3.11
python3.11 -m pip install claude-agent-sdk

# Verify
python3.11 -c "import claude_agent_sdk; print('OK')"
```

**Error:** `Permission denied` for tool use
```yaml
# Change permission mode in config.yaml
sdk_integration:
  permission_mode: "bypassPermissions"  # Auto-approve everything
```

### No Reports Found

**Error:** `No reports found in reports/ directory`
```bash
# Generate a report first
python3 space_weather_automation.py

# Then refine
python3.11 report_refine_sdk.py
```

### Empty Response from Claude

This usually means:
1. API key issue (check .env)
2. Network connectivity
3. Claude Code CLI not running

```bash
# Test CLI directly
claude-code --version

# Check logs
tail -f space_weather_automation.log
```

## Cost and Performance

**Automated Report Generation:**
- Cost: ~$0.15 per report
- Time: 15-30 seconds
- Frequency: Every 6 hours

**SDK Refinement (Optional):**
- Cost: ~$0.50-1.50 per session (3-10 turns)
- Time: 2-5 minutes (includes human time)
- Frequency: As needed (daily morning review typical)

**Total Daily Cost:**
- 4 automated reports: $0.60
- 1 morning refinement: ~$1.00
- **Total: ~$1.60/day**

## Integration with Automation

The SDK **complements** your automation, it doesn't replace it:

```
AUTOMATED WORKFLOW (Every 6 hours)
├─ Fetch data from sources
├─ Query databases
├─ Generate report via Claude API
└─ Save to reports/

MANUAL REFINEMENT (Once per morning)
├─ Run report_refine_sdk.py
├─ Review Claude's suggestions
├─ Iterate improvements in conversation
└─ Save refined version

KNOWLEDGE ACCUMULATION (Continuous)
├─ Patterns learned from refinements
├─ Science context built up
└─ Future automated reports improve
```

## Next Steps

1. **Test the tool:**
   ```bash
   # Generate a test report
   python3 space_weather_automation.py

   # Try quick review
   python3.11 report_refine_sdk.py
   ```

2. **Use for one week:**
   - Daily morning reviews
   - Note common patterns
   - Watch knowledge base grow

3. **Refine prompts:**
   - Update `science_context.md` with learned patterns
   - Add style preferences to `writing_guidelines.md`
   - Use accumulated knowledge for better automated reports

4. **Merge to main:**
   - Once confident in SDK workflow
   - Create PR from `sdk-integration` branch
   - Keep automation unchanged, SDK as optional feature

## Questions?

See also:
- [CLAUDE.md](../CLAUDE.md) - Complete system documentation
- [README.md](../README.md) - Quick start guide
- `knowledge_base/` - Accumulated refinement wisdom

The SDK gives you the conversational refinement you've been using ChatGPT for, but with Claude, context retention, database verification, and continuous learning!
