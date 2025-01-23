import rasterio
from rasterio.mask import mask
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os

def process_sentinel_data(raster_paths, shapefile_path):
    """
    Process Sentinel-2 raster data with clipping and NDWI calculation
    
    Args:
    raster_paths (list): List of paths to Sentinel-2 band rasters
    shapefile_path (str): Path to shapefile for clipping
    """
    # Ensure paths are valid
    for path in raster_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Raster file not found: {path}")
    
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")

    # Read shapefile and get clip geometry
    clip_shape = gpd.read_file(shapefile_path)
    
    # Assume first raster for CRS
    with rasterio.open(raster_paths[0]) as src:
        raster_crs = src.crs  # Corrected from src.ccrs
    
    # Reproject shapefile to raster CRS
    clip_shape = clip_shape.to_crs(raster_crs)
    geometry = clip_shape.geometry

    # Clipping process
    for i, raster_path in enumerate(raster_paths):
        with rasterio.open(raster_path) as src:
            # Clip raster
            clipped_raster, clipped_transform = mask(src, geometry, crop=True)
            clipped_meta = src.meta.copy()

        # Update metadata after clipping
        clipped_meta.update({
            'driver': 'GTiff',
            'height': clipped_raster.shape[1],
            'width': clipped_raster.shape[2],
            'transform': clipped_transform
        })

        # Save clipped raster
        output_path = f'clipped_raster_{i}.tif'
        with rasterio.open(output_path, 'w', **clipped_meta) as dst:
            dst.write(clipped_raster)
        
        print(f"Saved clipped raster: {output_path}")

def calculate_ndwi(nir_path, green_path):
    """
    Calculate Normalized Difference Water Index (NDWI)
    
    Args:
    nir_path (str): Path to NIR band raster
    green_path (str): Path to Green band raster
    
    Returns:
    ndwi (numpy.ndarray): Calculated NDWI values
    """
    # Read NIR and Green bands
    with rasterio.open(nir_path) as nir, rasterio.open(green_path) as green:
        nir_data = nir.read(1).astype(float)
        green_data = green.read(1).astype(float)

    # NDWI calculation with zero division handling
    with np.errstate(divide='ignore', invalid='ignore'):
        ndwi = (green_data - nir_data) / (green_data + nir_data)
    
    # Replace inf and NaN with 0
    ndwi = np.nan_to_num(ndwi, nan=0.0, posinf=0.0, neginf=0.0)
    
    return ndwi

def visualize_water_masks(ndwi, thresholds=None):
    """
    Visualize water masks at different NDWI thresholds
    
    Args:
    ndwi (numpy.ndarray): NDWI values
    thresholds (list, optional): List of thresholds to apply. Defaults to [0.0, 0.1, 0.2]
    """
    if thresholds is None:
        thresholds = [0.0, 0.1, 0.2]
    
    fig, axs = plt.subplots(1, len(thresholds), figsize=(15, 5))
    
    for i, thresh in enumerate(thresholds):
        water_mask = ndwi > thresh
        axs[i].imshow(water_mask, cmap='Blues')
        axs[i].set_title(f'Water Mask (Threshold > {thresh})')
    
    plt.tight_layout()
    plt.show()

def main():
    raster_paths = [
        '/Users/chloe/Documents/INDSTUDY/S2A_MSIL2A_20240819T213531_N0511_R086_T05VPJ_20240820T004850.SAFE/GRANULE/L2A_T05VPJ_A047845_20240819T213526/IMG_DATA/R10m/S2A_MSIL2A_20240819T213531_N0511_R086_T05VPJ_20240820T004850.SAFE/GRANULE/L2A_T05VPJ_A047845_20240819T213526/IMG_DATA/R10m/B08_10m.jp2',  # Green Band
        '/Users/chloe/Documents/INDSTUDY/S2A_MSIL2A_20240819T213531_N0511_R086_T05VPJ_20240820T004850.SAFE/GRANULE/L2A_T05VPJ_A047845_20240819T213526/IMG_DATA/R10m/S2A_MSIL2A_20240819T213531_N0511_R086_T05VPJ_20240820T004850.SAFE/GRANULE/L2A_T05VPJ_A047845_20240819T213526/IMG_DATA/R10m/B03_10m.jp2'   # NIR Band
    ]
    shapefile_path = '/path/to/your/shapefile.shp'

    # Process and clip rasters
    process_sentinel_data(raster_paths, shapefile_path)

    # Calculate NDWI
    ndwi = calculate_ndwi(raster_paths[1], raster_paths[0])  # NIR, Green

    # Visualize water masks
    visualize_water_masks(ndwi)

if __name__ == "__main__":
    main()
