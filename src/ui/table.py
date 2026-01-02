import streamlit as st
import pandas as pd
from src.ui.utils import create_callsign_map, label_aircraft


def render_selection_status(a_id, b_id, conflict_df, label_func):
    """
    Render the status of the currently selected aircraft pair.

    Args:
        a_id: First aircraft ICAO24
        b_id: Second aircraft ICAO24
        conflict_df: DataFrame of conflicts
        label_func: Function to convert ICAO24 to display label
    """
    if not a_id or not b_id:
        return

    pair_conflict = conflict_df[
        ((conflict_df["a"] == a_id) & (conflict_df["b"] == b_id)) |
        ((conflict_df["a"] == b_id) & (conflict_df["b"] == a_id))
    ]

    is_conflict = not pair_conflict.empty
    status_text = "Conflict predicted" if is_conflict else "No conflict"

    with st.container(border=True):
        col_info, col_btn = st.columns([7, 1])

        with col_info:
            st.markdown(
                f"""
                **Selection status**  
                {label_func(a_id)} ↔ {label_func(b_id)}  
                <span style="color: {'#d97706' if is_conflict else '#15803d'};">
                    {status_text}
                </span>
                """,
                unsafe_allow_html=True
            )

        with col_btn:
            st.write("")
            st.write("")
            if st.button("Clear"):
                st.session_state.selected_pair = {"a": None, "b": None}
                st.rerun()


def render_conflict_table(conflict_df, label_func, a_id, b_id):
    """
    Render the conflict table with selection handling.

    Args:
        conflict_df: DataFrame of conflicts
        label_func: Function to convert ICAO24 to display label
        a_id: Currently selected aircraft A
        b_id: Currently selected aircraft B

    Returns:
        Tuple of (new_a_id, new_b_id) if selection changed, else (None, None)
    """
    if conflict_df.empty:
        st.caption("No predicted conflicts at this time.")
        return None, None

    display_df = conflict_df.copy()
    display_df["Aircraft A"] = display_df["a"].apply(label_func)
    display_df["Aircraft B"] = display_df["b"].apply(label_func)
    display_df["Time to CPA (s)"] = display_df["t_cpa"].round(1)
    display_df["Horizontal Sep (NM)"] = display_df["d_cpa_nm"].round(2)
    display_df["Vertical Sep (ft)"] = display_df["vert_sep_ft"].round(0)

    # Sort by smallest time to CPA
    display_df = display_df.sort_values("Time to CPA (s)")

    # Select columns for display
    table_df = display_df[["Aircraft A", "Aircraft B",
                           "Time to CPA (s)", "Horizontal Sep (NM)", "Vertical Sep (ft)"]].copy()

    # Create highlighting for selected pair
    selected_mask = (
        ((display_df["a"] == a_id) & (display_df["b"] == b_id)) |
        ((display_df["a"] == b_id) & (display_df["b"] == a_id))
    )

    def highlight_selected(row):
        idx = row.name
        if selected_mask.loc[idx]:
            return ['background-color: rgba(120, 120, 120, 0.15)'] * len(row)
        return [''] * len(row)

    styled_df = (
        table_df.style
        .format({
            "Time to CPA (s)": "{:.1f}",
            "Horizontal Sep (NM)": "{:.2f}",
            "Vertical Sep (ft)": "{:.0f}"
        })
        .apply(highlight_selected, axis=1)
    )

    event = st.dataframe(
        styled_df,
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # Handle row selection
    if event.selection.rows:
        i = event.selection.rows[0]
        selected_row = display_df.iloc[i]
        new_a = selected_row["a"]
        new_b = selected_row["b"]

        if a_id != new_a or b_id != new_b:
            return new_a, new_b

    return None, None


def render_table(conflict_df, snapshot, a_id, b_id):
    """
    Render the conflict table with selection handling.
    """
    # Create callsign mapping and label function
    callsign_map = create_callsign_map(snapshot)
    def label_func(icao): return label_aircraft(icao, callsign_map)

    st.subheader("Predicted Conflicts")

    # Show selection status
    render_selection_status(a_id, b_id, conflict_df, label_func)

    # Render conflict table and handle selection
    new_a, new_b = render_conflict_table(conflict_df, label_func, a_id, b_id)

    # Update selection if changed
    if new_a is not None and new_b is not None:
        st.session_state.selected_pair["a"] = new_a
        st.session_state.selected_pair["b"] = new_b
        st.rerun()

    st.caption(
        "Pairs of aircraft predicted to violate both horizontal and vertical separation "
        "within the selected look-ahead window. Click a row to inspect the encounter."
    )
