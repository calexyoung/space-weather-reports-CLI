# Space Weather Report Automation System

Automated generation of professional space weather reports by fetching data from authoritative sources and using AI to produce comprehensive, human-readable reports.

## Features

- **Multi-source data collection**: NOAA SWPC, UK Met Office, SIDC (Solar Influences Data analysis Center)
- **Solar flare tracking**: Rolling 24-hour database with data from LMSAL and NOAA
- **CME tracking**: Enhanced tracking with WSA-ENLIL+Cone model predictions from NASA DONKI
- **Multi-provider AI support**: Anthropic Claude, OpenAI GPT, and Google Gemini
- **Multiple output formats**: HTML, Markdown, JSON, plain text
- **Automated scheduling**: Configurable report generation and flare collection schedules
- **Automatic archival**: Reports organized by year-month with configurable retention

## Quick Start

### Prerequisites

- Python 3.10+
- API key from at least one AI provider (Anthropic, OpenAI, or Google)

### Installation

```bash
# Clone the repository
git clone https://github.com/calexyoung/space-weather-reports-CLI.git
cd space-weather-reports-CLI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your API key(s)
```

### Generate a Report

```bash
# Use default model (from config.yaml)
python3 space_weather_automation.py

# Use a specific model
python3 space_weather_automation.py --model gpt-5.1
python3 space_weather_automation.py --model claude-sonnet-4.5
python3 space_weather_automation.py --model gemini-2.5-pro

# Add custom suffix to output files
python3 space_weather_automation.py --model gpt-5.1 --output-suffix openai
```

## Scheduling

### Foreground Schedulers

```bash
# Main report scheduler (configurable interval, default 6 hours)
python3 scheduler.py

# Flare collection scheduler (every 4 hours)
python3 flare_scheduler.py
```

Press `Ctrl+C` to stop.

### Background Service (macOS launchd)

```bash
# Load the service
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist

# Check status
launchctl list | grep spaceweather

# Stop the service
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist
```

### Process Management

```bash
# Check running processes
ps aux | grep -E "(scheduler|space_weather)" | grep -v grep

# View recent logs
tail -20 space_weather_automation.log

# Kill processes if needed
pkill -f space_weather_automation.py
pkill -f scheduler.py
pkill -f flare_scheduler.py
```

## Configuration

### Environment Variables (.env)

```bash
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
```

### Config File (config.yaml)

Key configuration options:

```yaml
models:
  default: "claude-sonnet-4.5"  # Default AI model

output:
  base_directory: "/path/to/reports"
  formats:
    html: true
    markdown: true
    json: true
    text: true
  max_archive_days: 30

schedule:
  interval_hours: 6
  specific_times: []  # Or ["00:00", "06:00", "12:00", "18:00"]

flare_tracking:
  enabled: true
  retention_hours: 24
```

## Available AI Models

### Anthropic Claude
| Model | Description |
|-------|-------------|
| `claude-sonnet-4.5` | Fast, balanced performance (recommended) |
| `claude-opus-4.5` | Most capable, best for complex analysis |
| `claude-haiku-3.5` | Fastest and most economical |

### OpenAI GPT
| Model | Description |
|-------|-------------|
| `gpt-5.1` | Latest with adaptive thinking |
| `gpt-5.1-instant` | Fast everyday model |
| `gpt-4o` | Multimodal, fast and capable |
| `gpt-4o-mini` | Smaller, faster variant |
| `o1` / `o1-mini` | Reasoning models |

### Google Gemini
| Model | Description |
|-------|-------------|
| `gemini-2.5-flash` | Fast and capable |
| `gemini-2.5-pro` | Best for complex tasks |
| `gemini-2.0-flash` | Fast and efficient |

## Project Structure

```
space-weather-reports-CLI/
├── space_weather_automation.py   # Main entry point
├── ai_report_generator.py        # AI-powered report generation
├── flare_tracker_simple.py       # Solar flare tracking
├── cme_tracker_enhanced.py       # CME tracking with predictions
├── scheduler.py                  # Main report scheduler
├── flare_scheduler.py            # Flare collection scheduler
├── migrate_flare_db.py           # Database migration utility
├── config.yaml                   # Configuration file
├── requirements.txt              # Python dependencies
├── model_providers/              # Multi-provider AI system
│   ├── __init__.py
│   ├── base.py                   # Abstract base class
│   ├── factory.py                # Provider factory
│   ├── anthropic_provider.py     # Claude integration
│   ├── openai_provider.py        # GPT integration
│   └── google_provider.py        # Gemini integration
├── knowledge_base/               # Reference materials
│   ├── comprehensive_aurora_forecasting_guide.md
│   ├── science_context.md
│   ├── writing_guidelines.md
│   └── refinement_patterns.md
├── docs/                         # Documentation
│   ├── QUICKSTART.md
│   ├── PRD.md
│   ├── REPORT_STYLE_GUIDE.md
│   ├── FLARE_TRACKING_GUIDE.md
│   ├── API_KEY_SETUP.md
│   └── [additional docs...]
├── reports/                      # Generated reports (by YYYY-MM)
├── flare_database.db             # SQLite flare database
└── space_weather.db              # SQLite CME database
```

## Data Sources

### Primary Sources
| Source | Description |
|--------|-------------|
| NOAA SWPC Discussion | Official space weather forecasts and analysis |
| UK Met Office | Space weather forecasts for UK region |
| SIDC | Solar activity reports from Royal Observatory of Belgium |

### Flare Data
| Source | Description |
|--------|-------------|
| LMSAL (preferred) | Precise start/peak/end times |
| NOAA | Official flare classifications |

### CME Data
| Source | Description |
|--------|-------------|
| NASA DONKI API | CME analyses, WSA-ENLIL+Cone model predictions, Earth arrival times, Kp estimates |

## Database Schema

### flare_database.db

| Column | Description |
|--------|-------------|
| `event_date` | Date of flare |
| `event_time` | Start time (UTC) |
| `event_timestamp` | Unix timestamp |
| `flare_class` | Classification (C/M/X) |
| `region` | Active region number |
| `location` | Heliographic coordinates |
| `peak_time` | Peak intensity time |
| `end_time` | End time |
| `source` | Data source (LMSAL/NOAA) |

### space_weather.db

| Table | Description |
|-------|-------------|
| `cmes_enhanced` | Basic CME information |
| `cme_analyses` | LE and SH analyses with speeds |
| `cme_model_runs` | Earth arrival predictions |
| `cme_spacecraft_impacts` | Spacecraft arrival predictions |

## Report Contents

Generated reports include:

- **Headline**: Engaging summary of the main story
- **Top story**: Narrative description of significant events
- **Flare activity**: Detailed breakdown of solar flares with times and regions
- **Sunspot regions**: Active region analysis with magnetic classifications
- **CME tracking**: Earth-directed CME predictions with arrival times
- **Solar wind conditions**: Speed, IMF strength, Bz orientation
- **Geomagnetic activity**: Kp index and G-scale storm levels
- **Forecast**: 3-day outlook with probabilities and aurora visibility

## Standalone Tools

### Flare Tracker
```bash
python3 flare_tracker_simple.py
```

### CME Tracker
```bash
python3 cme_tracker_enhanced.py
```

### Database Migration
```bash
python3 migrate_flare_db.py
```

## Monitoring

### View Logs
```bash
# Main automation log
tail -f space_weather_automation.log

# Flare collection log
tail -f flare_collection.log
```

### Check Service Status
```bash
launchctl list | grep spaceweather
```

## Troubleshooting

### Reports not generating?
1. Check log file: `tail -50 space_weather_automation.log`
2. Verify internet connection
3. Run manually to see errors: `python3 space_weather_automation.py`

### API key not working?
1. Verify `.env` file exists with correct format
2. Check no spaces around `=`: `ANTHROPIC_API_KEY=sk-ant-...`
3. See `docs/API_KEY_SETUP.md` for detailed troubleshooting

### Want to change schedule?
Edit `config.yaml` then restart the scheduler or launchd service.

## What Works Without API Key?

Even without an AI API key, the system:
- Fetches data from all available sources
- Creates timestamped archives
- Generates basic template reports
- Runs on schedule
- Logs everything

With an API key, you additionally get:
- Professional formatted reports
- Intelligent data synthesis
- Natural language summaries
- Engaging narrative style

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Acknowledgments

- NOAA Space Weather Prediction Center
- UK Met Office Space Weather Operations Centre
- SIDC - Royal Observatory of Belgium
- NASA CCMC DONKI
- LMSAL Latest Events Archive
