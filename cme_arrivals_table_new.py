    @staticmethod
    def generate_cme_arrivals_html_table(arrivals: list) -> str:
        """
        Generate HTML table of predicted CME arrivals grouped by CME event
        Updated to show CME-level organization with associated flares

        Each CME may have multiple analyses (LE=Leading Edge, SH=Shock), and each
        analysis may have multiple model runs predicting arrivals at different targets.

        Args:
            arrivals: List of CME dictionaries from enhanced tracker with arrival predictions

        Returns:
            HTML string with organized CME arrival predictions
        """
        if not arrivals or len(arrivals) == 0:
            return """<div style="padding: 10px; background-color: #e8f5e9; border-radius: 5px;">
<p><em>No CME arrivals predicted for the forecast period.</em></p>
</div>"""

        html = """
<h3>Predicted CME Arrivals - Forecast Period</h3>
<p style="font-size: 0.9em; color: #555; margin-bottom: 15px;">
Each CME may have multiple analysis types (LE=Leading Edge, SH=Shock) with multiple model runs per target.
</p>
"""

        cme_num = 0
        total_earth_arrivals = 0
        total_spacecraft_arrivals = 0

        for cme in arrivals:
            cme_num += 1
            start_time = cme.get('start_time', '')
            activity_id = cme.get('activity_id', '')
            donki_url = cme.get('donki_url', '')
            associated_flare = cme.get('associated_flare', '')

            # Count arrivals for this CME
            analyses = cme.get('analyses', [])
            cme_earth_count = 0
            cme_spacecraft_count = 0

            for analysis in analyses:
                model_runs = analysis.get('model_runs', [])
                for mr in model_runs:
                    if mr.get('earth_arrival_timestamp'):
                        cme_earth_count += 1
                    spacecraft_impacts = mr.get('spacecraft_impacts', [])
                    for impact in spacecraft_impacts:
                        if impact.get('spacecraft_name', '').lower() != 'earth':
                            cme_spacecraft_count += 1

            total_earth_arrivals += cme_earth_count
            total_spacecraft_arrivals += cme_spacecraft_count

            # CME header section
            html += f"""
<div style="margin-bottom: 20px; border: 2px solid #2c3e50; border-radius: 8px; overflow: hidden;">
  <div style="background-color: #34495e; color: white; padding: 12px;">
    <h4 style="margin: 0; font-size: 1.1em;">CME #{cme_num}: {activity_id}</h4>
    <p style="margin: 5px 0 0 0; font-size: 0.9em;">
      Start: {start_time}"""

            if associated_flare:
                html += f""" | <strong>Associated Flare: {associated_flare}</strong>"""

            html += f"""
      | <a href="{donki_url}" target="_blank" rel="noopener" style="color: #3498db;">NASA DONKI Alert</a>
    </p>
  </div>
"""

            # Analysis sections
            for analysis_idx, analysis in enumerate(analyses):
                analysis_type = analysis.get('analysis_type', 'LE')
                speed = analysis.get('speed')
                speed_str = f"{int(speed)} km/s" if speed else "Unknown"

                model_runs = analysis.get('model_runs', [])

                # Count Earth and spacecraft arrivals for this analysis
                earth_runs = [mr for mr in model_runs if mr.get('earth_arrival_timestamp')]
                spacecraft_runs = []
                for mr in model_runs:
                    for impact in mr.get('spacecraft_impacts', []):
                        if impact.get('spacecraft_name', '').lower() != 'earth':
                            spacecraft_runs.append((mr, impact))

                total_predictions = len(earth_runs) + len(spacecraft_runs)

                if total_predictions == 0:
                    continue  # Skip analyses with no predictions

                # Analysis header
                bg_color = "#3498db" if analysis_type == "LE" else "#e67e22"
                html += f"""
  <div style="background-color: {bg_color}; color: white; padding: 8px 12px; font-weight: bold;">
    {analysis_type} Analysis: {speed_str} | {total_predictions} arrival prediction(s)
  </div>
  <table style="width: 100%; border-collapse: collapse;">
    <thead>
      <tr style="background-color: #ecf0f1;">
        <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Run #</th>
        <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Target</th>
        <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Predicted Arrival</th>
        <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Kp Est.</th>
        <th style="padding: 8px; border: 1px solid #bdc3c7; text-align: left;">Details</th>
      </tr>
    </thead>
    <tbody>
"""

                # Earth arrivals
                for mr in earth_runs:
                    run_num = mr.get('run_number', '—')
                    arrival_time = mr.get('earth_arrival_time', '—')

                    # Kp estimates
                    kp_90 = mr.get('kp_90')
                    kp_135 = mr.get('kp_135')
                    kp_180 = mr.get('kp_180')

                    if kp_90 and kp_180:
                        kp_str = f"{kp_90}-{kp_180}"
                    elif kp_90:
                        kp_str = str(kp_90)
                    else:
                        kp_str = "—"

                    # Additional details
                    details = []
                    if kp_90 and kp_135 and kp_180:
                        details.append(f"Kp 90°={kp_90}, 135°={kp_135}, 180°={kp_180}")
                    rmin = mr.get('rmin_earth_radii')
                    if rmin:
                        details.append(f"Rmin={rmin} RE")
                    details_str = " | ".join(details) if details else "—"

                    html += f"""      <tr style="background-color: #ffe6e6;">
        <td style="padding: 8px; border: 1px solid #bdc3c7;">{run_num}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7; font-weight: bold;">Earth</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7; font-weight: bold;">{arrival_time}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7;">{kp_str}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7; font-size: 0.85em;">{details_str}</td>
      </tr>
"""

                # Spacecraft arrivals
                for mr, impact in spacecraft_runs:
                    run_num = mr.get('run_number', '—')
                    spacecraft_name = impact.get('spacecraft_name', 'Unknown')
                    arrival_time = impact.get('arrival_time', '—')

                    html += f"""      <tr style="background-color: #fff9e6;">
        <td style="padding: 8px; border: 1px solid #bdc3c7;">{run_num}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7; font-weight: bold;">{spacecraft_name}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7;">{arrival_time}</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7;">—</td>
        <td style="padding: 8px; border: 1px solid #bdc3c7;">—</td>
      </tr>
"""

                html += """    </tbody>
  </table>
"""

            html += "</div>\n"  # Close CME container

        # Overall summary
        html += f"""
<p style="margin-top: 15px; padding: 10px; background-color: #ecf0f1; border-radius: 5px; font-size: 0.9em;">
<strong>Summary:</strong> {cme_num} CME event(s) with arrival predictions |
Earth arrivals: {total_earth_arrivals} | Spacecraft arrivals: {total_spacecraft_arrivals}
</p>
<p style="font-size: 0.85em; color: #777; font-style: italic;">
Note: LE (Leading Edge) = bulk CME material, SH (Shock) = shock wave ahead of CME. Shock arrives first.
</p>
"""

        return html
