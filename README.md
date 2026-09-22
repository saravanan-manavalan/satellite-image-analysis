# Satellite Image Analysis 🛰️

A clean, modern Python pipeline designed to programmatically search, filter, and stream high-resolution **Sentinel-2 satellite imagery** directly from cloud providers without downloading massive, unneeded imagery files. 

This repository leverages the open-source **STAC (SpatioTemporal Asset Catalog) API** standard to efficiently target specific regions, control for cloud-cover thresholds, and isolate discrete spectral bands for remote sensing analysis.

## 🚀 Key Features
* **Cloud-Optimized Streaming:** Connects to the Planetary Computer STAC API to stream pixel data straight into memory (`xarray` arrays) without heavy local downloads.
* **Automated Cloud Filtering:** Instantly filters out satellite passes containing excessive cloud interference (e.g., `< 10%` cloud cover).
* **Precise Geospatial Targeting:** Uses bounding boxes (`bbox`) to isolate exact coordinates (pre-configured for geographic regions in Tamil Nadu, India).
* **Multi-Band Extraction:** Seamlessly extracts raw True-Color (Red, Green, Blue) channels, laying the framework for advanced index generation (like NDVI or NDWI).

## 📂 Project Structure
* `download_sentinel.py` - Core Python script that queries the STAC API catalog, processes metadata, and handles memory streaming.
* `requirements.txt` - Complete list of open-source geospatial dependencies required to run the pipeline.

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd satellite-image-analysis
   ```

2. **Install the required geospatial libraries:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the data pipeline:**
   ```bash
   python download_sentinel.py
   ```

## 📦 Core Technologies Used
* **`pystac-client` & `planetary-computer`** - For interacting with the cloud STAC API catalogs securely.
* **`odc-stac`** - For loading SpatioTemporal Asset Catalogs directly into highly efficient multi-dimensional array structures.
* **`rasterio`** - For working with geospatial raster data layouts.
* **`numpy` & `matplotlib`** - For numerical computation and image visualization processing.
