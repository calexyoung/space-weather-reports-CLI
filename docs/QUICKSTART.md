# Quick Start Guide - Space Weather Report Automation

## 🚀 Get Started in 4 Steps

### Step 0: Set Up API Key (Optional but Recommended)

For fully automated, professional reports with Claude:

1. **Get API key** from https://console.anthropic.com/
2. **Open `.env` file**:
   ```bash
   cd ~/Documents/Obsidian/CAY-power-vault/space-weather-reports
   nano .env
   ```
3. **Add your key**:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```
4. **Save** (Ctrl+X, Y, Enter)

📖 **Detailed guide:** See `API_KEY_SETUP.md`

### Step 1: Install Dependencies (one time)
```bash
cd ~/Documents/Obsidian/CAY-power-vault/space-weather-reports
pip3 install -r requirements.txt
```

### Step 2: Generate Your First Report
```bash
python3 space_weather_automation.py
```

Check your `space-weather-reports` folder for the generated files!

### Step 3: Automate It (optional)

**Option A - Simple Scheduler:**
```bash
python3 scheduler.py
```
Leave this running. Press Ctrl+C to stop.

**Option B - Background Service (macOS):**
```bash
chmod +x setup.sh
./setup.sh
```
This sets up automatic generation every 6 hours.

---

## 📝 Customization

Edit `config.yaml` to:
- Change update frequency (default: every 6 hours)
- Enable/disable output formats (HTML, Markdown, JSON, Text)
- Add custom data sources
- Change save location

## 📊 Output Files

Reports are saved with timestamps:
- `space_weather_2025-10-03_1230.html` - Rich formatted report
- `space_weather_2025-10-03_1230.md` - Markdown for Obsidian
- `space_weather_2025-10-03_1230.json` - Structured data
- `space_weather_2025-10-03_1230.txt` - Plain text

## 🔍 Monitoring

**View logs:**
```bash
tail -f space_weather_automation.log
```

**Check if service is running:**
```bash
launchctl list | grep spaceweather
```

## 🌐 Browser MCP for Blocked Sites

Some sites block direct scraping. Use browser MCP to access them:

1. **Make sure Chrome is running**
2. **Ask Claude Desktop:**
   ```
   "Fetch LMSAL flare data using browser MCP"
   ```

📖 **Full guide:** See `BROWSER_MCP_SOLUTION.md`

## 🛠 Troubleshooting

**Reports not generating?**
1. Check log file: `tail -50 space_weather_automation.log`
2. Verify internet connection
3. Run manually to see errors: `python3 space_weather_automation.py`

**API key not working?**
1. Verify `.env` file exists and has correct format
2. Check no spaces: `ANTHROPIC_API_KEY=sk-ant-...` (no spaces around =)
3. See `API_KEY_SETUP.md` for detailed troubleshooting

**Want to change schedule?**
Edit `config.yaml` then restart:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist
```

## 💡 Pro Tips

1. **Obsidian Integration**: Reports are already in your vault! Just open them in Obsidian.
2. **Historical Data**: Old reports are kept for 30 days (configurable).
3. **Custom Sources**: Add your favorite space weather sites in `config.yaml`.
4. **Multiple Formats**: Enable all formats to have options for different uses.
5. **API Key**: With Claude API, you get professional-quality reports automatically.

## 📚 Documentation Files

- `API_KEY_SETUP.md` - Complete API key setup guide
- `BROWSER_MCP_SOLUTION.md` - Access blocked websites
- `AUTOMATION_COMPLETE.md` - Full system overview
- `README.md` - Complete detailed documentation
- `config.yaml` - All configuration options

## 🎯 What Works Without API Key?

Even without Claude API, the system:
- ✅ Fetches data from all available sources
- ✅ Creates timestamped archives
- ✅ Generates basic template reports
- ✅ Runs on schedule
- ✅ Logs everything

With API key:
- ✅ **Professional formatted reports**
- ✅ **Intelligent data synthesis**
- ✅ **Natural language summaries**
- ✅ **Complete automation**

---

**Need Help?** 

1. Check logs: `tail -f space_weather_automation.log`
2. See troubleshooting section above
3. Read detailed docs: `API_KEY_SETUP.md` or `README.md`

**Ready to go!** Your first command:
```bash
python3 space_weather_automation.py
```
