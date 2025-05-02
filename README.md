# satellite-image-classification
This is the thesis project of Chloe Schueller

# Water Classification System
This Python script provides a complete workflow for classifying water bodies (lakes and rivers) from satellite imagery using machine learning.

FILE: convert_to_tif.py
## Functions
### convert_jp2_to_geotiff(jp2_path, output_dir)
Converts Sentinel2 jp2 files to tif while altering the actual path and file name.

FILE: svm_second.ipynb
## Functions
### load_polygons(shapefile_path, class_field='land_type')
Loads polygon training data from a shapefile containing classified areas (lake, river, land).
- **Parameters:**
  - `shapefile_path`: Path to the shapefile with labeled polygons
  - `class_field`: Field name containing class labels
- **Returns:** GeoDataFrame with polygons and numeric class labels

### load_band(band_path)
Loads a single spectral band from a raster file.
- **Parameters:**
  - `band_path`: Path to the band file
- **Returns:** Dictionary with band data, transform, CRS, and profile

### load_bands(band_paths)
Loads multiple spectral bands from specified file paths.
- **Parameters:**
  - `band_paths`: Dictionary with band names as keys and file paths as values
- **Returns:** Dictionary with loaded band data

### calculate_indices(bands)
Calculates water and vegetation indices (NDWI, NDVI) from spectral bands.
- **Parameters:**
  - `bands`: Dictionary with loaded band data
- **Returns:** Dictionary with calculated indices

### process_single_image(image_idx, band_paths, polygons_gdf, max_samples_per_polygon=10000, all_touched=True, min_valid_ratio=0.1)
Processes a single satellite image and extracts features from overlapping polygons.
- **Parameters:**
  - `image_idx`: Index of the image being processed
  - `band_paths`: Dictionary with paths to spectral bands
  - `polygons_gdf`: GeoDataFrame with training polygons
  - `max_samples_per_polygon`: Maximum number of pixels to sample from each polygon
  - `all_touched`: Whether to include pixels partially covered by polygons
  - `min_valid_ratio`: Minimum ratio of valid pixels required
- **Returns:** Feature array, labels array, and polygon IDs

### create_training_dataset(band_paths_list, polygons_gdf, max_samples_per_polygon=10000, all_touched=True, min_valid_ratio=0.1)
Creates a training dataset by processing multiple satellite images.
- **Parameters:**
  - `band_paths_list`: List of dictionaries with paths to spectral bands
  - `polygons_gdf`: GeoDataFrame with training polygons
  - `max_samples_per_polygon`: Maximum pixels to sample per polygon
  - `all_touched`: Whether to include pixels partially covered by polygons
  - `min_valid_ratio`: Minimum ratio of valid pixels required
- **Returns:** Feature array, labels array, polygon IDs, and feature names

### train_water_model(X, y, polygon_ids, model_type='rf', max_samples=500000)
Trains a machine learning model for water classification with robust validation.
- **Parameters:**
  - `X`: Feature array
  - `y`: Labels array
  - `polygon_ids`: Array of polygon IDs for each sample
  - `model_type`: Model type ('rf' for Random Forest, 'svm' for SVM)
  - `max_samples`: Maximum number of samples for training
- **Returns:** Dictionary with trained model and performance metrics

### apply_model_to_image(model_results, band_paths, output_path, model_type='rf', probabilities=False, batch_size=1000000)
Applies the trained model to a new satellite image for water classification.
- **Parameters:**
  - `model_results`: Dictionary with trained models and metrics
  - `band_paths`: Dictionary with paths to spectral bands
  - `output_path`: Path to save classification results
  - `model_type`: Model type ('rf' for Random Forest, 'svm' for SVM)
  - `probabilities`: Whether to save probability maps
  - `batch_size`: Size of batches for processing large images
- **Returns:** Classification array

### check_spatial_autocorrelation(X, y, polygon_ids, distance_threshold=100)
Checks for spatial autocorrelation in results to validate model performance.
- **Parameters:**
  - `X`: Feature array
  - `y`: Labels array
  - `polygon_ids`: Array of polygon IDs
  - `distance_threshold`: Distance threshold for nearby pixels
- **Returns:** Ratio of nearby pixels with the same class label

### create_enhanced_visualization(classification, bands, output_path)
Creates an enhanced visualization with RGB background and classified water overlay.
- **Parameters:**
  - `classification`: Classification array
  - `bands`: Dictionary with loaded band data
  - `output_path`: Path to save visualization

### extract_water_boundaries(classification, output_path, class_id=1, min_area=1000)
Extracts water boundaries as vector polygons from the classification results.
- **Parameters:**
  - `classification`: Classification array
  - `output_path`: Path to save vector file
  - `class_id`: ID of the class to extract (1 for lakes, 2 for rivers)
  - `min_area`: Minimum area in pixels to keep a polygon

### create_visualization(classification, output_path)
Creates a simple colored visualization of the classification results.
- **Parameters:**
  - `classification`: Classification array
  - `output_path`: Path to save visualization

### main(band_paths_list, shapefile_path, output_dir, class_field='land_type', model_type='rf', max_samples_per_polygon=10000, max_training_samples=500000, all_touched=True, min_valid_ratio=0.1)
Main function that orchestrates the entire water classification workflow.
- **Parameters:**
  - `band_paths_list`: List of dictionaries with paths to spectral bands
  - `shapefile_path`: Path to shapefile with polygon classifications
  - `output_dir`: Directory to save outputs
  - `class_field`: Field in shapefile with class labels
  - `model_type`: Model type ('rf', 'svm', or 'both')
  - `max_samples_per_polygon`: Maximum samples per polygon
  - `max_training_samples`: Maximum samples for model training
  - `all_touched`: Whether to include partially covered pixels
  - `min_valid_ratio`: Minimum ratio of valid pixels required
- **Returns:** Dictionary with model results


Interpreting Results:
1. Model Performance Metrics
When the model is trained, it prints a classification report with these key metrics:

Accuracy: Overall percentage of correctly classified pixels
Precision: For each class, what percentage of pixels predicted as that class were correct (TP/(TP+FP))
Recall: For each class, what percentage of pixels of that class were correctly identified (TP/(TP+FN))
F1-score: Harmonic mean of precision and recall (2 * (precision * recall) / (precision + recall))

The higher these values (closer to 1.0), the better the model performance. Pay special attention to the class-specific metrics to ensure all classes (land, lake, river) are being detected well.
2. Confusion Matrix
The confusion matrix shows the count of predictions vs. actual classes. The rows represent the actual classes and columns represent the predicted classes. A perfect model would have values only on the diagonal. Numbers off the diagonal represent errors.
For example, if you see a high number in row 1 (lake), column 2 (river), it means many lake pixels are being misclassified as river.
3. Feature Importance
For the Random Forest model, the code saves a CSV file with feature importance values, which tells you which spectral bands (Blue, Green, Red, NIR) contribute most to the classification. Higher values indicate more important features. This can help understand which wavelengths are most useful for distinguishing water bodies.
4. Output Files
The system produces several output files in your specified output directory:

Classification Raster (.tif): Contains pixel-level classifications (0=land, 1=lake, 2=river)
Probability Maps (_*_prob.tif): For each class, shows the probability of each pixel belonging to that class (values from 0 to 1)
Enhanced Visualization (_viz.png): RGB image with colored overlay showing water classes
Vector Water Boundaries (.shp): Shapefiles containing boundaries of detected lakes and rivers

5. Spatial Autocorrelation Report
The code checks for spatial autocorrelation, which helps identify if the model performance is artificially high due to spatial dependence in nearby pixels. If this ratio is high (>0.8), it suggests strong spatial autocorrelation, which could mean the model is relying too heavily on the spatial patterns rather than learning the true spectral signatures.
6. Logs
The system creates a detailed log file in the output directory that records all processing steps, warnings, and errors. This is valuable for troubleshooting if anything goes wrong.
To evaluate the overall success of your water classification:

First check the accuracy metrics (should be >80% for a good model)
Visually inspect the enhanced visualization to confirm water features look correct
Examine the vector boundaries to ensure they match actual water features
If there are issues, look at the probability maps to see where the model is uncertain

The model is designed to distinguish between lakes, rivers, and land, focusing solely on the spectral signatures from the base bands (Blue, Green, Red, NIR) rather than using derived indices.