import requests
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import math
API_TOKEN = '8408aaf6de0d159232098dc647c833b1'
API_URL = "https://api.weatherflow.com/wxengine/rest/graph/getGraph"
# Constants/Parameters
station_id = '183476'
api_token = '8408aaf6de0d159232098dc647c833b1'
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 1, 5)
days_per_request = 5
wind_speed_thresholds = [8, 12, 16, 20, 24, 28]
output_file_path = 'C:/PythonTemp/wind_data_2023.csv'

def get_api_token():
    """
    Helper to get Weatherflow API Token String
    
    Parameters: None
    
    Returns: (str) Weatherflow API Token String
    
    Raises: None
    """
    return API_TOKEN

def get_api_url():
    """
    Helper to get Weatherflow API URL
    
    Parameters: None
    
    Returns: (str) Weatherflow API URL String
    
    Raises: None
    """
    return API_URL

def get_request(url, params):
    """
    Helper to make GET requests and return json of response
    
    Parameters: (str) url - URL address to make request to
                (dict) params - Dictionary of parameters to send in the request
    
    Returns: (dict) JSON response of request
    
    Raises: None
    """
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else: 
        print(f"Error fetching data: {response.status_code}")
        return None

def kph_to_knots(kph):
    return kph/1.852

def mph_to_knots(mph):
    return mph/1.15078

def mph_to_kph(mph):
    return mph*1.60934

def kph_to_mph(kph):
    return kph/1.60934

def degrees_to_rads(degrees):
    return (degrees*math.pi)/180

 # 2. Function to collect data for a specific time period 
def fetch_wind_data_all(station_id, start_time, end_time):
    params = {  'spot_id': station_id,
                'time_start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'time_end': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'units_wind': 'kph',
                'fields': 'wind,wind_gust,wind_dir',
                'wf_token': get_api_token(),
                'type': 'dataonly',
                'format': 'json' }
    url = get_api_url()
    response = get_request(url, params)
    return response

def fetch_wind_avg_data(station_id, start_time, end_time):
    data = fetch_wind_data_all(station_id, start_time, end_time)
    wind_data = data.get('wind_avg_data')
    df = pd.DataFrame(wind_data, columns=["Epoch Time", "Wind Speed (kph)"])
    df["Time"] = pd.to_datetime(df["Epoch Time"], unit='ms')
    df["Wind Speed (mph)"] = df["Wind Speed (kph)"].apply(kph_to_mph)
    df["Wind Speed (knots)"] = df["Wind Speed (kph)"].apply(kph_to_knots)
    return df

def fetch_wind_gust_data(station_id, start_time, end_time):
    data = fetch_wind_data_all(station_id, start_time, end_time)
    wind_data = data.get('wind_gust_data')
    df = pd.DataFrame(wind_data, columns=["Epoch Time", "Wind Speed (kph)"])
    df["Time"] = pd.to_datetime(df["Epoch Time"], unit='ms')
    df["Wind Speed (mph)"] = df["Wind Speed (kph)"].apply(kph_to_mph)
    df["Wind Speed (knots)"] = df["Wind Speed (kph)"].apply(kph_to_knots)
    return df

def fetch_wind_lull_data(station_id, start_time, end_time):
    data = fetch_wind_data_all(station_id, start_time, end_time)
    wind_data = data.get('wind_lull_data')
    df = pd.DataFrame(wind_data, columns=["Epoch Time", "Wind Speed (kph)"])
    df["Time"] = pd.to_datetime(df["Epoch Time"], unit='ms')
    df["Wind Speed (mph)"] = df["Wind Speed (kph)"].apply(kph_to_mph)
    df["Wind Speed (knots)"] = df["Wind Speed (kph)"].apply(kph_to_knots)
    return df

def fetch_wind_dir_data(station_id, start_time, end_time):
    data = fetch_wind_data_all(station_id, start_time, end_time)
    wind_data = data.get('wind_dir_data')
    df = pd.DataFrame(wind_data, columns=["Epoch Time", "Wind Direction (degrees)"])
    df["Time"] = pd.to_datetime(df["Epoch Time"], unit='ms')
    df["Wind Direction (rads)"] = df["Wind Direction (degrees)"].apply(degrees_to_rads)
    return df


#wind_avg_data, wind_gust_data, wind_lull_data, wind_dir_data

# # 3. Parse data into dataframe and display data
# data = fetch_wind_data(183476, start_date, end_date)
# wind_data = data['wind_avg_data']
# df = pd.DataFrame(wind_data, columns=["Epoch Time", "Wind Speed"])
# df["Time"] = pd.to_datetime(df["Epoch Time"], unit='ms')
# plt.plot(df["Time"], df["Wind Speed"])
# plt.xlabel("Time")
# plt.ylabel("Wind Speed")
# plt.grid(True)
# plt.show()
# print(data)

#test again!
