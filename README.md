# Space Weather Report Automation System

Automated generation of professional space weather reports by fetching data from authoritative sources and using AI to produce comprehensive, human-readable reports.

## Features

- **Multi-source data collection**: NOAA SWPC, UK Met Office, SIDC (Solar Influences Data analysis Center)
- **Solar flare tracking**: Rolling 24-hour database with data from LMSAL and NOAA
- **CME tracking**: Enhanced tracking with WSA-ENLIL+Cone model predictions from NASA DONKI
- **Multi-provider AI support**: Anthropic Claude, OpenAI GPT, and Google Gemini
- **Multiple output formats**: HTML, Markdown, JSON, plain text
- **Automatic archival**: Reports organized by year-month with configurable retention

## Quick Start

### Prerequisites

- Python 3.10+
- API key from at least one AI provider (Anthropic, OpenAI, or Google)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/space-weather-reports-CLI.git
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

flare_tracking:
  enabled: true
  retention_hours: 24
```

## Available AI Models

### Anthropic Claude
- `claude-sonnet-4.5` - Fast, balanced performance (recommended)
- `claude-opus-4.5` - Most capable, best for complex analysis
- `claude-haiku-3.5` - Fastest and most economical

### OpenAI GPT
- `gpt-5.1` - Latest with adaptive thinking
- `gpt-5.1-instant` - Fast everyday model
- `gpt-4o` - Multimodal, fast and capable
- `gpt-4o-mini` - Smaller, faster variant
- `o1` / `o1-mini` - Reasoning models

### Google Gemini
- `gemini-2.5-flash` - Fast and capable
- `gemini-2.5-pro` - Best for complex tasks
- `gemini-2.0-flash` - Fast and efficient

## Project Structure

```
space-weather-reports-CLI/
├── space_weather_automation.py   # Main entry point
├── ai_report_generator.py        # AI-powered report generation
├── flare_tracker_simple.py       # Solar flare tracking
├── cme_tracker_enhanced.py       # CME tracking with predictions
├── config.yaml                   # Configuration file
├── model_providers/              # Multi-provider AI system
│   ├── base.py                   # Abstract base class
│   ├── factory.py                # Provider factory
│   ├── anthropic_provider.py     # Claude integration
│   ├── openai_provider.py        # GPT integration
│   └── google_provider.py        # Gemini integration
├── flare_database.db             # SQLite flare database
└── space_weather.db              # SQLite CME database
```

## Data Sources

### Primary Sources
- **NOAA SWPC Discussion**: Official space weather forecasts and analysis
- **UK Met Office**: Space weather forecasts for UK region
- **SIDC**: Solar activity reports from Royal Observatory of Belgium

### Flare Data
- **LMSAL** (preferred): Precise start/peak/end times
- **NOAA**: Official flare classifications

### CME Data
- **NASA DONKI API**: CME analyses, WSA-ENLIL+Cone model predictions, Earth arrival times, Kp estimates

## Database Schema

### flare_database.db
| Column | Description |
|--------|-------------|
| event_date | Date of flare |
| event_time | Start time (UTC) |
| flare_class | Classification (C/M/X) |
| region | Active region number |
| location | Heliographic coordinates |
| peak_time | Peak intensity time |
| end_time | End time |

### space_weather.db
| Table | Description |
|-------|-------------|
| cmes_enhanced | Basic CME information |
| cme_analyses | LE and SH analyses with speeds |
| cme_model_runs | Earth arrival predictions |
| cme_spacecraft_impacts | Spacecraft arrival predictions |

## Output Example

Reports include:
- **Headline**: Engaging summary of the main story
- **Top story**: Narrative description of significant events
- **Flare activity**: Detailed breakdown of solar flares
- **Sunspot regions**: Active region analysis
- **CME tracking**: Earth-directed CME predictions
- **Solar wind conditions**: Speed, IMF, Bz orientation
- **Geomagnetic activity**: Kp index and G-scale storms
- **Forecast**: 3-day outlook with probabilities

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
