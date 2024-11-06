import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Paths to downloaded shapefiles (update these paths to your actual files)
national_boundary_path = "C:/weather_station_data/Boundaries/geoBoundariesCGAZ_ADM0.shp"
regional_boundary_path = "C:/weather_station_data/Boundaries/geoBoundariesCGAZ_ADM1.shp"
municipal_boundary_path = "C:/weather_station_data/Boundaries/geoBoundariesCGAZ_ADM2.shp"

# Load boundary shapefiles
national_boundaries = gpd.read_file(national_boundary_path)
regional_boundaries = gpd.read_file(regional_boundary_path)
municipal_boundaries = gpd.read_file(municipal_boundary_path)

# Load the station data with latitude and longitude
station_data_path = "C:/weather_station_data/all_weather_stations_241105.csv"
stations_df = pd.read_csv(station_data_path)

# Convert stations to a GeoDataFrame
stations_gdf = gpd.GeoDataFrame(
    stations_df,
    geometry=gpd.points_from_xy(stations_df["Longitude"], stations_df["Latitude"]),
    crs="EPSG:4326"  # WGS84 Latitude/Longitude
)

# Initialize columns for the administrative boundary information
stations_gdf["Country"] = None
stations_gdf["Nearest Country"] = None
stations_gdf["Region"] = None
stations_gdf["Nearest Region"] = None
stations_gdf["Municipality"] = None
stations_gdf["Nearest Municipality"] = None

# Define output file path
output_file = "C:/weather_station_data/weather_stations_with_boundaries.csv"

# Function to assign boundary or nearest boundary with distance calculation in a projected CRS
def assign_boundary_or_nearest(stations, boundaries, boundary_name, nearest_boundary_name):
    # Use 'shapeName' as the column containing boundary names
    boundary_column = "shapeName"

    # Reproject boundaries to a projected CRS for accurate distance calculations
    projected_crs = "EPSG:3857"  # You can also use EPSG:3395 or another suitable projected CRS
    boundaries_proj = boundaries.to_crs(projected_crs)
    stations_proj = stations.to_crs(projected_crs)

    # Perform spatial join in the original CRS to find which points are within boundaries
    joined = gpd.sjoin(stations, boundaries, how="left", predicate="within")
    stations[boundary_name] = joined[boundary_column]
    
    # Identify stations that are not within any boundary
    outside_stations = stations[stations[boundary_name].isnull()]
    
    if not outside_stations.empty:
        print(f"Finding nearest {boundary_name} for stations outside boundaries...")
        
        # Calculate the nearest boundary for each station outside the boundary
        for idx, station in outside_stations.iterrows():
            # Project the individual station point to the projected CRS
            station_point = gpd.GeoSeries([station.geometry], crs="EPSG:4326").to_crs(projected_crs).iloc[0]
            
            # Calculate distances to all boundaries in the projected CRS
            distances = boundaries_proj.distance(station_point)
            nearest_boundary_idx = distances.idxmin()  # Get the index of the closest boundary
            nearest_boundary_name_val = boundaries.iloc[nearest_boundary_idx][boundary_column]
            stations.at[idx, nearest_boundary_name] = nearest_boundary_name_val

            # Save progress after each station to capture data along the way
            stations.drop(columns="geometry").to_csv(output_file, index=False)
    
    return stations

# Assign national, regional, and municipal boundaries or nearest if outside
stations_gdf = assign_boundary_or_nearest(stations_gdf, national_boundaries, "Country", "Nearest Country")
stations_gdf = assign_boundary_or_nearest(stations_gdf, regional_boundaries, "Region", "Nearest Region")
stations_gdf = assign_boundary_or_nearest(stations_gdf, municipal_boundaries, "Municipality", "Nearest Municipality")

# Save the final enriched station data to the CSV file
stations_gdf.drop(columns="geometry").to_csv(output_file, index=False)
print(f"Final data with boundaries saved to {output_file}")
