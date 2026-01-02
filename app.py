from src.domain.cpa import detect_conflicts
from src.ui.state import init_session_state
from src.ui.footer import render_footer
from src.ui.sidebar import render_sidebar
from src.ui.map import render_map
from src.ui.table import render_table
from src.constants import NM_TO_M

import streamlit as st
import pandas as pd


# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(layout="wide")
st.title("AirCPA")
st.caption(
    "Offline analysis of historic ADS-B data using deterministic "
    "Closest Point of Approach (CPA) prediction on ADS-B state vectors."
)

# ==================================================
# MAIN APPLICATION
# ==================================================


def main():
    init_session_state()
    df = load_data("data/states_2022-06-27-15_germany.csv")

    times = sorted(df["time"].unique())[1:]

    # Render sidebar
    current_time, lookahead, sep_nm, sep_ft = render_sidebar(times)

    # Create snapshot at current time
    snapshot = df[df["time"] == current_time].copy()

    a_id = st.session_state.selected_pair["a"]
    b_id = st.session_state.selected_pair["b"]

    # Detect conflicts
    conflicts = detect_conflicts(
        snapshot,
        lookahead_s=lookahead,
        sep_nm=sep_nm,
        sep_ft=sep_ft
    )
    conflict_df = pd.DataFrame(conflicts) if conflicts else pd.DataFrame()

    # Render map & table
    col_map, col_table = st.columns([3, 2])

    with col_table:
        render_table(
            conflict_df=conflict_df,
            snapshot=snapshot,
            a_id=a_id,
            b_id=b_id
        )

    with col_map:
        render_map(
            snapshot=snapshot,
            df=df,
            current_time=current_time,
            conflict_df=conflict_df,
            a_id=a_id,
            b_id=b_id,
            lookahead=lookahead,
            sep_m=sep_nm * NM_TO_M
        )

    render_footer()


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


if __name__ == "__main__":
    main()
