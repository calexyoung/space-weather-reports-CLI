#!/usr/bin/env python3
"""
Simplified Flare Tracking System
Extracts flare data from NOAA SWPC discussion text which is already being fetched.
Maintains a rolling 24-hour database of solar flares.
Runs every 4 hours to capture all flares during high activity periods.
"""

import sqlite3
import re
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import requests


class SimpleFlareTracker:
    """Tracks solar flares from NOAA SWPC discussion text"""

    def __init__(self, db_path: str = "flare_database.db"):
        """
        Initialize the flare tracker

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date TEXT NOT NULL,
                event_time TEXT,
                event_timestamp INTEGER,
                flare_class TEXT NOT NULL,
                region TEXT,
                location TEXT,
                peak_time TEXT,
                end_time TEXT,
                scraped_at INTEGER NOT NULL,
                source TEXT DEFAULT 'NOAA',
                raw_text TEXT
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_event_timestamp
            ON flares(event_timestamp)
        ''')

        conn.commit()
        conn.close()
        self.logger.info(f"Flare database initialized at {self.db_path}")

    def fetch_noaa_discussion(self) -> Optional[str]:
        """Fetch NOAA SWPC discussion"""
        url = "https://services.swpc.noaa.gov/text/discussion.txt"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            self.logger.info("Successfully fetched NOAA discussion")
            return response.text
        except Exception as e:
            self.logger.error(f"Failed to fetch NOAA discussion: {e}")
            return None

    def fetch_lmsal_flares(self) -> Optional[str]:
        """Fetch LMSAL latest events page"""
        url = "https://www.lmsal.com/solarsoft/last_events/"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            self.logger.info("Successfully fetched LMSAL flares page")
            return response.text
        except Exception as e:
            self.logger.error(f"Failed to fetch LMSAL flares: {e}")
            return None

    def parse_noaa_flares(self, noaa_text: str) -> List[Dict]:
        """
        Extract flare information from NOAA SWPC discussion text

        Args:
            noaa_text: NOAA discussion text

        Returns:
            List of flare dictionaries
        """
        flares = []

        # NOAA format mentions flares like:
        # "M1.0 flare at 0026 UTC on 02 Nov"
        # "C8.2 long-duration flare at 1246 UTC"
        # "X1.5/2B flare from Region 4267"
        # "M7.4 flare occurred at 05/1119 UTC" (DD/HHMM format)

        # Pattern 1: Class + "flare" + time + date (standard format)
        pattern1 = r'([A-Z]\d+\.?\d*)[/-]?\d?[A-Z]?\s+(?:flare|event).*?(?:at\s+)?(\d{4})\s*UTC.*?(?:on\s+)?(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'

        # Pattern 1b: Class + "flare" + DD/HHMM format (compact format)
        pattern1b = r'([A-Z]\d+\.?\d*)[/-]?\d?[A-Z]?\s+(?:flare|event).*?(?:at\s+)?(\d{2})/(\d{4})\s*UTC'

        # Pattern 2: Class + from Region
        pattern2 = r'([A-Z]\d+\.?\d*)[/-]?\d?[A-Z]?\s+(?:flare|event).*?[Rr]egion\s+(\d{4})'

        # Pattern 3: Just class mentions
        pattern3 = r'([CMX]\d+\.?\d*)\s+(?:flare|event)'

        for match in re.finditer(pattern1, noaa_text, re.IGNORECASE):
            flare_class = match.group(1).upper()
            time_str = match.group(2)
            day = int(match.group(3))
            month_str = match.group(4)

            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            month = month_map.get(month_str, datetime.now(timezone.utc).month)
            year = datetime.now(timezone.utc).year

            try:
                hour = int(time_str[:2])
                minute = int(time_str[2:])
                event_dt = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)

                # Extract region if mentioned nearby (search in broader context)
                # Look within the match first
                region_match = re.search(r'[Rr]egion\s+(\d{4})', match.group(0))
                if not region_match:
                    # Look in the 100 characters after the match
                    context_end = min(match.end() + 100, len(noaa_text))
                    context = noaa_text[match.start():context_end]
                    region_match = re.search(r'[Rr]egion\s+(\d{4})', context)
                region = region_match.group(1) if region_match else None

                flare = {
                    'event_date': event_dt.strftime("%Y-%m-%d"),
                    'event_time': event_dt.strftime("%H:%M"),
                    'event_timestamp': int(event_dt.timestamp()),
                    'flare_class': flare_class,
                    'region': region,
                    'location': None,
                    'raw_text': match.group(0)
                }
                flares.append(flare)
            except (ValueError, IndexError) as e:
                self.logger.warning(f"Failed to parse flare: {e}")
                continue

        # Pattern 1b: DD/HHMM format (e.g., "M7.4 flare occurred at 05/1119 UTC")
        for match in re.finditer(pattern1b, noaa_text, re.IGNORECASE):
            flare_class = match.group(1).upper()
            day = int(match.group(2))
            time_str = match.group(3)  # HHMM format

            # Infer month and year from current date
            now = datetime.now(timezone.utc)
            year = now.year
            month = now.month

            # Handle month rollover (if day is in future, must be last month)
            if day > now.day:
                month = month - 1 if month > 1 else 12
                if month == 12:
                    year -= 1

            try:
                hour = int(time_str[:2])
                minute = int(time_str[2:])
                event_dt = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)

                # Extract region if mentioned nearby (search in broader context)
                # Look within the match first
                region_match = re.search(r'[Rr]egion\s+(\d{4})', match.group(0))
                if not region_match:
                    # Look in the 100 characters after the match
                    context_end = min(match.end() + 100, len(noaa_text))
                    context = noaa_text[match.start():context_end]
                    region_match = re.search(r'[Rr]egion\s+(\d{4})', context)
                region = region_match.group(1) if region_match else None

                flare = {
                    'event_date': event_dt.strftime("%Y-%m-%d"),
                    'event_time': event_dt.strftime("%H:%M"),
                    'event_timestamp': int(event_dt.timestamp()),
                    'flare_class': flare_class,
                    'region': region,
                    'location': None,
                    'raw_text': match.group(0)
                }

                # Only add if not already captured by Pattern 1
                if not any(f['flare_class'] == flare_class and f.get('event_timestamp') == flare['event_timestamp'] for f in flares):
                    flares.append(flare)
            except (ValueError, IndexError) as e:
                self.logger.warning(f"Failed to parse compact format flare: {e}")
                continue

        # Also look for region-based mentions without full datetime
        for match in re.finditer(pattern2, noaa_text, re.IGNORECASE):
            flare_class = match.group(1).upper()
            region = match.group(2)

            # Use current date as approximation if no date found
            now = datetime.now(timezone.utc)

            flare = {
                'event_date': now.strftime("%Y-%m-%d"),
                'event_time': None,
                'event_timestamp': int(now.timestamp()),
                'flare_class': flare_class,
                'region': region,
                'location': None,
                'raw_text': match.group(0)
            }

            # Only add if not a duplicate
            # Check against both region match and event_date match (Pattern 1/1b might have captured it)
            is_duplicate = any(
                (f['flare_class'] == flare_class and f.get('region') == region) or
                (f['flare_class'] == flare_class and f.get('event_date') and
                 abs((f.get('event_timestamp', 0) or 0) - (flare['event_timestamp'] or 0)) < 86400)  # Within 24h
                for f in flares
            )
            if not is_duplicate:
                flares.append(flare)

        self.logger.info(f"Extracted {len(flares)} flares from NOAA text")
        return flares

    def parse_lmsal_table(self, html_content: str) -> List[Dict]:
        """
        Parse LMSAL events table

        Table structure can have variations:
        - Simple: <td>N00W60 ( 4267 )</td>
        - With font tags: <td><font color=blue>N25E88</font> ( 4272 )</td>
        - With links: <td><font><a href="..."> N27E87</a> ( 4272 )</font></td>

        Columns: row#, event_id, start_time, end_time, peak_time, class, location/region
        """
        flares = []

        # More flexible regex pattern - captures the location <td> content including HTML
        pattern = r'<tr align=center><td>(\d+)</td>\s*' \
                  r'<td><A HREF="[^"]+">gev_(\d{8})_(\d{4})</A></td>\s*' \
                  r'<td>([\d/]+\s+[\d:]+)</td>\s*' \
                  r'<td>([\d:]+)</td>\s*' \
                  r'<td>([\d:]+)</td>\s*' \
                  r'<td>([A-Z][\d.]+)</td>\s*' \
                  r'<td>(.+?)(?:</td>|<tr)'

        for match in re.finditer(pattern, html_content, re.DOTALL):
            try:
                row_num = match.group(1)
                date_str = match.group(2)  # YYYYMMDD
                time_str = match.group(3)  # HHMM
                start_full = match.group(4)  # YYYY/MM/DD HH:MM:SS
                end_time = match.group(5)  # HH:MM:SS
                peak_time = match.group(6)  # HH:MM:SS
                flare_class = match.group(7)  # C8.2
                location_raw = match.group(8)  # May contain HTML tags

                # Extract region from location (handles both plain and HTML versions)
                region_match = re.search(r'\(\s*(\d{4})\s*\)', location_raw)
                region = region_match.group(1) if region_match else None

                # Extract location coordinates (strip HTML tags first)
                location_text = re.sub(r'<[^>]+>', '', location_raw)  # Remove HTML tags
                loc_match = re.search(r'([NS]\d{2}[EW]\d{2})', location_text)
                location = loc_match.group(1) if loc_match else None

                # Parse datetime from start_full (YYYY/MM/DD HH:MM:SS)
                event_dt = datetime.strptime(start_full, "%Y/%m/%d %H:%M:%S")
                event_dt = event_dt.replace(tzinfo=timezone.utc)

                flare = {
                    'event_date': event_dt.strftime("%Y-%m-%d"),
                    'event_time': event_dt.strftime("%H:%M"),
                    'event_timestamp': int(event_dt.timestamp()),
                    'flare_class': flare_class,
                    'region': region,
                    'location': location,
                    'peak_time': peak_time,
                    'end_time': end_time,
                    'raw_text': f"LMSAL: {flare_class} at {start_full}"
                }
                flares.append(flare)

            except (ValueError, IndexError) as e:
                self.logger.warning(f"Failed to parse LMSAL row {row_num}: {e}")
                continue

        self.logger.info(f"Extracted {len(flares)} flares from LMSAL table")
        return flares

    def store_flares(self, flares: List[Dict], source: str = 'NOAA') -> int:
        """
        Store flares in database

        Also updates existing flares if new region numbers become available.
        Sometimes LMSAL shows flares with only location (e.g., N22E84) but no
        region number initially. When the region is numbered, subsequent fetches
        will include the region number (e.g., AR4274), and this method will
        update the existing record.

        Duplicate Detection Strategy:
        - Matches flares with similar magnitude (within 0.2 tolerance)
        - Prioritizes LMSAL data over NOAA data when merging
        - Uses multiple matching criteria: timestamp, region, location, time window
        """
        if not flares:
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        scraped_at = int(datetime.now(timezone.utc).timestamp())
        new_count = 0
        updated_count = 0

        for flare in flares:
            try:
                # Extract flare magnitude for tolerance matching
                flare_class = flare['flare_class']
                magnitude_match = re.match(r'([A-Z])(\d+\.?\d*)', flare_class)
                if not magnitude_match:
                    # Can't parse magnitude, use exact match only
                    magnitude_min = magnitude_max = None
                else:
                    class_letter = magnitude_match.group(1)
                    magnitude = float(magnitude_match.group(2))
                    magnitude_min = magnitude - 0.2
                    magnitude_max = magnitude + 0.2

                # Check if this flare already exists using multiple criteria
                # Priority: match by event_timestamp and similar flare_class (most reliable)
                # Fallback: match by date, similar class, and region/location

                # Find potential matches with similar magnitude on same date
                if magnitude_min is not None:
                    cursor.execute('''
                        SELECT id, flare_class, region, location, event_time, event_timestamp,
                               peak_time, end_time, source
                        FROM flares
                        WHERE event_date = ?
                        ORDER BY event_timestamp DESC
                    ''', (flare['event_date'],))
                else:
                    # No magnitude parsing, use exact match
                    cursor.execute('''
                        SELECT id, flare_class, region, location, event_time, event_timestamp,
                               peak_time, end_time, source
                        FROM flares
                        WHERE event_date = ? AND flare_class = ?
                    ''', (flare['event_date'], flare_class))

                existing_candidates = cursor.fetchall()
                existing = None

                # Check each candidate for match
                for candidate in existing_candidates:
                    (ex_id, ex_class, ex_region, ex_location, ex_time, ex_timestamp,
                     ex_peak, ex_end, ex_source) = candidate

                    # Check magnitude tolerance
                    if magnitude_min is not None:
                        ex_match = re.match(r'([A-Z])(\d+\.?\d*)', ex_class)
                        if not ex_match or ex_match.group(1) != class_letter:
                            continue
                        ex_magnitude = float(ex_match.group(2))
                        if not (magnitude_min <= ex_magnitude <= magnitude_max):
                            continue

                    # Now check other matching criteria
                    match_found = False

                    # IMPORTANT: NOAA reports peak time, LMSAL reports start/peak/end times
                    # When comparing NOAA data (has event_timestamp) with LMSAL data (has peak_time),
                    # we need to parse LMSAL's peak_time and compare timestamps

                    # Match by start timestamp (within 5 minutes for exact matches)
                    # This catches LMSAL-to-LMSAL duplicates and some NOAA-to-LMSAL matches
                    incoming_ts = flare.get('event_timestamp')
                    if (incoming_ts is not None and ex_timestamp is not None and
                        abs(incoming_ts - ex_timestamp) <= 300):  # 5 minutes
                        match_found = True
                        self.logger.debug(
                            f"Timestamp match: incoming={incoming_ts}, existing={ex_timestamp}, "
                            f"diff={abs(incoming_ts - ex_timestamp)}s"
                        )

                    # Match NOAA time against LMSAL peak_time (NOAA reports peak, not start)
                    if not match_found and (source == 'NOAA' and flare.get('event_timestamp') and
                          ex_source == 'LMSAL' and ex_peak):
                        # Parse LMSAL peak time to timestamp for comparison
                        try:
                            # ex_peak is in HH:MM:SS format, combine with event_date
                            peak_dt_str = f"{flare['event_date']} {ex_peak}"
                            peak_dt = datetime.strptime(peak_dt_str, "%Y-%m-%d %H:%M:%S")
                            peak_dt = peak_dt.replace(tzinfo=timezone.utc)
                            peak_timestamp = int(peak_dt.timestamp())

                            # NOAA time should match LMSAL peak time within 2 minutes
                            if abs(flare['event_timestamp'] - peak_timestamp) <= 120:  # 2 minutes
                                match_found = True
                        except (ValueError, AttributeError):
                            pass

                    # Match LMSAL peak time against NOAA time (reverse case)
                    if not match_found and (source == 'LMSAL' and flare.get('peak_time') and
                          ex_source == 'NOAA' and ex_timestamp):
                        # Parse incoming LMSAL peak time to timestamp for comparison
                        try:
                            # flare['peak_time'] is in HH:MM:SS format, combine with event_date
                            peak_dt_str = f"{flare['event_date']} {flare['peak_time']}"
                            peak_dt = datetime.strptime(peak_dt_str, "%Y-%m-%d %H:%M:%S")
                            peak_dt = peak_dt.replace(tzinfo=timezone.utc)
                            peak_timestamp = int(peak_dt.timestamp())

                            # LMSAL peak time should match NOAA time within 2 minutes
                            if abs(peak_timestamp - ex_timestamp) <= 120:  # 2 minutes
                                match_found = True
                        except (ValueError, AttributeError):
                            pass

                    # Match LMSAL peak times directly (when both are LMSAL)
                    if not match_found and (source == 'LMSAL' and ex_source == 'LMSAL' and
                          flare.get('peak_time') and ex_peak):
                        # Both entries are LMSAL with peak times
                        try:
                            # Parse incoming LMSAL peak time
                            incoming_peak_str = f"{flare['event_date']} {flare['peak_time']}"
                            incoming_peak_dt = datetime.strptime(incoming_peak_str, "%Y-%m-%d %H:%M:%S")
                            incoming_peak_dt = incoming_peak_dt.replace(tzinfo=timezone.utc)
                            incoming_peak_timestamp = int(incoming_peak_dt.timestamp())

                            # Parse existing LMSAL peak time
                            existing_peak_str = f"{flare['event_date']} {ex_peak}"
                            existing_peak_dt = datetime.strptime(existing_peak_str, "%Y-%m-%d %H:%M:%S")
                            existing_peak_dt = existing_peak_dt.replace(tzinfo=timezone.utc)
                            existing_peak_timestamp = int(existing_peak_dt.timestamp())

                            # Match if peak times are within 1 minute
                            if abs(incoming_peak_timestamp - existing_peak_timestamp) <= 60:
                                match_found = True
                        except (ValueError, AttributeError):
                            pass

                    # Match by location and similar start time window (30 minutes)
                    if not match_found and (flare.get('location') and ex_location and
                          flare['location'] == ex_location and
                          flare.get('event_timestamp') and ex_timestamp and
                          abs(flare['event_timestamp'] - ex_timestamp) <= 1800):  # 30 min for location match
                        match_found = True

                    if match_found:
                        existing = candidate
                        break

                if existing:
                    # Flare already exists - check if we should update it with better data
                    (ex_id, ex_class, ex_region, ex_location, ex_time, ex_timestamp,
                     ex_peak, ex_end, ex_source) = existing

                    # Update if incoming flare has more complete data
                    # PRIORITIZE LMSAL DATA OVER NOAA DATA
                    should_update = False
                    updates = {}

                    # If incoming is LMSAL and existing is NOAA, prefer LMSAL values
                    prefer_incoming = (source == 'LMSAL' and ex_source == 'NOAA')

                    # Update flare_class if incoming is LMSAL (more accurate magnitude)
                    if prefer_incoming and flare['flare_class'] != ex_class:
                        updates['flare_class'] = flare['flare_class']
                        should_update = True

                    # Update region if we have one and existing doesn't, or if we prefer incoming
                    if flare.get('region') and (not ex_region or prefer_incoming):
                        updates['region'] = flare['region']
                        should_update = True

                    # Update location if we have one and existing doesn't, or if we prefer incoming
                    if flare.get('location') and (not ex_location or prefer_incoming):
                        updates['location'] = flare['location']
                        should_update = True

                    # Update times if we have them and existing doesn't, or if we prefer incoming
                    # LMSAL data is more complete with start/peak/end times
                    if flare.get('event_time') and (not ex_time or prefer_incoming):
                        updates['event_time'] = flare['event_time']
                        if flare.get('event_timestamp'):
                            updates['event_timestamp'] = flare['event_timestamp']
                        should_update = True

                    if flare.get('peak_time') and (not ex_peak or prefer_incoming):
                        updates['peak_time'] = flare['peak_time']
                        should_update = True

                    if flare.get('end_time') and (not ex_end or prefer_incoming):
                        updates['end_time'] = flare['end_time']
                        should_update = True

                    # Update source if we're preferring incoming
                    if prefer_incoming:
                        updates['source'] = source
                        should_update = True

                    if should_update:
                        # Build UPDATE query dynamically
                        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
                        set_clause += ', scraped_at = ?'
                        values = list(updates.values()) + [scraped_at, ex_id]

                        cursor.execute(f'''
                            UPDATE flares
                            SET {set_clause}
                            WHERE id = ?
                        ''', values)

                        updated_count += 1
                        self.logger.info(
                            f"Updated {flare['flare_class']} on {flare['event_date']} "
                            f"(was {ex_class} from {ex_source}) with better data from {source}"
                        )
                    else:
                        # Flare exists but no updates needed - this is an exact duplicate
                        self.logger.debug(
                            f"Skipped duplicate {flare['flare_class']} on {flare['event_date']} "
                            f"at {flare.get('event_time')} (already in database from {ex_source})"
                        )

                else:
                    # New flare - insert it
                    cursor.execute('''
                        INSERT INTO flares
                        (event_date, event_time, event_timestamp, flare_class, region,
                         location, peak_time, end_time, scraped_at, source, raw_text)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        flare['event_date'],
                        flare.get('event_time'),
                        flare.get('event_timestamp'),
                        flare['flare_class'],
                        flare.get('region'),
                        flare.get('location'),
                        flare.get('peak_time'),
                        flare.get('end_time'),
                        scraped_at,
                        source,
                        flare.get('raw_text', '')
                    ))
                    new_count += 1

            except sqlite3.Error as e:
                self.logger.warning(f"Database error storing flare: {e}")
                continue

        conn.commit()
        conn.close()

        if updated_count > 0:
            self.logger.info(f"Updated {updated_count} flare(s) with new region numbers")
        self.logger.info(f"Stored {new_count} new flares from {source}")

        return new_count

    def cleanup_old_flares(self, hours: int = 24) -> int:
        """Remove flares older than specified hours"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_timestamp = int(cutoff.timestamp())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM flares
            WHERE event_timestamp < ? AND event_timestamp IS NOT NULL
        ''', (cutoff_timestamp,))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        self.logger.info(f"Cleaned up {deleted} old flares")
        return deleted

    def get_flares_last_24h(self) -> List[Dict]:
        """Get all flares from the last 24 hours"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        cutoff_timestamp = int(cutoff.timestamp())

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT event_date, event_time, flare_class, region, location, raw_text
            FROM flares
            WHERE event_timestamp >= ? OR event_timestamp IS NULL
            ORDER BY event_timestamp DESC NULLS LAST
        ''', (cutoff_timestamp,))

        rows = cursor.fetchall()
        conn.close()

        flares = [dict(row) for row in rows]
        self.logger.info(f"Retrieved {len(flares)} flares from last 24 hours")
        return flares

    def get_flares_summary(self) -> Dict:
        """Get summary statistics"""
        flares = self.get_flares_last_24h()

        if not flares:
            return {
                'total_count': 0,
                'x_class_count': 0,
                'm_class_count': 0,
                'c_class_count': 0,
                'strongest_flare': None,
                'flares_list': []
            }

        x_count = sum(1 for f in flares if f['flare_class'].startswith('X'))
        m_count = sum(1 for f in flares if f['flare_class'].startswith('M'))
        c_count = sum(1 for f in flares if f['flare_class'].startswith('C'))

        def flare_strength(flare_class):
            if flare_class.startswith('X'):
                return 1000 + float(re.sub(r'[^0-9.]', '', flare_class[1:]) or '0')
            elif flare_class.startswith('M'):
                return 100 + float(re.sub(r'[^0-9.]', '', flare_class[1:]) or '0')
            elif flare_class.startswith('C'):
                return 10 + float(re.sub(r'[^0-9.]', '', flare_class[1:]) or '0')
            else:
                return 0

        strongest = max(flares, key=lambda f: flare_strength(f['flare_class'])) if flares else None

        return {
            'total_count': len(flares),
            'x_class_count': x_count,
            'm_class_count': m_count,
            'c_class_count': c_count,
            'strongest_flare': strongest,
            'flares_list': flares
        }

    def generate_lmsal_link(self, event_date: str, event_time: str, peak_time: str = None) -> str:
        """
        Generate LMSAL event archive link

        Args:
            event_date: Date in YYYY-MM-DD format
            event_time: Start time in HH:MM format
            peak_time: Peak time in HH:MM:SS format (optional, used if event_time not available)

        Returns:
            LMSAL archive URL or empty string if cannot generate
        """
        try:
            # Parse date components
            year, month, day = event_date.split('-')

            # Use event_time if available, otherwise try peak_time
            if event_time:
                time_parts = event_time.split(':')
                hour = time_parts[0]
                minute = time_parts[1]
            elif peak_time:
                time_parts = peak_time.split(':')
                hour = time_parts[0]
                minute = time_parts[1]
            else:
                return ""

            # Format: gev_YYYYMMDD_HHMM
            event_id = f"gev_{year}{month}{day}_{hour}{minute}"

            # Build URL
            url = f"http://www.lmsal.com/solarsoft/latest_events_archive/events_summary/{year}/{month}/{day}/{event_id}/index.html"
            return url
        except:
            return ""

    def export_monthly_flares_csv(self, year_month: str, output_dir: str = "reports") -> Optional[str]:
        """
        Export flares for a specific month to CSV file

        Note: Active Region column may be empty if the region has not been
        numbered yet by NOAA. These will be updated in subsequent scrapes
        when region numbers become available.

        Args:
            year_month: Month in YYYY-MM format
            output_dir: Base output directory

        Returns:
            Path to created CSV file or None if no flares
        """
        from pathlib import Path
        import csv

        # Get flares for the month
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT event_date, event_time, flare_class, region, location,
                   peak_time, end_time, source
            FROM flares
            WHERE event_date LIKE ?
            ORDER BY event_date, event_time
        ''', (f"{year_month}%",))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.logger.info(f"No flares found for {year_month}")
            return None

        # Create output directory
        output_path = Path(output_dir) / year_month
        output_path.mkdir(parents=True, exist_ok=True)

        # Create CSV file
        csv_file = output_path / f"flares-{year_month}.csv"

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                '#', 'LMSAL Link', 'Flare Class', 'Date',
                'Start Time', 'Peak Time', 'End Time', 'Position', 'Active Region'
            ])

            # Data rows
            for idx, row in enumerate(rows, start=1):
                lmsal_link = self.generate_lmsal_link(
                    row['event_date'],
                    row['event_time'],
                    row['peak_time']
                )

                writer.writerow([
                    idx,
                    lmsal_link,
                    row['flare_class'],
                    row['event_date'],
                    row['event_time'] or '',
                    row['peak_time'] or '',
                    row['end_time'] or '',
                    row['location'] or '',
                    f"AR{row['region']}" if row['region'] else ''
                ])

        self.logger.info(f"Exported {len(rows)} flares to {csv_file}")
        return str(csv_file)

    def export_monthly_flares_markdown(self, year_month: str, output_dir: str = "reports") -> Optional[str]:
        """
        Export flares for a specific month to Markdown table

        Note: Active Region column may be empty if the region has not been
        numbered yet by NOAA. These will be updated in subsequent scrapes
        when region numbers become available.

        Args:
            year_month: Month in YYYY-MM format
            output_dir: Base output directory

        Returns:
            Path to created Markdown file or None if no flares
        """
        from pathlib import Path

        # Get flares for the month
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT event_date, event_time, flare_class, region, location,
                   peak_time, end_time, source
            FROM flares
            WHERE event_date LIKE ?
            ORDER BY event_date, event_time
        ''', (f"{year_month}%",))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return None

        # Create output directory
        output_path = Path(output_dir) / year_month
        output_path.mkdir(parents=True, exist_ok=True)

        # Create Markdown file
        md_file = output_path / f"flares-{year_month}.md"

        with open(md_file, 'w', encoding='utf-8') as f:
            # Title
            year, month = year_month.split('-')
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            month_name = month_names[int(month)]

            f.write(f"# Solar Flares - {month_name} {year}\n\n")
            f.write(f"Total flares recorded: **{len(rows)}**\n\n")

            # Table header
            f.write("| # | LMSAL Link | Flare Class | Date | Start Time | Peak Time | End Time | Position | Active Region |\n")
            f.write("|---|------------|-------------|------|------------|-----------|----------|----------|---------------|\n")

            # Data rows
            for idx, row in enumerate(rows, start=1):
                lmsal_link = self.generate_lmsal_link(
                    row['event_date'],
                    row['event_time'],
                    row['peak_time']
                )

                # Format link as markdown if available
                link_cell = f"[Link]({lmsal_link})" if lmsal_link else ""
                region_cell = f"AR{row['region']}" if row['region'] else ""

                f.write(f"| {idx} | {link_cell} | {row['flare_class']} | {row['event_date']} | "
                       f"{row['event_time'] or ''} | {row['peak_time'] or ''} | {row['end_time'] or ''} | "
                       f"{row['location'] or ''} | {region_cell} |\n")

        self.logger.info(f"Exported {len(rows)} flares to {md_file}")
        return str(md_file)

    def scrape_and_update(self) -> Dict:
        """Complete scraping workflow - uses LMSAL as primary, NOAA as fallback"""
        self.logger.info("Starting flare scraping cycle")

        total_new_flares = 0
        sources_used = []

        # Try LMSAL first (comprehensive flare table)
        lmsal_html = self.fetch_lmsal_flares()
        if lmsal_html:
            lmsal_flares = self.parse_lmsal_table(lmsal_html)
            if lmsal_flares:
                new_count = self.store_flares(lmsal_flares, source='LMSAL')
                total_new_flares += new_count
                sources_used.append('LMSAL')
                self.logger.info(f"LMSAL: {new_count} new flares added")
            else:
                self.logger.warning("LMSAL: No flares extracted from HTML")
        else:
            self.logger.warning("LMSAL fetch failed, will use NOAA as fallback")

        # Also check NOAA for cross-reference
        noaa_text = self.fetch_noaa_discussion()
        if noaa_text:
            noaa_flares = self.parse_noaa_flares(noaa_text)
            if noaa_flares:
                new_count = self.store_flares(noaa_flares, source='NOAA')
                total_new_flares += new_count
                sources_used.append('NOAA')
                self.logger.info(f"NOAA: {new_count} new flares added")

        if not sources_used:
            return {'success': False, 'error': 'Failed to fetch data from any source'}

        deleted = self.cleanup_old_flares(hours=24)
        summary = self.get_flares_summary()

        # Export monthly flare files (CSV and Markdown)
        year_month = datetime.now(timezone.utc).strftime('%Y-%m')
        csv_file = self.export_monthly_flares_csv(year_month)
        md_file = self.export_monthly_flares_markdown(year_month)

        return {
            'success': True,
            'new_flares': total_new_flares,
            'deleted_old': deleted,
            'current_total': summary['total_count'],
            'sources_used': sources_used,
            'summary': summary,
            'monthly_csv': csv_file,
            'monthly_md': md_file
        }


def main():
    """Test the flare tracker"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    tracker = SimpleFlareTracker()
    result = tracker.scrape_and_update()

    print("\nFlare Scraping Results:")
    print(f"Success: {result['success']}")
    print(f"New flares: {result.get('new_flares', 0)}")
    print(f"Old flares deleted: {result.get('deleted_old', 0)}")
    print(f"Current 24h total: {result.get('current_total', 0)}")

    if 'summary' in result:
        s = result['summary']
        print(f"\nSummary (Last 24h):")
        print(f"  X-class: {s['x_class_count']}")
        print(f"  M-class: {s['m_class_count']}")
        print(f"  C-class: {s['c_class_count']}")
        if s['strongest_flare']:
            print(f"  Strongest: {s['strongest_flare']['flare_class']}")

        print(f"\nAll flares:")
        for f in s['flares_list'][:10]:
            print(f"  {f['flare_class']} - {f['event_date']} {f['event_time']} - AR{f['region'] or '????'}")


if __name__ == "__main__":
    main()
