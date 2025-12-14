# Report Refinement Guide

## Three Approaches to Improving Reports

### 🎯 **Option 1: Post-Generation Refinement (Recommended)**

**Best for:** Iterative improvements without modifying core code

**Workflow:**
```bash
# 1. Generate report normally
python3.11 space_weather_automation.py

# 2. Review the report
python3.11 report_refine_simple.py --review-only

# 3. Refine based on review
python3.11 refine_report.py

# OR use the combined workflow:
./review_and_refine.sh
```

**Pros:**
- ✅ No code changes needed
- ✅ Each report can be refined independently
- ✅ Review feedback saved for future reference
- ✅ Original report preserved (creates `*_refined.html`)
- ✅ Can iterate multiple times if needed

**Cons:**
- ⏱️ Takes 2-3 minutes per refinement (API call)
- 💰 Uses additional API tokens (~8K tokens/refinement)

**When to use:**
- One-off improvements for important reports
- Testing different refinement approaches
- When you want to preserve the original
- For reports that need special attention

---

### 🔧 **Option 2: Update Core Prompt (What We Just Did)**

**Best for:** Permanent improvements to all future reports

**How it works:**
- Edit `claude_integration_enhanced.py`
- Add guidelines to `_build_detailed_prompt()` method
- All future reports automatically apply improvements

**Pros:**
- ✅ No manual refinement needed
- ✅ Consistent quality across all reports
- ✅ No extra API calls
- ✅ Improvements compound over time

**Cons:**
- ⚙️ Requires code changes
- 🧪 Need to test changes don't break things
- 📝 Prompt can get very long

**When to use:**
- Recurring issues across multiple reports
- Standard improvements everyone wants
- Quality baseline for automation
- Issues that review catches repeatedly

**Already Applied:**
- Aurora visibility city names
- CME arrival time specificity
- Multi-CME context explanation
- Radio blackout details

---

### 🎨 **Option 3: Custom Refinement Prompts**

**Best for:** Specific editorial styles or requirements

Create specialized refinement scripts for different needs:

```python
# example: refine_for_social_media.py
def refine_for_twitter(report_html):
    """Extract key highlights as tweet-length summaries"""
    prompt = "Create 5 tweet-sized highlights from this report..."
    # ...

# example: refine_for_technical.py
def refine_for_experts(report_html):
    """Add more technical details and data"""
    prompt = "Enhance with additional technical details..."
    # ...
```

**When to use:**
- Multiple audiences (public, technical, social media)
- Special events (major storms, X-class flares)
- Custom formats (newsletter, blog post, alert)

---

## Recommended Workflow

### Daily Automated Reports
Use **Option 2** (core prompt improvements) for baseline quality.

```bash
# Runs every 6 hours via scheduler
python3.11 space_weather_automation.py
```

Reports automatically include:
- Specific aurora visibility cities
- Detailed CME arrival predictions
- Multi-CME context
- Professional formatting

### Important Reports Needing Extra Polish
Use **Option 1** (post-generation refinement):

```bash
# 1. Generate report
python3.11 space_weather_automation.py

# 2. Review and refine
./review_and_refine.sh

# 3. Use the refined version for distribution
```

### Special Circumstances
Use **Option 3** (custom refinement):

```bash
# Major storm event - create alert version
python3.11 refine_for_alerts.py reports/2025-11/space_weather_2025-11-07_1654.html

# Social media - extract highlights
python3.11 refine_for_social.py reports/2025-11/space_weather_2025-11-07_1654.html
```

---

## Files Reference

### Core Generation
- `space_weather_automation.py` - Main report generator
- `claude_integration_enhanced.py` - Claude API integration with prompts

### Review & Refinement
- `report_refine_simple.py` - Generate review with improvement suggestions
- `refine_report.py` - Apply review improvements to create refined version
- `review_and_refine.sh` - Complete workflow script

### Generated Files
- `space_weather_YYYY-MM-DD_HHMM.html` - Original report
- `report_review_YYYY-MM-DD_HHMM.md` - Review with suggestions
- `space_weather_YYYY-MM-DD_HHMM_refined.html` - Improved version

---

## Cost Analysis

**Option 1 - Post-Generation Refinement:**
- Generation: ~12K tokens ($0.18)
- Review: ~5K tokens ($0.08)
- Refinement: ~8K tokens ($0.12)
- **Total: ~$0.38 per refined report**

**Option 2 - Core Prompt Updates:**
- Generation: ~14K tokens ($0.21) ← slightly longer prompt
- No additional costs
- **Total: ~$0.21 per report**

**Recommendation:** Use Option 2 for daily automation (saves ~$0.17 per report), Option 1 for ~20% of reports that need extra attention.

---

## Quick Commands

```bash
# Generate report
python3.11 space_weather_automation.py

# Review latest report (API-based, reliable)
./review                                    # Simple!
# OR
python3.11 report_review_api.py            # Latest report
python3.11 report_review_api.py [file]     # Specific report

# Refine latest report
python3.11 refine_report.py

# Complete workflow (review + refine with confirmation)
./review_and_refine.sh

# Refine specific report
python3.11 refine_report.py reports/2025-11/space_weather_2025-11-07_1654.html
```

**Note:** Use `report_review_api.py` (API-based) instead of `report_refine_simple.py` (CLI-based) for more reliable reviews.

---

## Best Practices

1. **Use core prompt improvements** for recurring issues
2. **Use post-refinement** for ~20% of reports needing extra polish
3. **Save review files** to track common issues over time
4. **Compare original vs refined** to validate improvements
5. **Update core prompts quarterly** based on review patterns

This gives you flexibility: automate the baseline quality, refine when needed, without constant code changes!
