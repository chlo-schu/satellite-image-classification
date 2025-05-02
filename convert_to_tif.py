import os
import rasterio
from pathlib import Path

def convert_jp2_to_geotiff(jp2_path, output_dir):
    """
    Convert JP2 file to GeoTIFF and save in a specified directory
    
    Parameters:
    jp2_path: Path to the JP2 file
    output_dir: Base directory to save GeoTIFF files
    
    Returns:
    Path to the saved GeoTIFF file
    """
    jp2_path = Path(jp2_path)
    output_dir = Path(output_dir)
    
    # Extract the filename and create the output path
    filename = jp2_path.name.replace('.jp2', '.tif')
    output_path = output_dir / filename
    
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert file
    try:
        with rasterio.open(jp2_path) as src:
            # Read metadata
            meta = src.meta.copy()
            # Update metadata to GeoTIFF
            meta.update(driver='GTiff')
            # Read data
            data = src.read()
            
            # Write to GeoTIFF
            with rasterio.open(output_path, 'w', **meta) as dst:
                dst.write(data)
                
                # Copy all tags
                tags = src.tags()
                dst.update_tags(**tags)
        
        print(f"Converted: {jp2_path.name} → {output_path}")
        return str(output_path)
    except Exception as e:
        print(f"Error converting {jp2_path.name}: {str(e)}")
        return None

def main():
    """
    Convert all JP2 files in band_paths_list to GeoTIFF format
    """
    # Define paths to Sentinel-2 bands
    band_paths_list = [
        {
            # Image 1
            'blue': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/11.SAFE/GRANULE/L2A_T05VNJ_A033331_20230724T214533/IMG_DATA/R10m/T05VNJ_20230724T214539_B02_10m.jp2",  # Blue band
            'green': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/11.SAFE/GRANULE/L2A_T05VNJ_A033331_20230724T214533/IMG_DATA/R10m/T05VNJ_20230724T214539_B03_10m.jp2", # Green band
            'red': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/11.SAFE/GRANULE/L2A_T05VNJ_A033331_20230724T214533/IMG_DATA/R10m/T05VNJ_20230724T214539_B04_10m.jp2",   # Red band
            'nir': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/11.SAFE/GRANULE/L2A_T05VNJ_A033331_20230724T214533/IMG_DATA/R10m/T05VNJ_20230724T214539_B08_10m.jp2"   # NIR band
        },
        {
            # Image 2
            'blue': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/12.SAFE/GRANULE/L2A_T05VNK_A033288_20230721T213533/IMG_DATA/R10m/T05VNK_20230721T213539_B02_10m.jp2",
            'green': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/12.SAFE/GRANULE/L2A_T05VNK_A033288_20230721T213533/IMG_DATA/R10m/T05VNK_20230721T213539_B03_10m.jp2",
            'red': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/12.SAFE/GRANULE/L2A_T05VNK_A033288_20230721T213533/IMG_DATA/R10m/T05VNK_20230721T213539_B04_10m.jp2",
            'nir': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/12.SAFE/GRANULE/L2A_T05VNK_A033288_20230721T213533/IMG_DATA/R10m/T05VNK_20230721T213539_B08_10m.jp2"
        },
        {
            # Image 3
            'blue': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/21.SAFE/GRANULE/L2A_T05VPJ_A042225_20230723T212524/IMG_DATA/R10m/T05VPJ_20230723T212521_B02_10m.jp2",
            'green': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/21.SAFE/GRANULE/L2A_T05VPJ_A042225_20230723T212524/IMG_DATA/R10m/T05VPJ_20230723T212521_B03_10m.jp2",
            'red': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/21.SAFE/GRANULE/L2A_T05VPJ_A042225_20230723T212524/IMG_DATA/R10m/T05VPJ_20230723T212521_B04_10m.jp2",
            'nir': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/21.SAFE/GRANULE/L2A_T05VPJ_A042225_20230723T212524/IMG_DATA/R10m/T05VPJ_20230723T212521_B08_10m.jp2"
        },
        {
            # Image 4
            'blue': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/22.SAFE/GRANULE/L2A_T06VUQ_A042411_20230805T213615/IMG_DATA/R10m/T06VUQ_20230805T213531_B02_10m.jp2",
            'green': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/22.SAFE/GRANULE/L2A_T06VUQ_A042411_20230805T213615/IMG_DATA/R10m/T06VUQ_20230805T213531_B03_10m.jp2",
            'red': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/22.SAFE/GRANULE/L2A_T06VUQ_A042411_20230805T213615/IMG_DATA/R10m/T06VUQ_20230805T213531_B04_10m.jp2",
            'nir': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/22.SAFE/GRANULE/L2A_T06VUQ_A042411_20230805T213615/IMG_DATA/R10m/T06VUQ_20230805T213531_B08_10m.jp2"
        },
        {
            # Image 5
            'blue': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/31.SAFE/GRANULE/L2A_T06VWP_A034246_20230926T212653/IMG_DATA/R10m/T06VWP_20230926T212529_B02_10m.jp2",
            'green': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/31.SAFE/GRANULE/L2A_T06VWP_A034246_20230926T212653/IMG_DATA/R10m/T06VWP_20230926T212529_B03_10m.jp2",
            'red': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/31.SAFE/GRANULE/L2A_T06VWP_A034246_20230926T212653/IMG_DATA/R10m/T06VWP_20230926T212529_B04_10m.jp2",
            'nir': "/Users/chloe/Documents/INDSTUDY/Training Data Images/Polygon_Extraction_images/31.SAFE/GRANULE/L2A_T06VWP_A034246_20230926T212653/IMG_DATA/R10m/T06VWP_20230926T212529_B08_10m.jp2"
        }
    ]
    
    # Specify output directory for GeoTIFF files
    output_dir = "/Users/chloe/Documents/INDSTUDY/Training Data Images/GeoTIFF"
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Dictionary to store new paths
    new_band_paths_list = []
    
    # Process each image
    for i, band_paths in enumerate(band_paths_list):
        print(f"\nProcessing image {i+1}/{len(band_paths_list)}")
        
        new_band_paths = {}
        for band_name, band_path in band_paths.items():
            # Create a subdirectory for each image
            image_dir = Path(output_dir) / f"image_{i+1}"
            os.makedirs(image_dir, exist_ok=True)
            
            # Convert to GeoTIFF
            new_path = convert_jp2_to_geotiff(band_path, image_dir)
            new_band_paths[band_name] = new_path
        
        new_band_paths_list.append(new_band_paths)
    
    # Save the new paths to a file for reference
    paths_file = os.path.join(output_dir, "geotiff_paths.txt")
    with open(paths_file, 'w') as f:
        for i, band_paths in enumerate(new_band_paths_list):
            f.write(f"Image {i+1}:\n")
            for band_name, path in band_paths.items():
                f.write(f"  {band_name}: {path}\n")
            f.write("\n")
    
    print(f"\nConversion complete. New paths saved to: {paths_file}")
    print(f"GeoTIFF files are in: {output_dir}")
    
    # Return the new paths for use in your classification code
    return new_band_paths_list

if __name__ == "__main__":
    new_paths = main()