import requests
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd


#1. Set API parameters 
station_id = '183476'
api_url = "https://api.weatherflow.com/wxengine/rest/graph/getGraph"
api_token = '8408aaf6de0d159232098dc647c833b1'
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 1, 5)
days_per_request = 5
wind_speed_thresholds = [8, 12, 16, 20, 24, 28]
output_file_path = 'C:/PythonTemp/wind_data_2023.csv'

 # 2. Function to collect data for a specific time period 
def fetch_wind_data(station_id, start_time, end_time):
    params = {  'spot_id': station_id,
                'time_start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'time_end': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'units_wind': 'mph',
                'fields': 'wind,wind_gust,wind_dir',
                'wf_token': api_token,
                'type': 'dataonly',
                'format': 'json' }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    else: 
        print(f"Error fetching data: {response.status_code}")
        return None

# 3. Parse data into dataframe and display data
data = fetch_wind_data(183476, start_date, end_date)
wind_data = data['wind_avg_data']
df = pd.DataFrame(wind_data, columns=["Epoch Time", "Wind Speed"])
df["Time"] = pd.to_datetime(df["Epoch Time"], unit='ms')
plt.plot(df["Time"], df["Wind Speed"])
plt.xlabel("Time")
plt.ylabel("Wind Speed")
plt.grid(True)
plt.show()
print(data)
