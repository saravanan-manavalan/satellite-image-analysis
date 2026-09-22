import os
from pystac_client import Client
import planetary_computer as pc
import odc.stac
import matplotlib.pyplot as plt

def fetch_sentinel_data():
    print("🛰️ Connecting to the Planetary Computer STAC API...")
    # Open the open-source public catalog
    catalog = Client.open("https://microsoft.com")
    
    # Define an Area of Interest (Bounding box: [min_lon, min_lat, max_lon, max_lat])
    # This matches a region over Chennai / Morai, Tamil Nadu, India
    bbox = [80.10, 13.15, 80.25, 13.28] 
    
    # Set the timeframe for exploration
    time_range = "2026-01-01/2026-06-30"
    
    print("🔍 Searching for cloud-free Sentinel-2 imagery...")
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=time_range,
        query={"eo:cloud_cover": {"lt": 10}} # Look for less than 10% cloud coverage
    )
    
    # Grab all items that match our filters
    items = search.item_collection()
    print(f"✅ Found {len(items)} matching cloud-free images!")
    
    if len(items) == 0:
        print("❌ No scenes matched your criteria. Try expanding your date range or cloud threshold.")
        return

    # Pick the crispest, lowest-cloud item found
    selected_item = items[0]
    print(f"📷 Selected Scene ID: {selected_item.id}")
    print(f"☁️ Cloud Cover: {selected_item.properties['eo:cloud_cover']:.2f}%")
    
    # Sign the asset URLs with an ephemeral token for open access
    signed_item = pc.sign(selected_item)
    
    # Choose specific bands to stream (Red, Green, Blue for a True Color image)
    bands_to_load = ["B04", "B03", "B02"]
    print(f"📥 Streaming spectral bands {bands_to_load} straight into memory...")
    
    # Load data directly as an xarray dataset wrapped into the boundary box
    data = odc.stac.load(
        [signed_item], 
        bands=bands_to_load, 
        bbox=bbox,
        resolution=10 # Sentinel-2 high-res 10-meter resolution
    )
    
    # Create an output folder if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Extract the individual bands for inspection
    red = data["B04"].data
    green = data["B03"].data
    blue = data["B02"].data
    
    print("🎨 Successfully processed bands! Ready for visualization or index calculation.")
    return selected_item.id

if __name__ == "__main__":
    fetch_sentinel_data()
