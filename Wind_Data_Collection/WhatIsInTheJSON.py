import requests
import json
from datetime import datetime, timedelta

# 1. Set API parameters
station_id = '183476'
api_url = "https://api.weatherflow.com/wxengine/rest/graph/getGraph"
api_token = '8408aaf6de0d159232098dc647c833b1'
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 1, 2)
days_per_request = 5
output_file_path = 'C:/Kite_site/wind_data_output.json'

# 2. Function to fetch and save JSON data for a specific time period
def fetch_and_save_wind_data(station_id, start_time, end_time, output_file):
    params = {
        'spot_id': station_id,
        'time_start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'time_end': end_time.strftime('%Y-%m-%d %H:%M:%S'),
        'units_wind': 'mph',
        'fields': 'wind,wind_gust,wind_dir',
        'wf_token': api_token,
        'type': 'dataonly',
        'format': 'json'
    }
    
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        # Write the JSON response to the output file
        response_data = response.json()
        with open(output_file, 'a') as f:
            f.write(json.dumps(response_data, indent=4))
            f.write("\n\n")  # Add spacing between blocks for readability
        print(f"Data from {start_time} to {end_time} written to file.")
        return response_data
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return None

# 3. Loop through the date range and fetch data in blocks
current_start = start_date
with open(output_file_path, 'w') as f:  # Create or clear the file before appending data
    f.write("")  # Clear the file

while current_start < end_date:
    current_end = min(current_start + timedelta(days=days_per_request - 1), end_date)
    print(f"Fetching data from {current_start} to {current_end}...")
    fetch_and_save_wind_data(station_id, current_start, current_end, output_file_path)
    current_start = current_end + timedelta(days=1)

print(f"All data saved to {output_file_path}.")
