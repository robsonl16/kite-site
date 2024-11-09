import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
from scipy.spatial import Voronoi
import numpy as np

# Paths to downloaded shapefiles and outputs
country_boundary_path = "C:/weather_station_data/Boundaries/geoBoundariesCGAZ_ADM0.shp"
intermediate_output_dir = "C:/weather_station_data/Boundaries/"
output_path = "C:/weather_station_data/Boundaries/final_national_with_obnt_boundaries.shp"

# Load the original country boundaries shapefile
countries = gpd.read_file(country_boundary_path)

# Step 1: Reproject to a Projected CRS for Accurate Distance Calculations
projected_crs = "EPSG:3857"  # Use a global projected CRS like EPSG:3857 (Web Mercator)
countries = countries.to_crs(projected_crs)

# Step 2: Generate Centroids for Each Country Boundary in Projected CRS
countries["centroid"] = countries.geometry.centroid
centroids = countries[["shapeName", "centroid"]].copy()
centroids = centroids.set_geometry("centroid")

# Save Centroids to File for Debugging
centroids.to_file(f"{intermediate_output_dir}country_centroids.shp")
print("Saved country centroids for debugging.")

# Step 3: Extract Centroid Coordinates for Voronoi Seed Points
centroid_coords = np.array([(point.x, point.y) for point in centroids.geometry])
country_names = countries["shapeName"].tolist()  # or another column representing the country name

# Step 4: Create Voronoi Diagram Based on Centroids
vor = Voronoi(centroid_coords)

# Convert Voronoi regions to polygons
voronoi_polygons = []
for region in vor.regions:
    if not -1 in region and region:  # Ignore regions with points at infinity
        polygon_points = [vor.vertices[i] for i in region]
        polygon = Polygon(polygon_points)
        voronoi_polygons.append(polygon)

# Step 5: Assign Each Voronoi Cell a Country Based on Centroid
voronoi_gdf = gpd.GeoDataFrame({
    "geometry": voronoi_polygons,
    "country": country_names[:len(voronoi_polygons)]  # Assign country names to Voronoi cells
}, crs=projected_crs)

# Save Voronoi Polygons for Debugging
voronoi_gdf.to_file(f"{intermediate_output_dir}voronoi_polygons.shp")
print("Saved Voronoi polygons for debugging.")

# Step 6: Buffer Each Country to Ensure Border Consistency in Projected CRS
buffered_countries = countries.copy()
buffered_countries["geometry"] = buffered_countries.geometry.buffer(10000)  # Buffer by 10 km

# Save Buffered Countries for Debugging
buffered_countries.to_file(f"{intermediate_output_dir}buffered_countries.shp")
print("Saved buffered country boundaries for debugging.")

# Step 7: Create "Outside But Nearest To" (OBNT) Polygons
# Overlay buffered countries on Voronoi cells, and identify OBNT areas
obnt_polygons = []
for idx, row in voronoi_gdf.iterrows():
    voronoi_cell = row["geometry"]
    country_name = row["country"]
    
    # Check if this Voronoi cell overlaps with any buffered country
    overlaps = buffered_countries[buffered_countries.geometry.intersects(voronoi_cell)]
    
    if overlaps.empty:
        # If no overlaps, create an OBNT label and save the Voronoi cell as an OBNT polygon
        obnt_polygons.append({
            "geometry": voronoi_cell,
            "country": f"OBNT_{country_name}"
        })

# Convert OBNT polygons into a GeoDataFrame
obnt_gdf = gpd.GeoDataFrame(obnt_polygons, crs=projected_crs)

# Save OBNT Polygons for Debugging
obnt_gdf.to_file(f"{intermediate_output_dir}obnt_polygons.shp")
print("Saved OBNT polygons for debugging.")

# Step 8: Combine Original Boundaries with OBNT Polygons and Reproject to Geographic CRS
combined_gdf = gpd.GeoDataFrame(pd.concat([buffered_countries, obnt_gdf], ignore_index=True), crs=projected_crs)
combined_gdf = combined_gdf.to_crs("EPSG:4326")  # Reproject back to geographic CRS if needed

# Step 9: Save Combined Data as a New Shapefile
combined_gdf.to_file(output_path)
print(f"Interpolated shapefile with OBNT regions saved to {output_path}")
