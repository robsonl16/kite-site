import pandas as pd
import requests
from datetime import datetime

# Load the CSV file
locations = pd.read_csv(r'C:\Kite_site\Station_Locations.csv')

# Define the function to get sunrise, sunset, dawn, and dusk
def get_sunrise_sunset(lat, lon, date):
    formatted_date = date.strftime('%Y-%m-%d')
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={formatted_date}&formatted=0"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()['results']
        sunrise = data['sunrise']
        sunset = data['sunset']
        dawn = data['civil_twilight_begin']
        dusk = data['civil_twilight_end']
        return sunrise, sunset, dawn, dusk
    else:
        print(f"Error fetching sunrise/sunset data for ({lat}, {lon}) on {formatted_date}: {response.status_code}")
        return None, None, None, None

# Define the date for which you want to fetch the data (e.g., January 1, 2024)
win_sol = datetime(2025, 12, 21)
sum_sol = datetime(2025, 6, 20)
ver_equ = datetime(2024, 3, 20)
aut_equ = datetime(2024, 9, 22)

# Prepare an empty list to store results
sun_data_results = []

# Loop through each location to get sunrise, sunset, dawn, and dusk data
for index, row in locations.iterrows():
    station_id = row['Station_ID']
    station_name = row['Station Name']
    lat = row['Latitude']
    lon = row['Longitude']
    
    # Get sunrise, sunset, dawn, and dusk data for the target date
    ws_sunrise, ws_sunset, ws_dawn, ws_dusk = get_sunrise_sunset(lat, lon, win_sol)
    ss_sunrise, ss_sunset, ss_dawn, ss_dusk = get_sunrise_sunset(lat, lon, sum_sol)
    ve_sunrise, ve_sunset, ve_dawn, ve_dusk = get_sunrise_sunset(lat, lon, ver_equ)
    ae_sunrise, ae_sunset, ae_dawn, ae_dusk = get_sunrise_sunset(lat, lon, aut_equ)
    
    # Store the result
    sun_data_results.append({
        "Station_ID": station_id,
        "Station Name": station_name,
        "Latitude": lat,
        "Longitude": lon,
        "WS_Sunrise (UTC)": ws_sunrise,
        "WS_Sunset (UTC)": ws_sunset,
        "WS_Dawn (UTC)": ws_dawn,
        "WS_Dusk (UTC)": ws_dusk,
        "SS_Sunrise (UTC)": ss_sunrise,
        "SS_Sunset (UTC)": ss_sunset,
        "SS_Dawn (UTC)": ss_dawn,
        "SS_Dusk (UTC)": ss_dusk,
        "VE_Sunrise (UTC)": ve_sunrise,
        "VE_Sunset (UTC)": ve_sunset,
        "VE_Dawn (UTC)": ve_dawn,
        "VE_Dusk (UTC)": ve_dusk,
        "AE_Sunrise (UTC)": ae_sunrise,
        "AE_Sunset (UTC)": ae_sunset,
        "AE_Dawn (UTC)": ae_dawn,
        "AE_Dusk (UTC)": ae_dusk
    })

    # Print progress every 100 stations
    if (index + 1) % 100 == 0:
        print(f"Processed {index + 1} stations")

    # Save intermediate results every 1000 stations
    if (index + 1) % 1000 == 0:
        intermediate_df = pd.DataFrame(sun_data_results)
        intermediate_file = f'C:/Kite_site/SunData2_part_{index + 1}.csv'
        intermediate_df.to_csv(intermediate_file, index=False)
        print(f"Intermediate file saved: {intermediate_file}")

# Final save for all results
sun_data_df = pd.DataFrame(sun_data_results)
sun_data_df.to_csv('C:/Kite_site/Full_SunData.csv', index=False)

print("Final sun data saved to C:/Kite_site/Full_SunData.csv")
