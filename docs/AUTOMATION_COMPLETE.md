# Space Weather Report Automation - Complete Solution

## ✅ What Has Been Created

I've set up a complete automation system in your Obsidian vault:

📁 `/Users/cayoung/Documents/Obsidian/CAY-power-vault/space-weather-reports/`

### Files Created:

1. **config.yaml** - Configuration file for all settings
2. **space_weather_automation.py** - Main automation script
3. **scheduler.py** - 6-hour interval scheduler
4. **claude_integration.py** - Claude API integration module
5. **requirements.txt** - Python dependencies
6. **setup.sh** - One-click setup script for macOS
7. **README.md** - Complete documentation
8. **QUICKSTART.md** - Quick start guide
9. **space_weather_2025-10-03_1230_EXAMPLE.html** - Today's actual report as example

## 🎯 Your Questions Answered

### 1. Can this be automated using skills and connectors?

**YES!** Three automation approaches:

#### A. Claude API Integration (Recommended)
- Install: `pip install anthropic`
- Set API key: `export ANTHROPIC_API_KEY='your-key'`
- The system will automatically use Claude to generate full reports
- See `claude_integration.py` for implementation

#### B. MCP (Model Context Protocol)
- Use Claude Desktop with filesystem MCP
- Create workflows that trigger report generation
- Claude reads data sources and writes reports directly

#### C. Manual with Templates
- Automation scripts fetch data
- Use templates for basic reports
- Upload to Claude for full formatting when needed

### 2. Addressing websites that couldn't be accessed?

**SOLVED!** The system includes:
- Multiple fallback sources for each data type
- Alternative flare databases when LMSAL is blocked
- Web search fallbacks for critical data
- Configurable source priority in `config.yaml`

Add custom sources:
```yaml
alternative_sources:
  your_source: "https://your-preferred-site.com"
```

### 3. Save HTML reports to your computer?

**YES!** Reports are automatically saved to:
```
/Users/cayoung/Documents/Obsidian/CAY-power-vault/space-weather-reports/
```

Each report includes a timestamp:
- `space_weather_2025-10-03_1230.html`
- `space_weather_2025-10-03_1230.md`
- `space_weather_2025-10-03_1230.json`

Change location in `config.yaml`:
```yaml
output:
  base_directory: "/your/custom/path"
```

### 4. Optional input sources?

**YES!** Fully configurable in `config.yaml`:

```yaml
primary_sources:
  noaa_discussion: "https://services.swpc.noaa.gov/text/discussion.txt"
  uk_met_office: "https://weather.metoffice.gov.uk/specialist-forecasts/space-weather"
  your_source: "https://custom-source.com"

alternative_sources:
  spaceweather_com: "https://www.spaceweather.com/"
  custom: "https://your-backup-source.com"
```

### 5. Optional output formats?

**YES!** Enable/disable any format:

```yaml
output:
  formats:
    html: true      # Rich formatted reports
    markdown: true  # For Obsidian
    json: true      # Structured data
    text: true      # Plain text
    pdf: false      # Requires weasyprint
```

### 6. Run every 6 hours?

**YES!** Multiple options:

#### Option 1: Simple Scheduler (Foreground)
```bash
python3 scheduler.py
```
Runs every 6 hours while script is active.

#### Option 2: launchd Service (Background - macOS)
```bash
cd ~/Documents/Obsidian/CAY-power-vault/space-weather-reports
chmod +x setup.sh
./setup.sh
```
Runs automatically every 6 hours in background, even after restart.

#### Option 3: Custom Schedule
Edit `config.yaml`:
```yaml
schedule:
  interval_hours: 6  # Or any interval
  specific_times: ["00:00", "06:00", "12:00", "18:00"]  # Or specific times
```

## 🚀 Getting Started

### Quick Start (3 commands):
```bash
cd ~/Documents/Obsidian/CAY-power-vault/space-weather-reports
pip3 install -r requirements.txt
python3 space_weather_automation.py
```

### Full Automation Setup:
```bash
chmod +x setup.sh
./setup.sh
```

## 🎨 Customization Examples

### Change Update Frequency to 3 Hours:
```yaml
schedule:
  interval_hours: 3
```

### Add SpaceWeatherLive as Source:
```yaml
alternative_sources:
  spaceweatherlive: "https://www.spaceweatherlive.com/en/solar-activity.html"
```

### Save to Desktop Instead:
```yaml
output:
  base_directory: "/Users/cayoung/Desktop/space-weather"
```

### Keep Reports for 90 Days:
```yaml
output:
  archive: true
  max_archive_days: 90
```

## 🔧 Advanced Features

### Claude API Integration

For fully-automated, professional reports:

1. Get API key from https://console.anthropic.com/
2. Install SDK: `pip install anthropic`
3. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY='your-api-key'
   # Add to ~/.zshrc or ~/.bash_profile for persistence
   ```
4. Run automation - it will use Claude automatically!

### Monitoring

**View real-time logs:**
```bash
tail -f space_weather_automation.log
```

**Check if service is running:**
```bash
launchctl list | grep spaceweather
```

**View recent reports:**
```bash
ls -lt ~/Documents/Obsidian/CAY-power-vault/space-weather-reports/*.html | head -5
```

## 📊 What You Get

Every 6 hours, the system:
1. ✅ Fetches latest data from NOAA SWPC
2. ✅ Gets UK Met Office forecasts
3. ✅ Checks alternative sources if needed
4. ✅ Generates professional HTML report
5. ✅ Creates Markdown for Obsidian
6. ✅ Exports JSON for data analysis
7. ✅ Saves plain text version
8. ✅ Archives with timestamps
9. ✅ Cleans up old reports
10. ✅ Logs everything for debugging

## 🆘 Troubleshooting

### Reports not generating?
```bash
# Check logs
tail -50 space_weather_automation.log

# Test manually
python3 space_weather_automation.py

# Check internet
curl https://services.swpc.noaa.gov/text/discussion.txt
```

### Service not running?
```bash
# Check status
launchctl list | grep spaceweather

# Restart service
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist
```

### Want different schedule?
```bash
# Edit config
nano config.yaml

# Restart to apply changes
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist
```

## 🎓 Next Steps

1. **Try it now**: Generate your first report
   ```bash
   python3 space_weather_automation.py
   ```

2. **Customize**: Edit `config.yaml` to your preferences

3. **Automate**: Run `./setup.sh` for 6-hour automation

4. **Integrate Claude**: Add API key for professional reports

5. **Explore**: Check your Obsidian vault for the reports!

## 📚 Documentation

- **QUICKSTART.md** - Get running in minutes
- **README.md** - Complete detailed documentation
- **config.yaml** - All settings with comments
- **Example report** - See what you'll get

## 💡 Pro Tips

1. **Obsidian Integration**: Reports are already in your vault! Just link them in your daily notes.

2. **Historical Analysis**: Keep reports for months to track solar cycles.

3. **Multiple Formats**: Enable all formats - HTML for viewing, Markdown for notes, JSON for analysis.

4. **Custom Sources**: Add your favorite space weather sites for redundancy.

5. **API Integration**: With Claude API, you get professional-quality reports automatically.

---

**You're all set!** The system is ready to generate space weather reports automatically every 6 hours. 

Start with: `python3 space_weather_automation.py`

Questions? Check the logs: `tail -f space_weather_automation.log`
