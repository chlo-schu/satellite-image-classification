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
    
    Returns:
    list: Paths to clipped raster files
    """
    # Validate input paths
    for path in raster_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Raster file not found: {path}")
    
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")

    # Read shapefile and get clip geometry
    clip_shape = gpd.read_file(shapefile_path)
    
    # Assume first raster for CRS
    with rasterio.open(raster_paths[0]) as src:
        raster_crs = src.crs
    
    # Reproject shapefile to raster CRS
    clip_shape = clip_shape.to_crs(raster_crs)
    geometry = clip_shape.geometry

    # Store clipped raster paths
    clipped_raster_paths = []

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
        
        clipped_raster_paths.append(output_path)
        print(f"Saved clipped raster: {output_path}")
    
    return clipped_raster_paths

def calculate_ndwi(green_path, nir_path):
    """
    Calculate Normalized Difference Water Index (NDWI)
    
    Args:
    green_path (str): Path to Green band raster
    nir_path (str): Path to NIR band raster
    
    Returns:
    tuple: (ndwi array, raster metadata)
    """
    # Read Green and NIR bands
    with rasterio.open(green_path) as green, rasterio.open(nir_path) as nir:
        green_data = green.read(1).astype(float)
        nir_data = nir.read(1).astype(float)
        
        # Use green band's metadata for output
        raster_meta = green.meta.copy()

    # NDWI calculation with zero division handling
    with np.errstate(divide='ignore', invalid='ignore'):
        ndwi = (green_data - nir_data) / (green_data + nir_data)
    
    # Replace inf and NaN with 0
    ndwi = np.nan_to_num(ndwi, nan=0.0, posinf=0.0, neginf=0.0)
    
    return ndwi, raster_meta

def visualize_water_masks(ndwi, raster_meta, thresholds=None):
    """
    Visualize water masks at different NDWI thresholds
    
    Args:
    ndwi (numpy.ndarray): NDWI values
    raster_meta (dict): Raster metadata for saving
    thresholds (list, optional): List of thresholds to apply
    """
    if thresholds is None:
        thresholds = [0.0, 0.1, 0.2]
    
    fig, axs = plt.subplots(1, len(thresholds), figsize=(15, 5))
    
    for i, thresh in enumerate(thresholds):
        water_mask = ndwi > thresh
        im = axs[i].imshow(water_mask, cmap='Blues')
        axs[i].set_title(f'Water Mask (Threshold > {thresh})')
        plt.colorbar(im, ax=axs[i])
    
    plt.tight_layout()
    plt.show()

    # Optional: Save water masks as GeoTIFF
    for thresh in thresholds:
        water_mask = (ndwi > thresh).astype(np.uint8)
        output_mask_path = f'water_mask_thresh_{thresh}.tif'
        
        raster_meta.update({
            'dtype': 'uint8',
            'count': 1,
            'compress': 'lzw'
        })
        
        with rasterio.open(output_mask_path, 'w', **raster_meta) as dst:
            dst.write(water_mask, 1)
        print(f"Saved water mask: {output_mask_path}")

def main():
    # Update paths to Sentinel-2 image bands
    raster_paths = [
        '/Users/chloe/Documents/INDSTUDY/S2A_MSIL2A_20240819T213531_N0511_R086_T05VPJ_20240820T004850.SAFE/GRANULE/L2A_T05VPJ_A047845_20240819T213526/IMG_DATA/R10m/B03_10m.jp2',  # Green Band
        '/Users/chloe/Documents/INDSTUDY/S2A_MSIL2A_20240819T213531_N0511_R086_T05VPJ_20240820T004850.SAFE/GRANULE/L2A_T05VPJ_A047845_20240819T213526/IMG_DATA/R10m/B08_10m.jp2'   # NIR Band
    ]
    shapefile_path = '/Users/chloe/Documents/INDSTUDY/box1.shp'

    try:
        # Process and clip rasters
        clipped_rasters = process_sentinel_data(raster_paths, shapefile_path)

        # Calculate NDWI
        ndwi, raster_meta = calculate_ndwi(clipped_rasters[0], clipped_rasters[1])

        # Visualize water masks
        visualize_water_masks(ndwi, raster_meta)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()