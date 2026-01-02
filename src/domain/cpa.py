import numpy as np
from src.domain.aircraft import AircraftState
from itertools import combinations
import numpy as np
from src.constants import (
    DEFAULT_LOOKAHEAD_S,
    DEFAULT_HORIZONTAL_SEP_NM,
    DEFAULT_VERTICAL_SEP_FT,
    NM_TO_M,
    FT_TO_M,
    MAX_RELATIVE_SPEED_MPS,
)


def compute_cpa(
    relative_position_m: np.ndarray,
    relative_velocity_mps: np.ndarray,
):
    """
    Computes time and distance at closest point of approach (CPA)
    for two aircraft assuming linear motion in the horizontal plane.

    Args:
        relative_position_m: Relative position vector [m]
        relative_velocity_mps: Relative velocity vector [m/s]

    Returns:
        t_cpa_s: Time to CPA in seconds (None if undefined)
        d_cpa_m: Horizontal distance at CPA in meters
    """
    rel_speed_sq = np.dot(relative_velocity_mps, relative_velocity_mps)

    if rel_speed_sq == 0.0:
        return None, np.linalg.norm(relative_position_m)

    t_cpa_s = -np.dot(relative_position_m, relative_velocity_mps) / rel_speed_sq
    d_cpa_m = np.linalg.norm(
        relative_position_m + relative_velocity_mps * t_cpa_s
    )

    return t_cpa_s, d_cpa_m


def detect_conflicts(
    snapshot_df,
    lookahead_s: float = DEFAULT_LOOKAHEAD_S,
    sep_nm: float = DEFAULT_HORIZONTAL_SEP_NM,
    sep_ft: float = DEFAULT_VERTICAL_SEP_FT,
):
    """
    Detects predicted loss of separation events using deterministic
    Closest Point of Approach (CPA) analysis.

    Horizontal and vertical separation are evaluated independently.

    Args:
        snapshot_df: ADS-B state snapshot at a single timestamp
        lookahead_s: Look-ahead horizon [s]
        sep_nm: Horizontal separation minimum [NM]
        sep_ft: Vertical separation minimum [ft]

    Returns:
        List of detected conflict dictionaries
    """
    horizontal_sep_m = sep_nm * NM_TO_M
    vertical_sep_m = sep_ft * FT_TO_M

    max_initial_distance_m = (
        MAX_RELATIVE_SPEED_MPS * lookahead_s + horizontal_sep_m
    )

    lat_ref = snapshot_df["lat"].mean()
    lon_ref = snapshot_df["lon"].mean()

    aircraft_states = [
        AircraftState(
            icao24=row["icao24"],
            lat_deg=row["lat"],
            lon_deg=row["lon"],
            velocity_mps=row["velocity"],
            heading_deg=row["heading"],
            altitude_m=row["baroaltitude"],
            vertical_rate_mps=row["vertrate"],
        )
        for _, row in snapshot_df.iterrows()
    ]

    position_xy_m = {
        ac.icao24: ac.position_xy(lat_ref, lon_ref)
        for ac in aircraft_states
    }
    velocity_xy_mps = {
        ac.icao24: ac.velocity_vector()
        for ac in aircraft_states
    }

    conflicts = []

    for ownship, intruder in combinations(aircraft_states, 2):
        rel_position_m = (
            position_xy_m[intruder.icao24]
            - position_xy_m[ownship.icao24]
        )

        # Horizontal distance pre-filter
        if np.linalg.norm(rel_position_m) > max_initial_distance_m:
            continue

        rel_velocity_mps = (
            velocity_xy_mps[intruder.icao24]
            - velocity_xy_mps[ownship.icao24]
        )

        t_cpa_s, d_cpa_m = compute_cpa(
            rel_position_m, rel_velocity_mps
        )

        if t_cpa_s is None or not (0.0 < t_cpa_s <= lookahead_s):
            continue

        if d_cpa_m >= horizontal_sep_m:
            continue

        # Vertical separation check
        if (
            ownship.altitude_m is None
            or intruder.altitude_m is None
        ):
            continue

        initial_vertical_sep_m = (
            intruder.altitude_m - ownship.altitude_m
        )

        relative_vertical_rate_mps = (
            intruder.vertical_rate_mps - ownship.vertical_rate_mps
        )

        vertical_sep_at_cpa_m = (
            initial_vertical_sep_m
            + relative_vertical_rate_mps * t_cpa_s
        )

        if abs(vertical_sep_at_cpa_m) >= vertical_sep_m:
            continue

        ownship_cpa_xy_m = (
            position_xy_m[ownship.icao24]
            + velocity_xy_mps[ownship.icao24] * t_cpa_s
        )

        conflicts.append({
            "a": ownship.icao24,
            "b": intruder.icao24,
            "t_cpa": t_cpa_s,
            "d_cpa_nm": d_cpa_m / NM_TO_M,
            "vert_sep_ft": abs(vertical_sep_at_cpa_m) / FT_TO_M,
            "cpa_x": ownship_cpa_xy_m[0],
            "cpa_y": ownship_cpa_xy_m[1],
        })

    return conflicts
