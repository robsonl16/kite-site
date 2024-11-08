import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
import pandas as pd

# Paths to input files and output
country_boundary_path = "C:/weather_station_data/Boundaries/geoBoundariesCGAZ_ADM0.shp"
raster_path = "C:/weather_station_data/Boundaries/final_nearest_country_raster.tif"
output_path = "C:/weather_station_data/final_combined_with_obnt_boundaries.shp"

# Load original country boundaries for later combination
countries = gpd.read_file(country_boundary_path)
countries = countries.to_crs("EPSG:4326")  # Ensure it's in geographic CRS for consistency

# Create a mapping of country IDs to country names
country_id_to_name = {idx + 1: name for idx, name in enumerate(countries["shapeName"])}
countries["country_id"] = countries["shapeName"].map(country_id_to_name)  # Add this to GeoDataFrame for reference

# Initialize a list to store OBNT polygons
obnt_polygons = []

# Load the final nearest country raster
with rasterio.open(raster_path) as src:
    transform = src.transform
    raster_data = src.read(1)  # Read the data from the single band

    # Convert each unique country ID in the raster to polygons
    for geom, country_id in shapes(raster_data, transform=transform):
        if country_id == 0:
            continue  # Skip background or no-data areas

        # Get the country name for the current country ID
        country_name = country_id_to_name.get(country_id, f"Unknown_{country_id}")

        # Convert the raster polygon to a Shapely geometry
        polygon = shape(geom)
        polygon_gdf = gpd.GeoDataFrame(
            [[polygon, f"OBNT_{country_name}"]],
            columns=["geometry", "country"],
            crs="EPSG:3857"  # The CRS of the raster
        ).to_crs("EPSG:4326")  # Reproject to geographic CRS
        
        # Append the new OBNT polygon to the list
        obnt_polygons.append(polygon_gdf)

# Concatenate all OBNT polygons into a single GeoDataFrame
obnt_gdf = pd.concat(obnt_polygons, ignore_index=True)

# Rename the original country field for consistency
countries = countries.rename(columns={"shapeName": "country"})

# Combine the original countries with the OBNT polygons
combined_gdf = pd.concat([countries, obnt_gdf], ignore_index=True)

# Save the combined GeoDataFrame to a new shapefile
combined_gdf.to_file(output_path)
print("Final combined shapefile with original and OBNT boundaries saved.")
