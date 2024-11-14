import pandas as pd
import requests

# Load the CSV file
locations = pd.read_csv(r'C:\Kite_site\Station_Locations.csv')

# Define the function to get elevation
def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results'][0]['elevation']
    else:
        print(f"Error fetching elevation data for ({lat}, {lon}): {response.status_code}")
        return None

# Prepare an empty list to store results
elevation_results = []

# Start the loop from the 2001st row
for index, row in locations.iloc[33000:].iterrows():
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

# Final save for all results
elevation_df = pd.DataFrame(elevation_results)
elevation_df.to_csv('C:/Kite_site/Station_Elevations.csv', index=False)

print("Final elevation data saved to C:/Kite_site/Station_Elevations.csv")
