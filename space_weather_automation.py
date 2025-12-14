#!/usr/bin/env python3
"""
Space Weather Report Automation Script
Generates automated space weather reports at scheduled intervals
"""

import os
import sys
import json
import yaml
import requests
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
# AI report generation integration
try:
    from ai_report_generator import generate_reports_with_ai
    AI_REPORT_GENERATOR_AVAILABLE = True
except ImportError:
    AI_REPORT_GENERATOR_AVAILABLE = False
    print("⚠️  AI report generator not available")


# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    pass  # python-dotenv not installed, will use system env vars

# Configuration
CONFIG_FILE = "config.yaml"
SCRIPT_DIR = Path(__file__).parent

class SpaceWeatherReportGenerator:
    def __init__(self, config_path=None, model=None, output_suffix=None):
        """Initialize the report generator

        Args:
            config_path: Path to config.yaml file
            model: Model name to use for report generation (e.g., 'gpt-5.1', 'claude-sonnet-4.5')
            output_suffix: Suffix to append to output filenames (e.g., 'openai-gpt-5.1')
        """
        if config_path is None:
            config_path = SCRIPT_DIR / CONFIG_FILE

        self.config = self.load_config(config_path)
        self.model = model
        self.output_suffix = output_suffix
        self.setup_logging()
        self.logger.info("Space Weather Report Generator initialized")
    
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Configure logging"""
        log_config = self.config['logging']
        log_file = SCRIPT_DIR / log_config['file']
        
        handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config['max_size_mb'] * 1024 * 1024,
            backupCount=log_config['backup_count']
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_config['level']))
        self.logger.addHandler(handler)
        
        # Also log to console
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        self.logger.addHandler(console)
    
    def fetch_noaa_discussion(self):
        """Fetch NOAA SWPC discussion text"""
        url = self.config['primary_sources']['noaa_discussion']
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            self.logger.info(f"Successfully fetched NOAA discussion")
            return response.text
        except Exception as e:
            self.logger.error(f"Failed to fetch NOAA discussion: {e}")
            return None
    
    def fetch_uk_met_office(self):
        """Fetch UK Met Office space weather forecast"""
        url = self.config['primary_sources']['uk_met_office']
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            self.logger.info(f"Successfully fetched UK Met Office data")
            return response.text
        except Exception as e:
            self.logger.error(f"Failed to fetch UK Met Office data: {e}")
            return None

    def fetch_sidc_forecast(self):
        """Fetch SIDC (Solar Influences Data analysis Center) forecast"""
        url = self.config['primary_sources']['sidc_forecast']
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            self.logger.info(f"Successfully fetched SIDC forecast")
            return response.text
        except Exception as e:
            self.logger.error(f"Failed to fetch SIDC forecast: {e}")
            return None

    def fetch_alternative_sources(self):
        """Fetch data from alternative sources"""
        results = {}
        for name, url in self.config['alternative_sources'].items():
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                results[name] = response.text
                self.logger.info(f"Successfully fetched {name}")
            except Exception as e:
                self.logger.warning(f"Failed to fetch {name}: {e}")
        return results
    
    def generate_report_data(self):
        """Gather all data needed for report generation"""
        from datetime import timezone

        now = datetime.now(timezone.utc)
        analysis_start = now - timedelta(hours=24)
        forecast_end = now + timedelta(days=3)

        data = {
            'timestamp': now.isoformat(),
            'analysis_period': {
                'start': analysis_start.isoformat(),
                'end': now.isoformat()
            },
            'forecast_period': {
                'start': now.isoformat(),
                'end': forecast_end.isoformat()
            },
            'noaa_discussion': self.fetch_noaa_discussion(),
            'uk_met_office': self.fetch_uk_met_office(),
            'sidc_forecast': self.fetch_sidc_forecast(),
            'alternative_sources': self.fetch_alternative_sources(),
            'flare_summary': self.get_flare_summary(),
            'flares_detailed': self.get_flares_for_report_period(analysis_start, now),
            'cmes_observed': self.get_cmes_for_report_period(analysis_start, now),
            'cmes_predicted': self.get_predicted_cme_arrivals(now, forecast_end)
        }
        return data

    def get_flare_summary(self):
        """Get flare summary from the 24-hour tracking database"""
        try:
            from flare_tracker_simple import SimpleFlareTracker
            tracker = SimpleFlareTracker()
            summary = tracker.get_flares_summary()
            self.logger.info(f"Retrieved flare summary: {summary['total_count']} flares in last 24h")
            return summary
        except Exception as e:
            self.logger.warning(f"Could not retrieve flare summary: {e}")
            return None

    def get_flares_for_report_period(self, start_time=None, end_time=None):
        """
        Get detailed flare data for the report analysis period

        Args:
            start_time: Start of analysis period (datetime object, defaults to 24h ago)
            end_time: End of analysis period (datetime object, defaults to now)

        Returns:
            List of flare dictionaries with all details
        """
        try:
            import sqlite3
            from datetime import timezone

            if start_time is None:
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            if end_time is None:
                end_time = datetime.now(timezone.utc)

            # Convert to timestamps
            start_ts = int(start_time.timestamp())
            end_ts = int(end_time.timestamp())

            # Connect to flare database
            db_path = SCRIPT_DIR / 'flare_database.db'
            if not db_path.exists():
                self.logger.warning("Flare database not found")
                return []

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT flare_class, event_date, event_time, peak_time, end_time, region, location, raw_text, event_timestamp
                FROM flares
                WHERE event_timestamp >= ? AND event_timestamp <= ?
                ORDER BY event_timestamp DESC
            ''', (start_ts, end_ts))

            rows = cursor.fetchall()
            conn.close()

            flares = [dict(row) for row in rows]
            self.logger.info(f"Retrieved {len(flares)} flares for report period")
            return flares

        except Exception as e:
            self.logger.error(f"Failed to get flares for report period: {e}", exc_info=True)
            return []

    def get_cmes_for_report_period(self, start_time=None, end_time=None):
        """
        Get CME data that occurred during the report analysis period
        Uses enhanced CME tracker with complete analysis data

        Args:
            start_time: Start of analysis period (datetime object, defaults to 24h ago)
            end_time: End of analysis period (datetime object, defaults to now)

        Returns:
            List of CME dictionaries with all analyses, model runs, and Kp estimates
        """
        try:
            from datetime import timezone
            from cme_tracker_enhanced import EnhancedCMETracker

            if start_time is None:
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            if end_time is None:
                end_time = datetime.now(timezone.utc)

            # Use enhanced CME tracker
            tracker = EnhancedCMETracker()
            cmes = tracker.get_cmes_for_period(start_time, end_time)

            self.logger.info(f"Retrieved {len(cmes)} CMEs for report period")
            return cmes

        except Exception as e:
            self.logger.error(f"Failed to get CMEs for report period: {e}", exc_info=True)
            return []

    def get_predicted_cme_arrivals(self, start_time=None, end_time=None, uncertainty_hours=7):
        """
        Get CMEs predicted to arrive during the report forecast period
        Uses enhanced CME tracker with ±7 hour uncertainty window

        Args:
            start_time: Start of forecast period (datetime object, defaults to now)
            end_time: End of forecast period (datetime object, defaults to now + 3 days)
            uncertainty_hours: Hours of uncertainty around predictions (default: ±7)

        Returns:
            List of CME dictionaries with arrival predictions including all model runs
        """
        try:
            from datetime import timezone
            from cme_tracker_enhanced import EnhancedCMETracker

            if start_time is None:
                start_time = datetime.now(timezone.utc)
            if end_time is None:
                end_time = datetime.now(timezone.utc) + timedelta(days=3)

            # Use enhanced CME tracker with uncertainty window
            tracker = EnhancedCMETracker()
            arrivals = tracker.get_cmes_with_arrivals_in_window(
                start_time, end_time, uncertainty_hours
            )

            self.logger.info(f"Retrieved {len(arrivals)} predicted CME arrivals for forecast period")
            return arrivals

        except Exception as e:
            self.logger.error(f"Failed to get predicted CME arrivals: {e}", exc_info=True)
            return []
    

    
    def validate_data_quality(self, data):
        """
        Check if we have enough data for a quality report
        """
        issues = []
        
        # Check NOAA discussion (most critical)
        if not data.get('noaa_discussion'):
            issues.append("Missing NOAA SWPC Discussion (primary source)")
        elif len(data['noaa_discussion']) < 500:
            issues.append("NOAA discussion is unusually short")
        
        # Check for key sections in NOAA data
        if data.get('noaa_discussion'):
            noaa_text = data['noaa_discussion'].lower()
            required_sections = ['solar activity', 'solar wind', 'geospace']
            missing = [s for s in required_sections if s not in noaa_text]
            if missing:
                issues.append(f"NOAA data missing sections: {', '.join(missing)}")
        
        # Log data quality status
        if issues:
            self.logger.warning(f"Data quality issues: {'; '.join(issues)}")
            return False, issues
        else:
            self.logger.info("✅ Data quality check passed")
            return True, []

    def call_ai_for_report(self, data):
        """
        Generate report using AI integration
        """
        model_info = f" with model {self.model}" if self.model else ""
        self.logger.info(f"Generating report{model_info}...")

        # Check if AI report generator is available
        if not AI_REPORT_GENERATOR_AVAILABLE:
            self.logger.warning("AI report generator not available, using basic templates")
            return {
                'html': self.generate_html_template(data),
                'markdown': self.generate_markdown_template(data),
                'json': json.dumps(data, indent=2),
                'text': self.generate_text_template(data)
            }

        try:
            # Use AI report generation with optional model override
            self.logger.info(f"Using AI report generation{model_info}")
            reports = generate_reports_with_ai(data, model_name=self.model)
            self.logger.info("Successfully generated report with AI")
            return reports
            
        except Exception as e:
            self.logger.error(f"AI report generation failed: {e}")
            self.logger.info("Falling back to basic templates")
            # Fall back to basic templates
            return {
                'html': self.generate_html_template(data),
                'markdown': self.generate_markdown_template(data),
                'json': json.dumps(data, indent=2),
                'text': self.generate_text_template(data)
            }

    def generate_html_template(self, data):
        """Generate HTML report"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Space Weather Report - {now.strftime('%B %d, %Y')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h3 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        h4 {{ color: #7f8c8d; }}
        strong {{ color: #2c3e50; }}
        ul {{ line-height: 1.6; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .timestamp {{ color: #95a5a6; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="timestamp">Generated: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}</div>
    
    <h3>Sun news {now.strftime('%B %d')}: [Report Title]</h3>
    <h4>(11 UTC {yesterday.strftime('%B %d')} - 11 UTC {now.strftime('%B %d')})</h4>
    
    <strong>Today's top story:</strong> [Generated content will appear here]
    
    <p><em>Note: This is an automated report template. Full report generation requires AI API integration.</em></p>
    
    <h3>Raw Data Sources</h3>
    <ul>
        <li><strong>NOAA Discussion:</strong> {'Available' if data.get('noaa_discussion') else 'Not available'}</li>
        <li><strong>UK Met Office:</strong> {'Available' if data.get('uk_met_office') else 'Not available'}</li>
    </ul>
</body>
</html>"""
        return html
    
    def generate_markdown_template(self, data):
        """Generate Markdown report"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        md = f"""# Space Weather Report - {now.strftime('%B %d, %Y')}

*Generated: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}*

## Sun news {now.strftime('%B %d')}: [Report Title]

**Period:** 11 UTC {yesterday.strftime('%B %d')} → 11 UTC {now.strftime('%B %d')}

### Today's top story
[Generated content will appear here]

*Note: This is an automated report template. Full report generation requires AI API integration.*

### Data Sources Status
- **NOAA Discussion:** {'✓ Available' if data.get('noaa_discussion') else '✗ Not available'}
- **UK Met Office:** {'✓ Available' if data.get('uk_met_office') else '✗ Not available'}
"""
        return md
    
    def generate_text_template(self, data):
        """Generate plain text report"""
        now = datetime.now()
        return f"""SPACE WEATHER REPORT
Generated: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}

[Report content will appear here]

This is an automated report template.
Full report generation requires AI API integration.
"""
    
    def save_report(self, reports, timestamp=None):
        """Save reports in configured formats"""
        if timestamp is None:
            timestamp = datetime.now()

        date_str = timestamp.strftime('%Y-%m-%d')
        time_str = timestamp.strftime('%H%M')
        year_month = timestamp.strftime('%Y-%m')  # e.g., "2025-11"

        # Create year-month subdirectory
        base_dir = Path(self.config['output']['base_directory'])
        output_dir = base_dir / year_month
        output_dir.mkdir(parents=True, exist_ok=True)

        formats = self.config['output']['formats']
        pattern = self.config['output']['filename_pattern']

        saved_files = []

        for format_name, enabled in formats.items():
            if not enabled:
                continue

            if format_name not in reports:
                self.logger.warning(f"Report format {format_name} not available")
                continue

            # Generate filename
            filename = pattern.format(
                date=date_str,
                time=time_str,
                datetime=timestamp.strftime('%Y-%m-%d_%H%M'),
                format=format_name
            )

            # Add output suffix if specified (e.g., "_openai-gpt-5.1")
            if self.output_suffix:
                filename = f"{filename}_{self.output_suffix}"
            
            # Add extension
            ext_map = {
                'html': '.html',
                'markdown': '.md',
                'json': '.json',
                'text': '.txt',
                'pdf': '.pdf'
            }
            filename += ext_map.get(format_name, f'.{format_name}')
            
            filepath = output_dir / filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(reports[format_name])
                saved_files.append(filepath)
                self.logger.info(f"Saved report: {filepath}")
            except Exception as e:
                self.logger.error(f"Failed to save {filepath}: {e}")
        
        return saved_files
    
    def cleanup_old_reports(self):
        """Remove reports older than configured retention period"""
        max_days = self.config['output'].get('max_archive_days', 30)
        if not self.config['output'].get('archive', True):
            return

        base_dir = Path(self.config['output']['base_directory'])
        cutoff = datetime.now() - timedelta(days=max_days)

        deleted_count = 0
        deleted_dirs = 0

        # Check both YYYY-MM subdirectories and legacy files in base directory
        # Legacy files (for backwards compatibility)
        for file in base_dir.glob('space_weather_*'):
            if file.is_file() and datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
                try:
                    file.unlink()
                    deleted_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to delete {file}: {e}")

        # YYYY-MM subdirectories
        for year_month_dir in base_dir.glob('20*-*'):
            if not year_month_dir.is_dir():
                continue

            # Delete old reports in this directory
            for file in year_month_dir.glob('space_weather_*'):
                if file.is_file() and datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
                    try:
                        file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        self.logger.error(f"Failed to delete {file}: {e}")

            # Remove empty directories
            try:
                if year_month_dir.is_dir() and not list(year_month_dir.iterdir()):
                    year_month_dir.rmdir()
                    deleted_dirs += 1
                    self.logger.info(f"Removed empty directory: {year_month_dir.name}")
            except Exception as e:
                self.logger.error(f"Failed to remove directory {year_month_dir}: {e}")

        if deleted_count > 0:
            self.logger.info(f"Cleaned up {deleted_count} old report(s) and {deleted_dirs} empty director(ies)")

    def collect_latest_flares(self):
        """
        Force fresh flare data collection immediately before generating report.
        Ensures the most recent flares (including those from the past few hours) are included.
        """
        try:
            from flare_tracker_simple import SimpleFlareTracker
            self.logger.info("Collecting latest flare data before report generation...")

            tracker = SimpleFlareTracker()
            result = tracker.scrape_and_update()

            if result['success']:
                self.logger.info(
                    f"Pre-report flare collection successful: "
                    f"{result['new_flares']} new flares added, "
                    f"{result['current_total']} total in 24h window"
                )
                if result.get('sources_used'):
                    self.logger.info(f"Flare sources used: {', '.join(result['sources_used'])}")
            else:
                self.logger.warning(f"Pre-report flare collection failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            self.logger.warning(f"Could not collect latest flares: {e}")
            # Don't fail the entire report generation if flare collection fails

    def run(self):
        """Main execution method"""
        try:
            self.logger.info("Starting report generation...")

            # Force fresh flare collection before generating report
            self.collect_latest_flares()

            # Gather data
            data = self.generate_report_data()
            
            # Generate reports
            reports = self.call_ai_for_report(data)
            
            # Save reports
            saved_files = self.save_report(reports)
            
            # Cleanup old reports
            self.cleanup_old_reports()
            
            self.logger.info(f"Successfully generated {len(saved_files)} report(s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}", exc_info=True)
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate automated space weather reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 space_weather_automation.py
  python3 space_weather_automation.py --model gpt-5.1
  python3 space_weather_automation.py --model claude-sonnet-4.5 --output-suffix anthropic-sonnet
  python3 space_weather_automation.py --model gemini-2.5-pro --output-suffix google-gemini

Available models:
  Anthropic: claude-sonnet-4.5, claude-opus-4.5, claude-haiku-3.5
  OpenAI:    gpt-5.1, gpt-5.1-instant, gpt-4o, gpt-4o-mini, o1, o1-mini
  Google:    gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash
        '''
    )
    parser.add_argument(
        '--model', '-m',
        type=str,
        help='Model to use for report generation (e.g., gpt-5.1, claude-sonnet-4.5, gemini-2.5-pro)'
    )
    parser.add_argument(
        '--output-suffix', '-s',
        type=str,
        help='Suffix to append to output filenames (e.g., openai-gpt-5.1)'
    )
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to config file (default: config.yaml)'
    )

    args = parser.parse_args()

    generator = SpaceWeatherReportGenerator(
        config_path=args.config,
        model=args.model,
        output_suffix=args.output_suffix
    )
    success = generator.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
