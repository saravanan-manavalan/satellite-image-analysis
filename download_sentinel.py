import os
import numpy as np
from pystac_client import Client
import planetary_computer as pc
import odc.stac
import matplotlib.pyplot as plt

def fetch_sentinel_data():
    print("🛰️ Connecting to the Planetary Computer STAC API...")
    # Open the open-source public catalog
    catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

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

    # Choose specific bands to stream (B08: Near-Infrared, B04: Red, B03: Green, B02: Blue)
    bands_to_load = ["B08", "B04", "B03", "B02"]
    print(f"📥 Streaming spectral bands {bands_to_load} straight into memory...")

    # Load data directly as an xarray dataset wrapped into the boundary box
    data = odc.stac.load(
        [signed_item],
        bands=bands_to_load,
        bbox=bbox,
        resolution=10 # Sentinel-2 high-res 10-meter resolution
    )

    # Extract single arrays and convert to float for division calculations, drop time dimension
    nir = data["B08"].isel(time=0).astype(float)
    red = data["B04"].isel(time=0).astype(float)
    green = data["B03"].isel(time=0).astype(float)
    blue = data["B02"].isel(time=0).astype(float)

    print("🧮 Calculating NDVI (Normalized Difference Vegetation Index)...")
    # Add a tiny value (1e-10) to the denominator to prevent division-by-zero errors
    ndvi = (nir - red) / (nir + red + 1e-10)

    print("🎨 Normalizing True-Color bands for visual display...")
    # Stack bands into an RGB layout and scale values so the image isn't pitch black
    rgb = np.stack([red, green, blue], axis=-1)
    rgb = np.clip(rgb / 3000, 0, 1)

    # Create an output folder if it doesn't exist
    os.makedirs("output", exist_ok=True)

    print("🖼️ Generating side-by-side analysis plot...")
    fig, ax = plt.subplots(1, 2, figsize=(14, 7))

    # Panel 1: True Color View
    ax[0].imshow(rgb)
    ax[0].set_title("True Color (As Human Eyes See It)")
    ax[0].axis("off")

    # Panel 2: NDVI Heatmap View
    im = ax[1].imshow(ndvi, cmap="RdYlGn", vmin=-0.2, vmax=0.8)
    ax[1].set_title("NDVI Vegetation Health Index Map")
    ax[1].axis("off")

    # Add a color bar scale legend
    cbar = fig.colorbar(im, ax=ax, shrink=0.7)
    cbar.set_label("NDVI Value (Healthy Greens > 0.4)", rotation=270, labelpad=15)

    plt.tight_layout()
    
    # Save a hard copy to your output folder
    output_path = os.path.join("output", f"ndvi_analysis_{selected_item.id}.png")
    plt.savefig(output_path, dpi=300)
    print(f"💾 Analysis plot saved locally to: {output_path}")
    
    plt.show()
    return selected_item.id

if __name__ == "__main__":
    fetch_sentinel_data()
