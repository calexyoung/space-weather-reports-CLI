#!/usr/bin/env python3
"""
Scheduler for Space Weather Report Automation
Runs the report generator at specified intervals
"""

import time
import schedule
import yaml
from pathlib import Path
from space_weather_automation import SpaceWeatherReportGenerator
import logging

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.yaml"

def load_config():
    """Load configuration"""
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

def run_report_generation():
    """Run the report generation"""
    print(f"\n{'='*60}")
    print(f"Starting scheduled report generation...")
    print(f"{'='*60}\n")
    
    generator = SpaceWeatherReportGenerator()
    generator.run()
    
    print(f"\n{'='*60}")
    print(f"Scheduled report generation completed")
    print(f"{'='*60}\n")

def main():
    """Main scheduler loop"""
    config = load_config()
    schedule_config = config['schedule']
    
    print("Space Weather Report Scheduler")
    print("="*60)
    print(f"Configuration loaded from: {CONFIG_FILE}")
    
    # Schedule based on configuration
    if schedule_config.get('specific_times'):
        # Schedule at specific times
        for time_str in schedule_config['specific_times']:
            schedule.every().day.at(time_str).do(run_report_generation)
            print(f"Scheduled: Daily at {time_str}")
    else:
        # Schedule at intervals
        interval_hours = schedule_config.get('interval_hours', 6)
        schedule.every(interval_hours).hours.do(run_report_generation)
        print(f"Scheduled: Every {interval_hours} hours")
    
    print("="*60)
    print("\nScheduler is running. Press Ctrl+C to stop.")
    print(f"Next run: {schedule.next_run()}\n")
    
    # Run once immediately
    run_report_generation()
    
    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        print("="*60)

if __name__ == "__main__":
    main()
