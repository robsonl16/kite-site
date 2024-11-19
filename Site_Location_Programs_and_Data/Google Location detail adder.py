import pandas as pd
import googlemaps
from concurrent.futures import ThreadPoolExecutor
import time

# Initialize Google Maps client
API_KEY = 'AIzaSyAqTazbXdD_p68EMJK1QmvWzI-HdSH3km8'
gmaps = googlemaps.Client(key=API_KEY)

# Function to fetch location details
def fetch_location_details(row):
    lat, lon = row['Latitude'], row['Longitude']
    station_id = row['Station_Id']
    try:
        # Reverse geocoding for address components
        geocode_result = gmaps.reverse_geocode((lat, lon))
        address_components = {comp['types'][0]: comp['long_name'] for result in geocode_result for comp in result['address_components']}
        
        # Parse location details
        country = address_components.get('country', 'Unknown')
        state = address_components.get('administrative_area_level_1', 'Unknown')
        county = address_components.get('administrative_area_level_2', 'Unknown')
        municipality = address_components.get('locality', 'Unknown')

        # Find nearby water body
        places_result = gmaps.places_nearby(location=(lat, lon), radius=5000, type='natural_feature')
        water_body = 'Unknown'
        for place in places_result.get('results', []):
            if 'water' in place['name'].lower():
                water_body = place['name']
                break
        
        return {
            'Station_Id': station_id,
            'Country': country,
            'State': state,
            'County': county,
            'Municipality': municipality,
            'Nearest_Water_Body': water_body
        }
    except Exception as e:
        print(f"Error processing station {station_id}: {e}")
        return {
            'Station_Id': station_id,
            'Country': 'Error',
            'State': 'Error',
            'County': 'Error',
            'Municipality': 'Error',
            'Nearest_Water_Body': 'Error'
        }

# Function to process batch of rows
def process_batch(batch):
    results = []
    for _, row in batch.iterrows():
        result = fetch_location_details(row)
        results.append(result)
    return results

def main():
    # Load station data
    input_file = 'C://weather_station_data/Stations Need Country Data 241118.csv'  # Path to your CSV file
    stations = pd.read_csv(input_file)

    # Prepare output storage
    all_results = []
    intermediate_counter = 0

    # Use ThreadPoolExecutor to parallelize
    batch_size = 1000  # Number of locations per batch
    save_interval = 5000  # Save intermediate results every 5000 locations

    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(0, len(stations), batch_size):
            batch = stations.iloc[i:i + batch_size]
            futures = executor.submit(process_batch, batch)
            all_results.extend(futures.result())
            
            # Print progress every 1000 locations
            print(f"Processed {len(all_results)} locations so far.")
            
            # Save intermediate results every 5000 locations
            if len(all_results) // save_interval > intermediate_counter:
                intermediate_counter += 1
                intermediate_file = f'C://weather_station_data/intermediate_results_{intermediate_counter * save_interval}.csv'
                pd.DataFrame(all_results).to_csv(intermediate_file, index=False)
                print(f"Intermediate results saved to '{intermediate_file}'.")

            time.sleep(1)  # Optional: Throttle requests to avoid quota limits

    # Save final results to a CSV
    final_file = 'C://weather_station_data/stations_with_google_info.csv'
    pd.DataFrame(all_results).to_csv(final_file, index=False)
    print(f"Processing complete! Results saved to '{final_file}'.")

if __name__ == "__main__":
    main()
