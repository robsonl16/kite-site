import pandas as pd
import requests
import json
import math
import csv
from datetime import datetime, timedelta
import process_wind_data
import gc

# --- 1. USER-DEFINED VARIABLES ---
# File paths
locations_file = 'C:/Kite_site/Locations_2_Process.csv'
ss_weekly_file = 'C:/Kite_site/SS_Weekly_Local_Corr.csv'
output_csv_file = 'C:/Kite_Site/Output/daytime_wind_analysis1.csv'
intermediate_data_file = 'C:/Kite_site/Output/intermediate_wind_data.json'

# API details
api_url = "https://api.weatherflow.com/wxengine/rest/graph/getGraph"
api_token = '8408aaf6de0d159232098dc647c833b1'

# Date range
start_date = datetime(2019, 1, 1)
end_date = datetime(2024, 11, 14)  # Adjust as needed

# Wind speed thresholds in knots
wind_speed_thresholds = [4, 8, 12, 16, 20, 24, 28, 32]

# --- 2. LOAD LOCATION AND SUNRISE/SUNSET FILES ---
# Load the list of Site_Ids
locations_df = pd.read_csv(locations_file)
site_ids = locations_df['Station_Id'].tolist()

# Load and preprocess the sunrise/sunset corrections
print("Loading and indexing SS_Weekly_Local_Corr.csv...")
ss_weekly_df = pd.read_csv(ss_weekly_file)

# Create a dictionary for efficient lookups
ss_lookup = {}
for _, row in ss_weekly_df.iterrows():
    site_id = row['Station_Id']
    week = row['Week']
    if site_id not in ss_lookup:
        ss_lookup[site_id] = {}
    ss_lookup[site_id][week] = {
        'sunrise': row['Sunrise_Week_Local_Corr'],
        'sunset': row['Sunset_Week_Local_Corr']
    }

print("Sunrise/Sunset lookup table created.")

def process_wind_data(data: dict, sunrise: datetime, sunset: datetime) -> dict:
    """
    Process the JSON data for a specific site and calculate metrics within the sunrise-sunset time window.

    Args:
        data (dict): JSON data containing 'data' (filtered wind data) and 'units_wind' (string).
        sunrise (datetime): Sunrise time for the day.
        sunset (datetime): Sunset time for the day.

    Returns:
        dict: Processed metrics for the day.
    """
    # Extract units_wind directly from the data
    units_wind = data.get('units_wind', 'knots')

    # Initialize processed data
    processed_data = {
        "daylight_hours": (sunset - sunrise).total_seconds() / 3600,  # Total daylight hours
        "air_temp_avg": None,
        "air_temp_low": None,
        "air_temp_high": None,
        "precip_sum": 0.0,
        "precip_accum_sum": 0.0,
        "data_frequency": None,  # Average interval between data points (in minutes)
        "units_wind": units_wind,
        "gustiness_avg": None,
        "lulliness_avg": None
    }

    # Add columns for hours above thresholds
    for threshold in wind_speed_thresholds:
        processed_data[f"Hours above {threshold} knots"] = 0.0

    # Helper variables for calculations
    sin_sum, cos_sum, wind_count = 0, 0, 0
    time_gaps = []
    time_gap = 5
    last_time = None
    valid_data_points = 0
    wind_data = data.get('data', [])

    for entry in wind_data:
        timestamp = datetime.fromtimestamp(entry['time'] / 1000.0)
        if sunrise <= timestamp <= sunset:
            # Calculate time gap and handle blanks
            if last_time:
                time_gap = (timestamp - last_time).total_seconds() / 60  # Time gap in minutes
                if time_gap > 120:  # Skip large gaps (e.g., >120 minutes)
                    print(f"Skipping large gap of {time_gap} minutes at {timestamp}")
                    last_time = timestamp
                    continue
                time_gaps.append(time_gap)
            last_time = timestamp

            # Convert wind speeds to knots
            wind_avg = convert_wind_speed_to_knots(entry.get('wind_avg_data', 0), units_wind)
            wind_gust = convert_wind_speed_to_knots(entry.get('wind_gust_data', 0), units_wind)
            wind_lull = convert_wind_speed_to_knots(entry.get('wind_lull_data', 0), units_wind)

            valid_data_points += 1

            # Track air temperature stats
            air_temp = entry.get('air_temp_data')
            if air_temp is not None:
                if processed_data["air_temp_low"] is None or air_temp < processed_data["air_temp_low"]:
                    processed_data["air_temp_low"] = air_temp
                if processed_data["air_temp_high"] is None or air_temp > processed_data["air_temp_high"]:
                    processed_data["air_temp_high"] = air_temp
                if processed_data["air_temp_avg"] is None:
                    processed_data["air_temp_avg"] = air_temp
                else:
                    processed_data["air_temp_avg"] += air_temp

            # Track precipitation
            processed_data["precip_sum"] += entry.get('precip', 0)
            processed_data["precip_accum_sum"] += entry.get('precip_accum', 0)

            # Calculate hours above thresholds
            for threshold in wind_speed_thresholds:
                if wind_avg > threshold:
                    if time_gap > 0:
                        processed_data[f"Hours above {threshold} knots"] += (time_gap / 60)


            # Wind direction calculations
            if wind_avg > 4:  # Only for wind > 4 knots
                wind_dir = entry.get('wind_dir_data')
                if wind_dir is not None and isinstance(wind_dir, (int, float)):
                    sin_sum += math.sin(math.radians(wind_dir))
                    cos_sum += math.cos(math.radians(wind_dir))
                    wind_count += 1

                # Gustiness and lulliness
                gustiness = wind_gust - wind_avg
                lulliness = wind_avg - wind_lull
                processed_data["gustiness_avg"] = (processed_data["gustiness_avg"] or 0) + gustiness
                processed_data["lulliness_avg"] = (processed_data["lulliness_avg"] or 0) + lulliness

    # Finalize calculations
    if valid_data_points > 0:
        processed_data["air_temp_avg"] = processed_data["air_temp_avg"] / valid_data_points if processed_data["air_temp_avg"] is not None else None
    if time_gaps:
        processed_data["data_frequency"] = sum(time_gaps) / len(time_gaps)
    else:
        processed_data["data_frequency"] = None

    if wind_count > 0:
        avg_sin = sin_sum / wind_count
        avg_cos = cos_sum / wind_count
        processed_data["wind_avg_direction"] = math.degrees(math.atan2(avg_sin, avg_cos)) % 360
    else:
        processed_data["wind_avg_direction"] = None
    if processed_data["gustiness_avg"] is not None:
        processed_data["gustiness_avg"] /= wind_count
    if processed_data["lulliness_avg"] is not None:
        processed_data["lulliness_avg"] /= wind_count

    return processed_data



def convert_wind_speed_to_knots(speed: float, units_wind: str) -> float:
    """
    Convert wind speed to knots based on the units.

    Args:
        speed (float): The wind speed to be converted. Defaults to 0 if None.
        units_wind (str): The current units of the wind speed ('kph', 'mph', or 'knots').

    Returns:
        float: The wind speed converted to knots.
    """
    if speed is None:
        speed = 0  # Default to 0 if speed is None
    if units_wind == 'kph':
        return speed * 0.539957  # 1 kilometer per hour = 0.539957 knots
    elif units_wind == 'mph':
        return speed * 0.868976  # 1 mile per hour = 0.868976 knots
    elif units_wind == 'knots':
        return speed  # Already in knots, no conversion needed
    else:
        raise ValueError(f"Unsupported wind speed unit: {units_wind}")


# --- 3. FUNCTION TO FETCH DATA FROM API ---
def fetch_wind_data(site_id: str, start_time: datetime, end_time: datetime) -> dict:
    """
    Fetch data from the API for a specific site and time range.
    """
    params = {
        'spot_id': site_id,
        'time_start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'time_end': end_time.strftime('%Y-%m-%d %H:%M:%S'),
        'wf_token': api_token,
        'type': 'dataonly',
        'format': 'json'
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        print(f"Successfully fetched data for Site_Id {site_id} from {start_time} to {end_time}.")
        return response.json()
    else:
        print(f"Error fetching data for site {site_id}: {response.status_code}, {response.text}")
        return None

# --- 4. FUNCTION TO GET SUNRISE/SUNSET TIMES ---
def get_sunrise_sunset(site_id: str, current_date: datetime) -> (datetime, datetime):
    """
    Get the sunrise and sunset times for the site and current date based on weekly corrections.
    """
    week_number = current_date.timetuple().tm_yday // 7 + 1
    site_data = ss_lookup.get(site_id, {})
    week_data = site_data.get(week_number)

    if week_data:
        sunrise_time = week_data['sunrise']
        sunset_time = week_data['sunset']

        # Convert to datetime objects with AM/PM format handling
        try:
            sunrise = datetime.strptime(sunrise_time, '%I:%M:%S %p').replace(
                year=current_date.year, month=current_date.month, day=current_date.day
            )
            sunset = datetime.strptime(sunset_time, '%I:%M:%S %p').replace(
                year=current_date.year, month=current_date.month, day=current_date.day
            )
            return sunrise, sunset
        except ValueError as e:
            raise ValueError(f"Error parsing sunrise/sunset times for Site_Id {site_id}, Week {week_number}: {e}")
    else:
        raise ValueError(f"No sunrise/sunset data found for Site_Id {site_id} and Week {week_number}.")

# --- 5. MAIN SCRIPT TO LOOP THROUGH LOCATIONS AND DATES ---
all_results = []

# Loop through each site
for site_id in site_ids:
    try:
        # Initialize the start of the date range for the location
        current_date = start_date

        # Loop through the date range in 7-day chunks
        while current_date <= end_date:
            # Calculate the 7-day range
            range_end_date = min(current_date + timedelta(days=6), end_date)
            # print(f"Fetching data for Site_Id {site_id} from {current_date.date()} to {range_end_date.date()}...")

            # Get sunrise/sunset times for each day in the 7-day range
            sunrise_sunset_times = []
            for day in (current_date + timedelta(days=i) for i in range((range_end_date - current_date).days + 1)):
                try:
                    sunrise, sunset = get_sunrise_sunset(site_id, day)
                    sunrise_sunset_times.append((day, sunrise, sunset))
                except ValueError as e:
                    print(f"Skipping day {day.date()} for Site_Id {site_id}: {e}")

            # Fetch 7 days of data in a single API call
            json_data = fetch_wind_data(site_id, current_date, range_end_date)
            if json_data:
                # Keys for individual data sets
                keys_to_process = ['wind_avg_data', 'wind_gust_data', 'wind_lull_data', 
                                   'wind_dir_data', 'air_temp_data', 'precip_data', 'precip_accum_data']
                units_wind = json_data.get('units_wind')

                # Loop through each day in the 7-day range
                for day, sunrise, sunset in sunrise_sunset_times:
                    try:
                        # print(f"Processing Site_Id {site_id} on {day.date()} with Sunrise: {sunrise}, Sunset: {sunset}...")

                        # Initialize a unified data structure for this day
                        unified_data = {}

                        # Process each key individually
                        for key in keys_to_process:
                            if key not in json_data:
                                # print(f"Key {key} not found in JSON data. Skipping...")
                                continue

                            if json_data[key] is None:
                                # print(f"Key {key} is present but has no data. Skipping...")
                                continue

                            # Process entries within the key
                            for entry in json_data[key]:
                                timestamp, value = entry  # Each entry is [timestamp, value]
                                entry_time = datetime.fromtimestamp(timestamp / 1000.0)  # Convert Unix Epoch to datetime

                                # Filter by sunrise-sunset window for this day
                                if sunrise <= entry_time <= sunset:
                                    if timestamp not in unified_data:
                                        unified_data[timestamp] = {"time": timestamp}
                                    unified_data[timestamp][key] = value

                        # Convert the unified data dictionary into a list for processing
                        daily_data = list(unified_data.values())

                        # Debugging: Print the unified data for this day
                        # print(f"Unified data for Site_Id {site_id} on {day.date()}: {daily_data}")

                        # Process the day's data if there are valid entries
                        if daily_data:
                            processed = process_wind_data(
                                {'data': daily_data, 
                                 'units_wind': json_data.get('units_wind'), 
                                 'units_temp': json_data.get('units_temp')}, 
                                sunrise, sunset
                            )
                            processed["date"] = day.date()  # Add the date to the results
                            processed["Site_Id"] = site_id  # Add the site ID to the results
                            all_results.append(processed)

                    except Exception as e:
                        print(f"Error processing day {day.date()} for Site_Id {site_id}: {e}")
                        continue  # Move to the next day

            # Move to the next 7-day block
            current_date += timedelta(days=7)

        # Save intermediate results for the current site
        intermediate_file_path = f"C:/Kite_Site/Output/intermediate_{site_id}.csv"
        if all_results:
            with open(intermediate_file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
                writer.writeheader()
                writer.writerows(all_results)
            print(f"Intermediate file saved for Site_Id {site_id} at {intermediate_file_path}")
            gc.collect()  # Clear memory
            all_results.clear()

    except Exception as e:
        print(f"Error processing Site_Id {site_id}: {e}")


# --- 6. SAVE RESULTS TO CSV ---
if all_results:
    with open(output_csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)
    print(f"Analysis complete. Results saved to {output_csv_file}.")
else:
    print("No data was collected or processed. No results saved.")

