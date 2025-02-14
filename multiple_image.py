import rasterio
from rasterio.mask import mask
from rasterio.merge import merge
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

def process_sentinel_data(raster_paths_list, shapefile_path):
    """
    Process multiple Sentinel-2 raster datasets with clipping and merging
    
    Args:
    raster_paths_list (list): List of lists, where each inner list contains paths to bands for one scene
    shapefile_path (str): Path to shapefile for clipping
    
    Returns:
    list: Paths to merged and clipped raster files for each band
    """
    # Validate input paths
    for paths in raster_paths_list:
        for path in paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Raster file not found: {path}")
    
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")

    # Read shapefile and get clip geometry
    clip_shape = gpd.read_file(shapefile_path)
    
    # Get CRS from first raster
    with rasterio.open(raster_paths_list[0][0]) as src:
        raster_crs = src.crs
    
    # Reproject shapefile to raster CRS
    clip_shape = clip_shape.to_crs(raster_crs)
    geometry = clip_shape.geometry

    # Store merged and clipped raster paths
    final_raster_paths = []

    # Process each band separately
    num_bands = len(raster_paths_list[0])
    for band_idx in range(num_bands):
        # Create a list to store opened datasets
        opened_datasets = []
        
        try:
            # Open all datasets for this band
            for scene_paths in raster_paths_list:
                src = rasterio.open(scene_paths[band_idx])
                opened_datasets.append(src)
            
            # Merge scenes for this band
            mosaic, transform = merge(opened_datasets)
            
            # Create metadata for merged raster
            merged_meta = opened_datasets[0].meta.copy()
            merged_meta.update({
                'height': mosaic.shape[1],
                'width': mosaic.shape[2],
                'transform': transform
            })

            # Save temporary merged file
            temp_merged_path = f'temp_merged_band_{band_idx}.tif'
            with rasterio.open(temp_merged_path, 'w', **merged_meta) as dst:
                dst.write(mosaic)

            # Clip merged raster
            with rasterio.open(temp_merged_path) as src:
                clipped_raster, clipped_transform = mask(src, geometry, crop=True)
                clipped_meta = src.meta.copy()

            # Update metadata for clipped raster
            clipped_meta.update({
                'height': clipped_raster.shape[1],
                'width': clipped_raster.shape[2],
                'transform': clipped_transform
            })

            # Save final clipped raster
            output_path = f'merged_clipped_band_{band_idx}.tif'
            with rasterio.open(output_path, 'w', **clipped_meta) as dst:
                dst.write(clipped_raster)
            
            final_raster_paths.append(output_path)
            print(f"Saved merged and clipped raster: {output_path}")
            
            # Clean up temporary file
            if os.path.exists(temp_merged_path):
                os.remove(temp_merged_path)

        finally:
            # Make sure to close all opened datasets
            for dataset in opened_datasets:
                dataset.close()

    return final_raster_paths
    
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

def visualize_water_masks(ndwi, raster_meta, thresholds=None, title_prefix=""):
    """
    Visualize water masks at different NDWI thresholds
    
    Args:
    ndwi (numpy.ndarray): NDWI values
    raster_meta (dict): Raster metadata for saving
    thresholds (list, optional): List of thresholds to apply
    title_prefix (str): Prefix for plot titles
    """
    if thresholds is None:
        thresholds = [0.0, 0.1, 0.2]
    
    fig, axs = plt.subplots(1, len(thresholds), figsize=(15, 5))
    
    for i, thresh in enumerate(thresholds):
        water_mask = ndwi > thresh
        im = axs[i].imshow(water_mask, cmap='Blues')
        axs[i].set_title(f'{title_prefix}Water Mask (Threshold > {thresh})')
        plt.colorbar(im, ax=axs[i])
    
    plt.tight_layout()
    plt.show()

def main():
    # Example of multiple scenes - update these paths for your data
    raster_paths_list = [
        # Scene 1
        [
            '/Users/chloe/Documents/INDSTUDY/S2A_MSIL2A_20240819T213531_N0511_R086_T05VPJ_20240820T004850.SAFE/GRANULE/L2A_T05VPJ_A047845_20240819T213526/IMG_DATA/R10m/B03_10m.jp2',  # Green Band
            '/Users/chloe/Documents/INDSTUDY/S2A_MSIL2A_20240819T213531_N0511_R086_T05VPJ_20240820T004850.SAFE/GRANULE/L2A_T05VPJ_A047845_20240819T213526/IMG_DATA/R10m/B08_10m.jp2'
        ],
        # Scene 2
        [
            '/Users/chloe/Documents/INDSTUDY/S2B_MSIL2A_20230926T212529_N0509_R043_T05VPJ_20230926T232522.SAFE/GRANULE/L2A_T05VPJ_A034246_20230926T212653/IMG_DATA/R10m/B03_10m.jp2',  # Green Band
            '/Users/chloe/Documents/INDSTUDY/S2B_MSIL2A_20230926T212529_N0509_R043_T05VPJ_20230926T232522.SAFE/GRANULE/L2A_T05VPJ_A034246_20230926T212653/IMG_DATA/R10m/B08_10m.jp2'
        ]
        # Add more scenes as needed
    ]
    
    shapefile_path = '/Users/chloe/Documents/INDSTUDY/box1.shp'

    try:
        # Process and clip rasters
        merged_rasters = process_sentinel_data(raster_paths_list, shapefile_path)

        # Calculate NDWI
        ndwi, raster_meta = calculate_ndwi(merged_rasters[0], merged_rasters[1])

        # Visualize water masks
        thresholds = [0.0, 0.1, 0.2]
        visualize_water_masks(ndwi, raster_meta, thresholds)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()