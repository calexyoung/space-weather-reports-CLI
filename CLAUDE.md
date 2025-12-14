# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Space Weather Report Automation System - generates automated space weather reports by fetching data from authoritative sources (NOAA SWPC, UK Met Office, SIDC), tracking solar flares and CMEs, and using AI to produce professional reports in multiple formats (HTML, Markdown, JSON, text).

## Commands

### Generate Report
```bash
python3 space_weather_automation.py
python3 space_weather_automation.py --model gpt-5.1  # Use specific model
python3 space_weather_automation.py --model claude-sonnet-4.5 --output-suffix anthropic
```

### Flare Tracking
```bash
python3 flare_tracker_simple.py  # Run standalone flare collection
```

### CME Tracking
```bash
python3 cme_tracker_enhanced.py  # Initialize/test CME database
```

### Database Migration
```bash
python3 migrate_flare_db.py  # Fix duplicate flares
```

## Architecture

### Main Entry Point
- `space_weather_automation.py` - Orchestrates data collection, report generation, and file saving via `SpaceWeatherReportGenerator` class

### Data Trackers
- `flare_tracker_simple.py` - `SimpleFlareTracker` class scrapes LMSAL and NOAA for solar flare data, stores in `flare_database.db` (SQLite), maintains rolling 24-hour window
- `cme_tracker_enhanced.py` - `EnhancedCMETracker` class fetches CME data from NASA DONKI API, stores in `space_weather.db` with tables: `cmes_enhanced`, `cme_analyses`, `cme_model_runs`, `cme_spacecraft_impacts`

### Multi-Model Provider System
Located in `model_providers/`:
- `base.py` - Abstract `ModelProvider` class, `ModelConfig` and `ModelResponse` dataclasses
- `factory.py` - `get_provider()` factory function creates providers from model name
- `anthropic_provider.py` - Claude API integration
- `openai_provider.py` - OpenAI/GPT integration
- `google_provider.py` - Google Gemini integration

Models configured in `config.yaml` under `models.providers`. Default model set via `models.default`.

### Configuration
- `config.yaml` - Data source URLs, output settings, model config, schedule settings
- `.env` - API keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`

### AI Report Generator
- `ai_report_generator.py` - `AIReportGenerator` class and `generate_reports_with_ai()` function for AI-powered report generation

### Data Flow
1. `SpaceWeatherReportGenerator.run()` calls `collect_latest_flares()` to refresh flare data
2. `generate_report_data()` fetches from NOAA, UK Met Office, SIDC, and queries flare/CME databases
3. `call_ai_for_report()` uses model provider to generate formatted report
4. `save_report()` writes to configured output directory organized by YYYY-MM subdirectories

### Output
Reports saved to `output.base_directory` (configurable) in formats: HTML, Markdown, JSON, text. Filename pattern: `space_weather_{date}_{time}.{ext}`

## Key Classes

- `SpaceWeatherReportGenerator` - Main orchestrator in `space_weather_automation.py`
- `AIReportGenerator` - AI-powered report generation in `ai_report_generator.py`
- `SimpleFlareTracker` - Flare scraping/storage in `flare_tracker_simple.py`
- `EnhancedCMETracker` - CME tracking in `cme_tracker_enhanced.py`
- `ModelProvider` (ABC) - Base class for AI providers in `model_providers/base.py`
- `ModelConfig` / `ModelResponse` - Data classes for model configuration and responses

## Database Schema

### flare_database.db
Table `flares`: `id`, `event_date`, `event_time`, `event_timestamp`, `flare_class`, `region`, `location`, `peak_time`, `end_time`, `scraped_at`, `source`, `raw_text`

### space_weather.db
Table `cmes_enhanced`: CME basic info with `activity_id`, `start_time`, `source_location`, etc.
Table `cme_analyses`: Leading Edge (LE) and Shock Front (SH) analyses with speed, direction, half_angle
Table `cme_model_runs`: WSA-ENLIL+Cone model predictions with `earth_arrival_time`, Kp estimates
Table `cme_spacecraft_impacts`: Arrival predictions for various spacecraft

## Important Notes

- LMSAL is preferred over NOAA for flare data (more complete with start/peak/end times)
- CME data from NASA DONKI API (no API key required for CCMC endpoint)
- Reports auto-cleanup files older than `max_archive_days` (default 30)
- The `ARCHIVE-original/` directory contains legacy code and is not part of the active system
