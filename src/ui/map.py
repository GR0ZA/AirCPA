import streamlit as st
import pydeck as pdk
import numpy as np
from src.domain.aircraft import AircraftState
from src.ui.utils import project_future_positions, get_view_center
from src.domain.geometry import xy_to_lonlat


def create_base_layer(snapshot):
    """Create base aircraft layer showing all aircraft."""
    return pdk.Layer(
        "ScatterplotLayer",
        data=snapshot,
        get_position="[lon, lat]",
        get_radius=1600,
        get_fill_color=[0, 110, 200, 140],
        pickable=True
    )


def create_trajectory_layer(df, icao, current_time, color):
    """
    Create historical trajectory layer for an aircraft.

    Args:
        df: Full dataframe
        icao: Aircraft ICAO24
        current_time: Current timestamp
        color: RGBA color for the trajectory

    Returns:
        PyDeck Layer or None
    """
    time_window = df[df["time"] <= current_time]
    history = time_window[time_window["icao24"] == icao].copy()

    if history.empty:
        return None

    history = history.sort_values("time")
    return pdk.Layer(
        "PathLayer",
        data=[{"path": history[["lon", "lat"]].values.tolist()}],
        get_path="path",
        get_color=color,
        width_scale=1,
        width_min_pixels=2
    )


def create_selected_aircraft_layer(snapshot, a_id, b_id):
    """Create layer highlighting selected aircraft."""
    selected_ids = [x for x in [a_id, b_id] if x]
    if not selected_ids:
        return None

    selected_data = snapshot[snapshot["icao24"].isin(selected_ids)]
    if selected_data.empty:
        return None

    return pdk.Layer(
        "ScatterplotLayer",
        data=selected_data,
        get_position="[lon, lat]",
        get_radius=1600,
        get_fill_color=[220, 20, 60, 230],
        pickable=True
    )


def create_future_trajectory_layer(snapshot, icao, lookahead):
    """
    Create future trajectory layer for an aircraft.

    Args:
        snapshot: Current snapshot DataFrame
        icao: Aircraft ICAO24
        lookahead: Look-ahead time in seconds

    Returns:
        PyDeck Layer or None
    """
    if icao not in snapshot["icao24"].values:
        return None

    row = snapshot[snapshot["icao24"] == icao].iloc[0]
    aircraft_state = AircraftState(
        icao, row["lat"], row["lon"],
        row["velocity"], row["heading"],
        row["baroaltitude"], row["vertrate"]
    )

    lat0 = snapshot["lat"].mean()
    lon0 = snapshot["lon"].mean()

    future_points = project_future_positions(aircraft_state, lat0, lon0, lookahead)

    if not future_points:
        return None

    return pdk.Layer(
        "PathLayer",
        data=[{"path": future_points}],
        get_path="path",
        get_color=[128, 128, 128, 120],
        width_scale=1,
        width_min_pixels=2,
        get_width=2
    )


def create_cpa_circle_layer(conflict_df, a_id, b_id, snapshot, sep_m):
    """
    Create CPA circle layer showing the separation requirement.

    Args:
        conflict_df: DataFrame of conflicts
        a_id: First aircraft ICAO24
        b_id: Second aircraft ICAO24
        snapshot: Current snapshot DataFrame
        sep_m: Separation distance in meters

    Returns:
        PyDeck Layer or None
    """
    # Check if both aircraft are in snapshot
    if a_id not in snapshot["icao24"].values or b_id not in snapshot["icao24"].values:
        return None

    conflict = conflict_df[
        ((conflict_df["a"] == a_id) & (conflict_df["b"] == b_id)) |
        ((conflict_df["a"] == b_id) & (conflict_df["b"] == a_id))
    ]

    if conflict.empty:
        return None

    row = conflict.iloc[0]
    lat0 = snapshot["lat"].mean()
    lon0 = snapshot["lon"].mean()

    cpa_lon, cpa_lat = xy_to_lonlat(row["cpa_x"], row["cpa_y"], lat0, lon0)

    return pdk.Layer(
        "ScatterplotLayer",
        data=[{"lon": cpa_lon, "lat": cpa_lat}],
        get_position="[lon, lat]",
        get_radius=sep_m,
        get_fill_color=[255, 0, 0, 60]
    )


def render_map(snapshot, df, current_time, conflict_df, a_id, b_id, lookahead, sep_m):
    """
    Render the air situation map.

    Args:
        snapshot: Current snapshot DataFrame
        df: Full dataframe
        current_time: Current timestamp
        conflict_df: DataFrame of conflicts
        a_id: First selected aircraft ICAO24
        b_id: Second selected aircraft ICAO24
        lookahead: Look-ahead time in seconds
        sep_m: Separation distance in meters
    """
    st.subheader("Air Situation Map")

    layers = []

    # Base layer - all aircraft
    layers.append(create_base_layer(snapshot))

    # If aircraft are selected, add their layers
    if a_id and b_id:
        # Historical trajectories
        traj_a = create_trajectory_layer(df, a_id, current_time, [255, 100, 100, 150])
        if traj_a:
            layers.append(traj_a)

        traj_b = create_trajectory_layer(df, b_id, current_time, [100, 100, 255, 150])
        if traj_b:
            layers.append(traj_b)

        # Highlight selected aircraft
        selected_layer = create_selected_aircraft_layer(snapshot, a_id, b_id)
        if selected_layer:
            layers.append(selected_layer)

        # Future trajectories
        future_a = create_future_trajectory_layer(snapshot, a_id, lookahead)
        if future_a:
            layers.append(future_a)

        future_b = create_future_trajectory_layer(snapshot, b_id, lookahead)
        if future_b:
            layers.append(future_b)

        # CPA circle
        cpa_layer = create_cpa_circle_layer(conflict_df, a_id, b_id, snapshot, sep_m)
        if cpa_layer:
            layers.append(cpa_layer)

    # Calculate view center
    view_lat, view_lon, view_zoom = get_view_center(
        snapshot, a_id, b_id, df, current_time
    )

    # Create and render deck
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(
            latitude=view_lat,
            longitude=view_lon,
            zoom=view_zoom
        ),
        tooltip={"text": "ICAO: {icao24}\nCallsign: {callsign}"}
    )

    st.pydeck_chart(deck, height=600)
