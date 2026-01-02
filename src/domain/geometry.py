import numpy as np
from src.constants import EARTH_RADIUS_M


def latlon_to_xy(lat: float, lon: float, lat0: float, lon0: float) -> np.ndarray:
    """
    Convert lon/lat to XY coordinates.
    Args:
        lat: Latitude
        lon: Longitude
        lat0: Reference latitude
        lon0: Reference longitude
    Returns:
        Numpy array of (x, y) in meters
    """
    lat = np.radians(lat)
    lon = np.radians(lon)
    lat0 = np.radians(lat0)
    lon0 = np.radians(lon0)

    x = (lon - lon0) * np.cos(lat0) * EARTH_RADIUS_M
    y = (lat - lat0) * EARTH_RADIUS_M
    return np.array([x, y])


def xy_to_lonlat(x: float, y: float, lat0: float, lon0: float) -> tuple:
    """
    Convert XY coordinates to lon/lat.

    Args:
        x: X coordinate in meters
        y: Y coordinate in meters
        lat0: Reference latitude
        lon0: Reference longitude

    Returns:
        Tuple of (longitude, latitude)
    """
    lon = lon0 + (x / (EARTH_RADIUS_M * np.cos(np.radians(lat0)))) * 180 / np.pi
    lat = lat0 + (y / EARTH_RADIUS_M) * 180 / np.pi
    return lon, lat
