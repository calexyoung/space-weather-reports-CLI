#!/usr/bin/env python3
"""
Enhanced CME Tracker - NASA DONKI Integration with Full Analysis Data

Tracks Coronal Mass Ejections (CMEs) from NASA's DONKI database including:
- Multiple analyses per CME (Leading Edge and Shock Front)
- Multiple model runs per analysis with Kp estimates
- Complete arrival predictions for Earth and other spacecraft

Data Source: https://kauai.ccmc.gsfc.nasa.gov/DONKI/
"""

import sqlite3
import requests
import logging
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class EnhancedCMETracker:
    """
    Enhanced CME tracker with complete analysis data

    Features:
    - Fetch CME data from NASA DONKI M2M catalog
    - Parse multiple analyses per CME (Leading Edge + Shock Front)
    - Store model runs with arrival times and Kp estimates
    - Query CMEs by occurrence time and arrival time windows
    - Export complete CME data for reports
    """

    def __init__(self, db_path: str = 'space_weather.db'):
        """
        Initialize enhanced CME tracker

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with enhanced CME tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main CME table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cmes_enhanced (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Primary identifiers
                activity_id TEXT UNIQUE NOT NULL,
                catalog TEXT DEFAULT 'M2M_CATALOG',

                -- Timing
                start_time TEXT NOT NULL,
                start_timestamp INTEGER NOT NULL,

                -- Source information
                source_location TEXT,
                source_region TEXT,
                associated_flare TEXT,

                -- Basic CME info
                note TEXT,
                instruments TEXT,

                -- Links
                donki_url TEXT,

                -- Metadata
                created_at INTEGER NOT NULL,
                updated_at INTEGER,

                UNIQUE(activity_id)
            )
        ''')

        # CME Analysis table (for LE and SH analyses)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cme_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Foreign key to main CME
                cme_id INTEGER NOT NULL,
                activity_id TEXT NOT NULL,

                -- Analysis identifiers
                analysis_id INTEGER NOT NULL,
                analysis_url TEXT,
                analysis_type TEXT, -- 'LE' (Leading Edge) or 'SH' (Shock Front)

                -- Measurement details
                measurement_time TEXT,
                measurement_timestamp INTEGER,
                technique TEXT,
                data_level INTEGER,

                -- Physical parameters
                speed REAL,
                type TEXT,
                direction_lon REAL,
                direction_lat REAL,
                half_angle REAL,
                time_at_21_5_rs TEXT,

                -- Instruments
                instruments TEXT,
                image_type TEXT,

                -- Analysis metadata
                submitted_by TEXT,
                submission_time TEXT,

                -- Metadata
                created_at INTEGER NOT NULL,
                updated_at INTEGER,

                FOREIGN KEY (cme_id) REFERENCES cmes_enhanced(id),
                UNIQUE(activity_id, analysis_id, analysis_type)
            )
        ''')

        # Model runs table (for WSA-ENLIL+Cone results)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cme_model_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Foreign key to analysis
                analysis_id INTEGER NOT NULL,
                activity_id TEXT NOT NULL,

                -- Model run details
                run_number INTEGER,
                model_completion_time TEXT,
                model_completion_timestamp INTEGER,

                -- Earth arrival prediction
                earth_arrival_time TEXT,
                earth_arrival_timestamp INTEGER,
                impact_duration REAL,
                rmin_earth_radii REAL,

                -- Kp estimates (at different angles)
                kp_90 INTEGER,
                kp_135 INTEGER,
                kp_180 INTEGER,

                -- Metadata
                created_at INTEGER NOT NULL,

                FOREIGN KEY (analysis_id) REFERENCES cme_analyses(id),
                UNIQUE(analysis_id, run_number)
            )
        ''')

        # Spacecraft impacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cme_spacecraft_impacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Foreign key to model run
                model_run_id INTEGER NOT NULL,
                analysis_id INTEGER NOT NULL,
                activity_id TEXT NOT NULL,

                -- Spacecraft details
                spacecraft_name TEXT NOT NULL,
                arrival_time TEXT,
                arrival_timestamp INTEGER,

                -- Metadata
                created_at INTEGER NOT NULL,

                FOREIGN KEY (model_run_id) REFERENCES cme_model_runs(id)
            )
        ''')

        # Create indexes for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cme_start_ts ON cmes_enhanced(start_timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cme_activity ON cmes_enhanced(activity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_cme ON cme_analyses(cme_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_activity ON cme_analyses(activity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_analysis ON cme_model_runs(analysis_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_arrival ON cme_model_runs(earth_arrival_timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_spacecraft_model ON cme_spacecraft_impacts(model_run_id)')

        conn.commit()
        conn.close()

        self.logger.info(f"Enhanced CME database initialized at {self.db_path}")

    def fetch_cmes_from_api(self, start_date: str, end_date: str, api_key: str = None) -> List[Dict]:
        """
        Fetch CME data from NASA DONKI API (CCMC direct endpoint)

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            api_key: Deprecated - no longer needed (kept for compatibility)

        Returns:
            List of CME dictionaries from DONKI API
        """
        try:
            # Use CCMC direct endpoint (no API key required, more current data)
            url = "https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/CME"
            params = {
                'startDate': start_date,
                'endDate': end_date
            }

            self.logger.info(f"Fetching CMEs from DONKI API: {start_date} to {end_date}")

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            cmes = response.json()
            self.logger.info(f"Fetched {len(cmes)} CMEs from DONKI API")

            return cmes

        except requests.Timeout:
            self.logger.error("DONKI API timeout")
            return []
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch CMEs from API: {e}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from DONKI: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error fetching CMEs: {e}", exc_info=True)
            return []

    def store_cme(self, cme_data: Dict) -> Optional[int]:
        """
        Store CME data from DONKI API into database

        Args:
            cme_data: CME dictionary from DONKI API

        Returns:
            Database ID of stored CME, or None if storage failed
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            activity_id = cme_data['activityID']
            start_time = cme_data['startTime']
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            start_timestamp = int(start_dt.timestamp())

            # Extract basic CME info
            source_location = cme_data.get('sourceLocation', '')
            source_region = str(cme_data.get('activeRegionNum', '')) if cme_data.get('activeRegionNum') else None
            instruments = ', '.join([inst['displayName'] for inst in cme_data.get('instruments', [])])
            note = cme_data.get('note', '')
            donki_url = cme_data.get('link', '')

            # Extract associated flare
            associated_flare = None
            if 'linkedEvents' in cme_data and cme_data['linkedEvents']:
                flare_events = [e['activityID'] for e in cme_data['linkedEvents'] if 'FLR' in e['activityID']]
                if flare_events:
                    associated_flare = flare_events[0]

            created_at = int(datetime.now(timezone.utc).timestamp())

            # Insert or update CME
            cursor.execute('''
                INSERT OR REPLACE INTO cmes_enhanced
                (activity_id, start_time, start_timestamp, source_location, source_region,
                 associated_flare, note, instruments, donki_url, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (activity_id, start_time, start_timestamp, source_location, source_region,
                  associated_flare, note, instruments, donki_url, created_at, created_at))

            cme_id = cursor.lastrowid

            # Store analyses
            if 'cmeAnalyses' in cme_data:
                for analysis in cme_data['cmeAnalyses']:
                    self._store_analysis(cursor, cme_id, activity_id, analysis)

            conn.commit()
            conn.close()

            self.logger.info(f"Stored CME {activity_id} with ID {cme_id}")
            return cme_id

        except Exception as e:
            self.logger.error(f"Failed to store CME {activity_id}: {e}", exc_info=True)
            return None

    def _store_analysis(self, cursor, cme_id: int, activity_id: str, analysis: Dict):
        """Store CME analysis (LE or SH) from API data"""
        try:
            # Extract analysis details
            analysis_type = analysis.get('featureCode', 'LE')  # 'LE' or 'SH'
            measurement_time = analysis.get('time21_5', '')
            measurement_timestamp = None
            if measurement_time:
                measurement_dt = datetime.fromisoformat(measurement_time.replace('Z', '+00:00'))
                measurement_timestamp = int(measurement_dt.timestamp())

            technique = analysis.get('measurementTechnique', '')
            data_level = analysis.get('levelOfData', 0)
            speed = analysis.get('speed')
            cme_type = analysis.get('type', '')
            direction_lon = analysis.get('longitude')
            direction_lat = analysis.get('latitude')
            half_angle = analysis.get('halfAngle')
            time_at_21_5_rs = analysis.get('time21_5', '')
            image_type = analysis.get('imageType', '')
            note = analysis.get('note', '')

            created_at = int(datetime.now(timezone.utc).timestamp())

            # Generate a unique analysis ID (use hash of key parameters)
            analysis_id = abs(hash(f"{activity_id}_{analysis_type}_{measurement_time}")) % 1000000

            # Insert or update analysis
            cursor.execute('''
                INSERT OR REPLACE INTO cme_analyses
                (cme_id, activity_id, analysis_id, analysis_type, measurement_time, measurement_timestamp,
                 technique, data_level, speed, type, direction_lon, direction_lat, half_angle,
                 time_at_21_5_rs, image_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cme_id, activity_id, analysis_id, analysis_type, measurement_time, measurement_timestamp,
                  technique, data_level, speed, cme_type, direction_lon, direction_lat, half_angle,
                  time_at_21_5_rs, image_type, created_at, created_at))

            analysis_db_id = cursor.lastrowid

            # Store ENLIL model runs
            if 'enlilList' in analysis and analysis['enlilList']:
                for run_num, enlil in enumerate(analysis['enlilList'], 1):
                    self._store_model_run(cursor, analysis_db_id, activity_id, run_num, enlil)

        except Exception as e:
            self.logger.error(f"Failed to store analysis: {e}", exc_info=True)

    def _store_model_run(self, cursor, analysis_id: int, activity_id: str, run_number: int, enlil: Dict):
        """Store WSA-ENLIL+Cone model run from API data"""
        try:
            model_completion_time = enlil.get('modelCompletionTime', '')
            model_completion_timestamp = None
            if model_completion_time:
                completion_dt = datetime.fromisoformat(model_completion_time.replace('Z', '+00:00'))
                model_completion_timestamp = int(completion_dt.timestamp())

            earth_arrival_time = enlil.get('estimatedShockArrivalTime')
            earth_arrival_timestamp = None
            if earth_arrival_time:
                arrival_dt = datetime.fromisoformat(earth_arrival_time.replace('Z', '+00:00'))
                earth_arrival_timestamp = int(arrival_dt.timestamp())

            impact_duration = enlil.get('estimatedDuration')
            rmin_earth_radii = enlil.get('rmin_re')
            kp_90 = enlil.get('kp_90')
            kp_135 = enlil.get('kp_135')
            kp_180 = enlil.get('kp_180')

            created_at = int(datetime.now(timezone.utc).timestamp())

            # Insert model run
            cursor.execute('''
                INSERT OR REPLACE INTO cme_model_runs
                (analysis_id, activity_id, run_number, model_completion_time, model_completion_timestamp,
                 earth_arrival_time, earth_arrival_timestamp, impact_duration, rmin_earth_radii,
                 kp_90, kp_135, kp_180, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (analysis_id, activity_id, run_number, model_completion_time, model_completion_timestamp,
                  earth_arrival_time, earth_arrival_timestamp, impact_duration, rmin_earth_radii,
                  kp_90, kp_135, kp_180, created_at))

            model_run_id = cursor.lastrowid

            # Store spacecraft impacts
            if 'impactList' in enlil and enlil['impactList']:
                for impact in enlil['impactList']:
                    self._store_spacecraft_impact(cursor, model_run_id, analysis_id, activity_id, impact)

        except Exception as e:
            self.logger.error(f"Failed to store model run: {e}", exc_info=True)

    def _store_spacecraft_impact(self, cursor, model_run_id: int, analysis_id: int,
                                 activity_id: str, impact: Dict):
        """Store spacecraft impact prediction from API data"""
        try:
            spacecraft_name = impact.get('location', '')
            arrival_time = impact.get('arrivalTime')
            arrival_timestamp = None
            if arrival_time:
                arrival_dt = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
                arrival_timestamp = int(arrival_dt.timestamp())

            created_at = int(datetime.now(timezone.utc).timestamp())

            cursor.execute('''
                INSERT OR REPLACE INTO cme_spacecraft_impacts
                (model_run_id, analysis_id, activity_id, spacecraft_name, arrival_time, arrival_timestamp, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (model_run_id, analysis_id, activity_id, spacecraft_name, arrival_time, arrival_timestamp, created_at))

        except Exception as e:
            self.logger.error(f"Failed to store spacecraft impact: {e}", exc_info=True)

    def sync_cmes(self, start_date: str, end_date: str, api_key: str = None) -> int:
        """
        Fetch and store all CMEs for the specified date range

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            api_key: NASA API key (optional)

        Returns:
            Number of CMEs stored
        """
        try:
            cmes = self.fetch_cmes_from_api(start_date, end_date, api_key)

            stored_count = 0
            for cme in cmes:
                if self.store_cme(cme):
                    stored_count += 1

            self.logger.info(f"Synced {stored_count}/{len(cmes)} CMEs to database")
            return stored_count

        except Exception as e:
            self.logger.error(f"Failed to sync CMEs: {e}", exc_info=True)
            return 0

    def get_cmes_for_period(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        Get CMEs that occurred during the specified period

        Args:
            start_time: Start of period (UTC datetime)
            end_time: End of period (UTC datetime)

        Returns:
            List of CME dictionaries with all analyses
        """
        try:
            start_ts = int(start_time.timestamp())
            end_ts = int(end_time.timestamp())

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM cmes_enhanced
                WHERE start_timestamp >= ? AND start_timestamp <= ?
                ORDER BY start_timestamp DESC
            ''', (start_ts, end_ts))

            cmes = [dict(row) for row in cursor.fetchall()]

            # Fetch analyses for each CME
            for cme in cmes:
                cme['analyses'] = self._get_analyses_for_cme(cursor, cme['id'])

            conn.close()

            self.logger.info(f"Retrieved {len(cmes)} CMEs for period")
            return cmes

        except Exception as e:
            self.logger.error(f"Failed to get CMEs for period: {e}", exc_info=True)
            return []

    def get_cmes_with_arrivals_in_window(self, window_start: datetime, window_end: datetime,
                                         uncertainty_hours: int = 7) -> List[Dict]:
        """
        Get CMEs with predicted Earth arrivals within the specified time window
        Includes ±uncertainty_hours around predicted arrival times

        Args:
            window_start: Start of forecast window (UTC datetime)
            window_end: End of forecast window (UTC datetime)
            uncertainty_hours: Hours of uncertainty to add around predictions (default: ±7)

        Returns:
            List of CME dictionaries with arrival predictions in window
        """
        try:
            # Expand window by uncertainty
            expanded_start = window_start - timedelta(hours=uncertainty_hours)
            expanded_end = window_end + timedelta(hours=uncertainty_hours)

            start_ts = int(expanded_start.timestamp())
            end_ts = int(expanded_end.timestamp())

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Find CMEs with model runs that have Earth arrivals in the window
            cursor.execute('''
                SELECT DISTINCT c.*
                FROM cmes_enhanced c
                JOIN cme_analyses a ON c.id = a.cme_id
                JOIN cme_model_runs m ON a.id = m.analysis_id
                WHERE m.earth_arrival_timestamp >= ? AND m.earth_arrival_timestamp <= ?
                ORDER BY c.start_timestamp DESC
            ''', (start_ts, end_ts))

            cmes = [dict(row) for row in cursor.fetchall()]

            # Fetch analyses for each CME
            for cme in cmes:
                cme['analyses'] = self._get_analyses_for_cme(cursor, cme['id'])

            conn.close()

            self.logger.info(f"Retrieved {len(cmes)} CMEs with arrivals in window")
            return cmes

        except Exception as e:
            self.logger.error(f"Failed to get CMEs with arrivals: {e}", exc_info=True)
            return []

    def _get_analyses_for_cme(self, cursor, cme_id: int) -> List[Dict]:
        """Helper method to get all analyses for a CME"""
        cursor.execute('''
            SELECT * FROM cme_analyses
            WHERE cme_id = ?
            ORDER BY analysis_type, analysis_id
        ''', (cme_id,))

        analyses = [dict(row) for row in cursor.fetchall()]

        # Get model runs for each analysis
        for analysis in analyses:
            cursor.execute('''
                SELECT * FROM cme_model_runs
                WHERE analysis_id = ?
                ORDER BY run_number
            ''', (analysis['id'],))

            analysis['model_runs'] = [dict(row) for row in cursor.fetchall()]

            # Get spacecraft impacts for each model run
            for model_run in analysis['model_runs']:
                cursor.execute('''
                    SELECT * FROM cme_spacecraft_impacts
                    WHERE model_run_id = ?
                    ORDER BY spacecraft_name
                ''', (model_run['id'],))

                model_run['spacecraft_impacts'] = [dict(row) for row in cursor.fetchall()]

        return analyses


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    tracker = EnhancedCMETracker()
    print("Enhanced CME Tracker initialized")
    print("Database schema created with tables:")
    print("  - cmes_enhanced (main CME data)")
    print("  - cme_analyses (LE and SH analyses)")
    print("  - cme_model_runs (WSA-ENLIL+Cone results)")
    print("  - cme_spacecraft_impacts (arrival predictions)")
