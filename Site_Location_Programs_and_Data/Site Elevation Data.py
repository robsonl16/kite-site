import pandas as pd
import requests
import time

# Load the CSV file
locations = pd.read_csv(r'C:\Kite_site\NoElev.csv')

# Define the function to get elevation
def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    for attempt in range(5):  # Retry up to 5 times
        try:
            response = requests.get(url, timeout=10)  # Set a timeout
            if response.status_code == 200:
                return response.json()['results'][0]['elevation']
            elif response.status_code == 504:
                print(f"504 Timeout for ({lat}, {lon}). Retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Error fetching elevation ({lat}, {lon}): {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request error for ({lat}, {lon}): {e}")
            return None
    print(f"Failed to fetch elevation after retries for ({lat}, {lon})")
    return None

# Prepare an empty list to store results
elevation_results = []

# Start the loop from the 2001st row
for index, row in locations.iloc[0:].iterrows():
    station_id = row['Station_ID']
    station_name = row['Station Name']
    lat = row['Latitude']
    lon = row['Longitude']
    
    # Get elevation data
    elevation = get_elevation(lat, lon)
    
    # Store the result
    elevation_results.append({
        "Station_ID": station_id,
        "Station Name": station_name,
        "Latitude": lat,
        "Longitude": lon,
        "Elevation (m)": elevation
    })
    
    # Print progress every 100 stations
    if (index + 1) % 100 == 0:
        print(f"Processed {index + 1} stations")
    
    # Save intermediate results every 1000 stations
    if (index + 1) % 1000 == 0:
        intermediate_df = pd.DataFrame(elevation_results)
        intermediate_file = f'C:/Kite_site/Station_Elevations_part_{index + 1}.csv'
        intermediate_df.to_csv(intermediate_file, index=False)
        print(f"Intermediate file saved: {intermediate_file}")
    
    time.sleep(0.5)

# Final save for all results
elevation_df = pd.DataFrame(elevation_results)
elevation_df.to_csv('C:/Kite_site/Station_Elevations_No.csv', index=False)

print("Final elevation data saved to C:/Kite_site/Station_Elevations.csv")
