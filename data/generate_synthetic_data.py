import numpy as np
import pandas as pd
from datetime import datetime, timezone

OUTPUT_FILE = "synthetic_opensky_germany.csv"

START_TIME = int(
    datetime(2022, 6, 27, 15, 0, tzinfo=timezone.utc).timestamp()
)
DURATION_S = 3600          # 1 hour
TIME_STEP_S = 10

N_AIRCRAFT = 500

LAT_MIN, LAT_MAX = 47.0, 55.0
LON_MIN, LON_MAX = 5.0, 15.0

ALT_MIN_M = 6_000
ALT_MAX_M = 12_000

SPEED_MIN = 180 / 3.6      # ~180 km/h
SPEED_MAX = 900 / 3.6      # ~900 km/h

np.random.seed(42)


def random_icao():
    return "".join(np.random.choice(list("abcdef0123456789"), 6))


def random_callsign(i):
    return f"SYN{i:03d}"


aircraft = []

for i in range(N_AIRCRAFT):
    aircraft.append({
        "icao24": random_icao(),
        "callsign": random_callsign(i),
        "lat": np.random.uniform(LAT_MIN, LAT_MAX),
        "lon": np.random.uniform(LON_MIN, LON_MAX),
        "heading": np.random.uniform(0, 360),
        "velocity": np.random.uniform(SPEED_MIN, SPEED_MAX),
        "altitude": np.random.uniform(ALT_MIN_M, ALT_MAX_M),
        "vertical_rate": np.random.normal(0.0, 0.3),
    })

# -----------------------------
# Generate time series
# -----------------------------

rows = []

times = np.arange(
    START_TIME,
    START_TIME + DURATION_S,
    TIME_STEP_S,
)

for t in times:
    for ac in aircraft:
        heading_rad = np.radians(ac["heading"])

        # Simple motion model (flat-earth approx)
        d_lat = (
            ac["velocity"] * np.cos(heading_rad) * TIME_STEP_S
        ) / 111_000
        d_lon = (
            ac["velocity"] * np.sin(heading_rad) * TIME_STEP_S
        ) / (111_000 * np.cos(np.radians(ac["lat"])))

        ac["lat"] += d_lat
        ac["lon"] += d_lon
        ac["altitude"] += ac["vertical_rate"] * TIME_STEP_S

        rows.append({
            "time": t,
            "icao24": ac["icao24"],
            "lat": ac["lat"],
            "lon": ac["lon"],
            "velocity": ac["velocity"],
            "heading": ac["heading"],
            "vertrate": ac["vertical_rate"],
            "callsign": ac["callsign"],
            "onground": False,
            "alert": False,
            "spi": False,
            "squawk": "",
            "baroaltitude": ac["altitude"],
            "geoaltitude": ac["altitude"] + np.random.normal(0, 15),
            "lastposupdate": t - np.random.uniform(0.5, 1.5),
            "lastcontact": t,
        })

df = pd.DataFrame(rows)

df.to_csv(OUTPUT_FILE, index=False)

print(f"Generated {len(df):,} synthetic ADS-B states")
print(f"Saved to {OUTPUT_FILE}")
