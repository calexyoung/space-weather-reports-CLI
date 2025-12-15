#!/usr/bin/env python3
"""
Flare Collection Scheduler
Runs flare tracking every 4 hours to maintain comprehensive 24-hour flare database.
This runs independently of the main report generation (which runs every 12-24 hours).
"""

import schedule
import time
import logging
import sys
from datetime import datetime, timezone
from flare_tracker_simple import SimpleFlareTracker


def collect_flares():
    """Run flare collection cycle"""
    try:
        logger = logging.getLogger(__name__)
        logger.info("="*60)
        logger.info(f"Starting flare collection cycle at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

        tracker = SimpleFlareTracker()
        result = tracker.scrape_and_update()

        if result['success']:
            logger.info(f"Flare collection successful:")
            logger.info(f"  - New flares added: {result['new_flares']}")
            logger.info(f"  - Old flares cleaned: {result['deleted_old']}")
            logger.info(f"  - Total in 24h window: {result['current_total']}")

            summary = result['summary']
            logger.info(f"  - X-class: {summary['x_class_count']}, M-class: {summary['m_class_count']}, C-class: {summary['c_class_count']}")

            if summary['strongest_flare']:
                strongest = summary['strongest_flare']
                logger.info(f"  - Strongest: {strongest['flare_class']} from AR{strongest.get('region', '????')}")
        else:
            logger.error(f"Flare collection failed: {result.get('error', 'Unknown error')}")

        logger.info("="*60)

    except Exception as e:
        logging.error(f"Error in flare collection: {e}", exc_info=True)


def main():
    """Main scheduler loop for 4-hour flare collection"""

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('flare_collection.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)

    logger.info("="*60)
    logger.info("Flare Collection Scheduler Starting")
    logger.info("Schedule: Every 4 hours")
    logger.info("="*60)

    # Run immediately on startup
    logger.info("Running initial flare collection...")
    collect_flares()

    # Schedule every 4 hours
    schedule.every(4).hours.do(collect_flares)

    logger.info("Scheduler initialized. Running every 4 hours.")
    logger.info("Press Ctrl+C to stop.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("\nFlare collection scheduler stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
