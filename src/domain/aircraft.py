from dataclasses import dataclass
import numpy as np
from src.domain.geometry import latlon_to_xy


@dataclass
class AircraftState:
    """
    Represents the instantaneous kinematic state of an aircraft
    derived from ADS-B data.

    All motion assumptions are linear and time-invariant
    over the prediction horizon.
    """
    icao24: str
    lat_deg: float
    lon_deg: float
    velocity_mps: float
    heading_deg: float
    altitude_m: float
    vertical_rate_mps: float

    def position_xy(self, lat0, lon0):
        return latlon_to_xy(self.lat_deg, self.lon_deg, lat0, lon0)

    def velocity_vector(self):
        h = np.radians(self.heading_deg)
        return np.array([
            self.velocity_mps * np.sin(h),
            self.velocity_mps * np.cos(h)
        ])
