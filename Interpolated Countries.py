import geopandas as gpd
import rasterio
from rasterio.features import rasterize, shapes
from rasterio.transform import from_origin
from shapely.geometry import Polygon, shape
import numpy as np
from scipy.ndimage import distance_transform_edt
import pandas as pd

# Define paths
country_boundary_path = "C:/weather_station_data/Boundaries/geoBoundariesCGAZ_ADM2.shp"
intermediate_output_dir = "C:/weather_station_data/Boundaries/intermediate_outputs/"
output_path = "C:/weather_station_data/Boundaries/final_municipalities_combined_with_obnt_boundaries.shp"

# Load the country boundaries
countries = gpd.read_file(country_boundary_path)

# Reproject to a projected CRS for accurate distance calculations
countries = countries.to_crs("EPSG:3857")

# Set pixel size to 4,000 meters (4 km)
pixel_size = 4000  
minx, miny, maxx, maxy = countries.total_bounds
width = int((maxx - minx) / pixel_size)
height = int((maxy - miny) / pixel_size)
transform = from_origin(minx, maxy, pixel_size, pixel_size)

# Prepare country ID mapping
country_ids = {idx + 1: name for idx, name in enumerate(countries["shapeName"])}

# Step 1: Save Centroids for Debugging
countries["centroid"] = countries.geometry.centroid
centroids = countries[["shapeName", "centroid"]].copy()
centroids = centroids.set_geometry("centroid")
centroids.to_file(f"{intermediate_output_dir}country_centroids.shp")
print("Saved country centroids for debugging.")

# Step 2: Rasterize the countries and save the initial raster
shapes_generator = ((geom, idx + 1) for idx, geom in enumerate(countries.geometry))
initial_raster = rasterize(
    shapes=shapes_generator,
    out_shape=(height, width),
    transform=transform,
    fill=0,  # Fill areas outside countries with 0
    dtype="int32"
)

with rasterio.open(f"{intermediate_output_dir}initial_country_raster.tif", "w", driver="GTiff", height=height, width=width,
                   count=1, dtype=initial_raster.dtype, crs="EPSG:3857", transform=transform) as dst:
    dst.write(initial_raster, 1)
print("Saved initial rasterized country boundaries.")

# Step 3: Distance transform for "nearest country" interpolation
country_mask = initial_raster != 0
distance, nearest_country_raster = distance_transform_edt(~country_mask, return_indices=True)

# Step 4: Save Distance Transformation Result for Debugging
np.save(f"{intermediate_output_dir}distance_transformed.npy", distance)
print("Saved distance transformation results for debugging.")

# Step 5: Assign nearest country IDs to outside areas and save the final raster
nearest_country_ids = initial_raster[nearest_country_raster[0], nearest_country_raster[1]]
final_raster = initial_raster.copy()
final_raster[~country_mask] = nearest_country_ids[~country_mask]  # Assign nearest country ID

with rasterio.open(f"{intermediate_output_dir}final_nearest_country_raster.tif", "w", driver="GTiff", height=height, width=width,
                   count=1, dtype=final_raster.dtype, crs="EPSG:3857", transform=transform) as dst:
    dst.write(final_raster, 1)
print("Saved final raster with nearest country interpolation.")

# Step 6: Convert raster back to a GeoDataFrame with polygons, including OBNT shapes
result = []
for i, country_id in enumerate(np.unique(final_raster)):
    if country_id == 0:
        continue  # Skip background

    # Print progress for each country_id
    print(f"Processing country ID {country_id} ({i + 1} of {len(np.unique(final_raster)) - 1})")

    country_mask = final_raster == country_id
    shape_generator = shapes(country_mask.astype("uint8"), transform=transform)
    country_name = country_ids.get(country_id, f"Unknown_{country_id}")
    
    for geom, value in shape_generator:
        if value == 1:  # Only consider actual shapes
            geom = shape(geom)  # Convert to Shapely geometry
            geom_gdf = gpd.GeoSeries([geom], crs="EPSG:3857").to_crs("EPSG:4326")
            is_obnt = not (initial_raster == country_id).any()  # Determine if it’s OBNT or actual shape
            result.append({
                "geometry": geom_gdf.iloc[0],
                "country": f"OBNT_{country_name}" if is_obnt else country_name
            })

# Convert to GeoDataFrame and combine with original boundaries
original_countries = countries.to_crs("EPSG:4326")[["shapeName", "geometry"]].rename(columns={"shapeName": "country"})
obnt_gdf = gpd.GeoDataFrame(result, crs="EPSG:4326")

# Concatenate original and OBNT shapes into one GeoDataFrame
combined_gdf = pd.concat([original_countries, obnt_gdf], ignore_index=True)

# Save the final combined shapefile with both original and OBNT shapes
combined_gdf.to_file(output_path)
print("Final shapefile with original and OBNT boundaries saved.")
