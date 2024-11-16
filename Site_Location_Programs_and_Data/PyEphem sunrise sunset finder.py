#!/usr/bin/env python3

import pandas as pd
import logging
from datetime import datetime, timedelta, timezone
import ephem
import os

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# Processing function for a CSV of locations
def process_locations(file_path: str, start_date: datetime, end_date: datetime, timezone_offset: int):
    """Process sunrise, sunset, dawn, and dusk times for multiple locations from a CSV file."""
    locations_df = pd.read_csv(file_path)
    intermediate_files = []
    results = []
    output_folder = os.path.dirname(file_path)
    
    for idx, (_, row) in enumerate(locations_df.iterrows(), start=1):
        station_id = row['Station_ID']
        station_name = row['Station Name']
        latitude = row['Latitude']
        longitude = row['Longitude']
        elevation = row['Elevation (m)']

        # Set up observer
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)
        observer.elevation = int(elevation)

        current_date = start_date
        while current_date <= end_date:
            observer.date = current_date
            sun = ephem.Sun()

            # Initialize each value to None by default
            sunrise, sunset, dawn, dusk = None, None, None, None

            # Calculate sunrise
            try:
                sunrise = observer.next_rising(sun, use_center=True).datetime()
            except ephem.AlwaysUpError:
                log.warning(f"Continuous daylight at {station_name} on {current_date.strftime('%Y-%m-%d')}")
            except ephem.NeverUpError:
                log.warning(f"Continuous darkness at {station_name} on {current_date.strftime('%Y-%m-%d')}")

            # Calculate sunset
            try:
                sunset = observer.next_setting(sun, use_center=True).datetime()
            except ephem.AlwaysUpError:
                log.warning(f"Continuous daylight at {station_name} on {current_date.strftime('%Y-%m-%d')}")
            except ephem.NeverUpError:
                log.warning(f"Continuous darkness at {station_name} on {current_date.strftime('%Y-%m-%d')}")

            # Calculate dawn and dusk if sunrise and sunset exist
            if sunrise is not None and sunset is not None:
                observer.horizon = '-6'  # Dawn/dusk at 6 degrees below the horizon
                try:
                    dawn = observer.next_rising(sun, use_center=True).datetime()
                except (ephem.AlwaysUpError, ephem.NeverUpError):
                    dawn = None

                try:
                    dusk = observer.next_setting(sun, use_center=True).datetime()
                except (ephem.AlwaysUpError, ephem.NeverUpError):
                    dusk = None

            # Adjust times for timezone if valid
            timezone_info = timezone(timedelta(hours=timezone_offset))
            sunrise = sunrise.astimezone(timezone_info).strftime('%Y-%m-%d %H:%M:%S') if sunrise else None
            sunset = sunset.astimezone(timezone_info).strftime('%Y-%m-%d %H:%M:%S') if sunset else None
            dawn = dawn.astimezone(timezone_info).strftime('%Y-%m-%d %H:%M:%S') if dawn else None
            dusk = dusk.astimezone(timezone_info).strftime('%Y-%m-%d %H:%M:%S') if dusk else None

            results.append({
                'Station_ID': station_id,
                'Station Name': station_name,
                'Date': current_date.strftime('%Y-%m-%d'),
                'Dawn': dawn,
                'Sunrise': sunrise,
                'Sunset': sunset,
                'Dusk': dusk
            })

            current_date += timedelta(days=1)

        # Print progress every 100 stations
        if idx % 100 == 0:
            log.info(f"Processed {idx} stations")

        # Save intermediate results every 1000 stations
        if idx % 1000 == 0:
            intermediate_file_path = os.path.join(output_folder, f"intermediate_{idx // 1000}.csv")
            intermediate_files.append(intermediate_file_path)

            # Append new results to the intermediate file
            pd.DataFrame(results).to_csv(intermediate_file_path, mode='a', header=not os.path.exists(intermediate_file_path), index=False)
            results.clear()  # Clear memory after saving

    # Save final results if any remain
    if results:
        final_intermediate_file = os.path.join(output_folder, f"intermediate_{(idx // 1000) + 1}.csv")
        intermediate_files.append(final_intermediate_file)
        pd.DataFrame(results).to_csv(final_intermediate_file, mode='a', header=True, index=False)
    
    # Combine all intermediate files into a final output
    combined_output_path = os.path.join(output_folder, 'combined_sunrise_sunset_dawn_dusk_times2.csv')
    with open(combined_output_path, 'w') as combined_file:
        for i, file in enumerate(intermediate_files):
            with open(file, 'r') as f:
                if i > 0:
                    next(f)  # Skip header for subsequent files
                combined_file.write(f.read())
            os.remove(file)  # Remove intermediate file after combining

    log.info(f"Final results saved to '{combined_output_path}'")

# Define date range and timezone offset for the calculation
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
timezone_offset = 0  # Change as needed

# Run the location processing
process_locations('c:/Kite_site/Station_Elevations_Final.csv', start_date, end_date, timezone_offset)
