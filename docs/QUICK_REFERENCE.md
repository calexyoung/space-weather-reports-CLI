# Quick Reference - Report Review & Refinement

## The Problem You Had

`report_refine_simple.py` was failing because it uses the Claude CLI subprocess method, which can be unreliable.

## The Solution

Created `report_review_api.py` - uses Claude API directly (much more reliable).

---

## Simple Commands

### Just Review Latest Report
```bash
./review
```
That's it! Reviews most recent report and saves feedback to markdown.

### Review Specific Report
```bash
./review reports/2025-11/space_weather_2025-11-07_1706.html
```

### Review + Refine (Complete Workflow)
```bash
./review_and_refine.sh
```
This will:
1. Generate review
2. Show you highlights
3. Ask if you want to refine
4. Create improved version

---

## What Files Do What

| File | Purpose | When to Use |
|------|---------|-------------|
| `report_review_api.py` | Review only (API-based ✅) | Just want feedback |
| `refine_report.py` | Apply review improvements | Want improved version |
| `review_and_refine.sh` | Complete workflow | Want both with confirmation |
| `./review` | Shortcut to review_api | Quick review command |
| ~~`report_refine_simple.py`~~ | Old CLI version (❌ unreliable) | Don't use this one |

---

## Generated Files

After running review:
```
reports/2025-11/
├── space_weather_2025-11-07_1706.html          ← Original
└── report_review_2025-11-07_1706.md            ← Review feedback
```

After running refine:
```
reports/2025-11/
├── space_weather_2025-11-07_1706.html          ← Original
├── report_review_2025-11-07_1706.md            ← Review
└── space_weather_2025-11-07_1720_refined.html  ← Improved version
```

---

## Troubleshooting

### "API credit balance too low"
Your Anthropic API credits need to be topped up.
- Go to: https://console.anthropic.com/settings/billing
- Add credits or upgrade plan

### "Review saved but empty"
Check if `ANTHROPIC_API_KEY` is set in `.env`:
```bash
cat .env | grep ANTHROPIC_API_KEY
```

### "No reports found"
Generate a report first:
```bash
python3.11 space_weather_automation.py
```

---

## Cost

- **Review**: ~$0.08 (5K tokens)
- **Refine**: ~$0.12 (8K tokens)
- **Total for both**: ~$0.20

Compare to updating code manually: Free but takes your time!

---

## Pro Tips

1. **Don't review every report** - Only ~20% need extra attention
2. **Use core prompt improvements** for recurring issues (already done!)
3. **Save review files** - They're markdown, great for tracking patterns
4. **Compare refined vs original** - See what actually improved
5. **Use `./review` daily** - Quick way to spot issues before they compound

---

## Migration Path

**Old way (CLI-based, broken):**
```bash
python3.11 report_refine_simple.py --review-only
```

**New way (API-based, reliable):**
```bash
./review
# OR
python3.11 report_review_api.py
```

Both do the same thing, but the new way uses the API directly instead of subprocess calls to Claude CLI.
