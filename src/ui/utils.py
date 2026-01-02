import pandas as pd
import numpy as np
from src.constants import EARTH_RADIUS_M


def create_callsign_map(snapshot: pd.DataFrame) -> dict:
    """
    Create a mapping from ICAO24 to callsign.

    Args:
        snapshot: DataFrame containing aircraft states

    Returns:
        Dictionary mapping ICAO24 to callsign
    """
    return snapshot.set_index("icao24")["callsign"].fillna("").to_dict()


def label_aircraft(icao: str, callsign_map: dict) -> str:
    """
    Get display label for an aircraft.

    Args:
        icao: ICAO24 identifier
        callsign_map: Dictionary mapping ICAO24 to callsign

    Returns:
        Display label (callsign if available, otherwise ICAO24)
    """
    cs = callsign_map.get(icao, "").strip()
    return f"{cs}" if cs else icao


def project_future_positions(aircraft_state, lat0, lon0, lookahead, step=10):
    """
    Project future positions of an aircraft.

    Args:
        aircraft_state: AircraftState object
        lat0: Reference latitude for projection
        lon0: Reference longitude for projection
        lookahead: Look-ahead time in seconds
        step: Time step in seconds for sampling

    Returns:
        List of [lon, lat] coordinates
    """
    future_points = []
    time_steps = np.arange(0, lookahead + 1, step)

    for dt in time_steps:
        future_pos = aircraft_state.position_xy(lat0, lon0) + aircraft_state.velocity_vector() * dt
        future_lon = lon0 + (future_pos[0] / (EARTH_RADIUS_M * np.cos(np.radians(lat0)))) * 180 / np.pi
        future_lat = lat0 + (future_pos[1] / EARTH_RADIUS_M) * 180 / np.pi
        future_points.append([future_lon, future_lat])

    return future_points


def get_view_center(snapshot, a_id=None, b_id=None, df=None, current_time=None):
    """
    Calculate the view center for the map.

    Args:
        snapshot: Current snapshot DataFrame
        a_id: First selected aircraft ICAO24
        b_id: Second selected aircraft ICAO24
        df: Full dataframe (for historical lookup)
        current_time: Current timestamp

    Returns:
        Tuple of (latitude, longitude, zoom_level)
    """
    # If both aircraft are selected
    if a_id and b_id and df is not None and current_time is not None:
        a_in_snapshot = a_id in snapshot["icao24"].values
        b_in_snapshot = b_id in snapshot["icao24"].values

        if a_in_snapshot and b_in_snapshot:
            a_row = snapshot[snapshot["icao24"] == a_id].iloc[0]
            b_row = snapshot[snapshot["icao24"] == b_id].iloc[0]
            view_lat = np.mean([a_row["lat"], b_row["lat"]])
            view_lon = np.mean([a_row["lon"], b_row["lon"]])
            return view_lat, view_lon, 7.5
        else:
            # Try to find their last known positions
            a_last = df[df["icao24"] == a_id][df["time"] <= current_time].sort_values("time").tail(1)
            b_last = df[df["icao24"] == b_id][df["time"] <= current_time].sort_values("time").tail(1)

            positions = []
            if not a_last.empty:
                positions.append((a_last.iloc[0]["lat"], a_last.iloc[0]["lon"]))
            if not b_last.empty:
                positions.append((b_last.iloc[0]["lat"], b_last.iloc[0]["lon"]))

            if positions:
                view_lat = np.mean([p[0] for p in positions])
                view_lon = np.mean([p[1] for p in positions])
                return view_lat, view_lon, 7.5

    # Default view
    if not snapshot.empty:
        return snapshot["lat"].mean(), snapshot["lon"].mean(), 5.3
    else:
        return 51, 10, 5.3  # Central Europe
