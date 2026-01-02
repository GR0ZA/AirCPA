import pandas as pd

INPUT_FILE = "states_2022-06-27-15.csv"
OUTPUT_FILE = "states_europe_1h_germany.csv"

LAT_MIN, LAT_MAX = 47.0, 55.0
LON_MIN, LON_MAX = 5.0, 15.0
MIN_STATES_PER_AIRCRAFT = 30

print("Loading data...")
df = pd.read_csv(INPUT_FILE)

df = (
    df
    .dropna(subset=["lat", "lon", "velocity", "heading"])
    .query("onground == False")
    .query("@LAT_MIN <= lat <= @LAT_MAX")
    .query("@LON_MIN <= lon <= @LON_MAX")
)

valid_icao24 = (
    df.groupby("icao24")
      .size()
      .loc[lambda s: s >= MIN_STATES_PER_AIRCRAFT]
      .index
)

df = (
    df[df["icao24"].isin(valid_icao24)]
    .sort_values(["icao24", "time"])
)

df.to_csv(OUTPUT_FILE, index=False)

print(
    f"Rows: {len(df):,} | "
    f"Aircraft: {df['icao24'].nunique():,} | "
    f"Time range: {df['time'].min()}–{df['time'].max()} | "
    f"Saved: {OUTPUT_FILE}"
)
