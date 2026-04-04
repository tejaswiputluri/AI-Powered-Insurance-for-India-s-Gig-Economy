"""
Tile Fetcher — Downloads NASA POWER satellite tiles for Bengaluru region.
Used to build training dataset for CNN weather verification model.

Source: NASA POWER satellite imagery
Region: Bengaluru (12.8–13.1 lat, 77.5–77.8 lon)
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Bengaluru bounding box
BENGALURU_BOUNDS = {
    "lat_min": 12.80,
    "lat_max": 13.10,
    "lon_min": 77.50,
    "lon_max": 77.80,
}

TILE_SIZE = 224
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "data" / "satellite_tiles"


async def fetch_tile(lat: float, lon: float, date_str: str) -> bytes:
    """
    Fetch a satellite tile from NASA POWER API.

    Args:
        lat: Latitude
        lon: Longitude
        date_str: Date in YYYY-MM-DD format

    Returns:
        Raw image bytes (PNG)
    """
    import httpx

    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": date_str.replace("-", ""),
        "end": date_str.replace("-", ""),
        "format": "JSON",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.content
    except Exception as e:
        logger.error(f"Failed to fetch tile: {e}")
        return b""


def setup_tile_directories():
    """Create directories for labeled satellite tiles."""
    categories = ["clear", "light_rain", "heavy_rain", "flood_risk"]
    for cat in categories:
        (OUTPUT_DIR / cat).mkdir(parents=True, exist_ok=True)
    logger.info(f"Tile directories created at {OUTPUT_DIR}")


if __name__ == "__main__":
    setup_tile_directories()
    print(f"Satellite tile directories created at: {OUTPUT_DIR}")
    print("Run fetch_tile() to download tiles from NASA POWER API.")
