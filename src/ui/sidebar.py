import streamlit as st
import pandas as pd


def render_time_controls(times: list) -> int:
    """
    Render time selection slider and navigation buttons.

    Args:
        times: List of available timestamps

    Returns:
        Selected timestamp
    """
    st.sidebar.header("Time Selection")

    # Ensure current_time_idx is within bounds
    if st.session_state.current_time_idx >= len(times):
        st.session_state.current_time_idx = len(times) - 1

    t = st.sidebar.select_slider(
        "Timestamp",
        options=times,
        value=times[st.session_state.current_time_idx],
        format_func=lambda x: pd.to_datetime(x, unit="s").strftime("%H:%M:%S")
    )

    # Update index if slider was manually moved
    if t != times[st.session_state.current_time_idx]:
        st.session_state.current_time_idx = times.index(t)

    # Time control buttons
    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("Back", use_container_width=True):
            if st.session_state.current_time_idx > 0:
                st.session_state.current_time_idx -= 1
                st.rerun()

    with col2:
        if st.button("Forward", use_container_width=True):
            if st.session_state.current_time_idx < len(times) - 1:
                st.session_state.current_time_idx += 1
                st.rerun()

    return t


def render_configuration_controls() -> tuple:
    """
    Render configuration sliders for conflict detection parameters.

    Returns:
        Tuple of (lookahead_s, sep_nm, sep_ft, sep_m)
    """
    st.sidebar.header("Configuration")

    lookahead = st.sidebar.slider(
        "Look-ahead (s)",
        min_value=30,
        max_value=300,
        value=st.session_state.lookahead,
        step=30,
        key="lookahead_slider"
    )
    st.session_state.lookahead = lookahead

    sep_nm = st.sidebar.slider(
        "Separation (NM)",
        min_value=3.0,
        max_value=10.0,
        value=st.session_state.sep_nm,
        step=0.5,
        key="sep_nm_slider"
    )
    st.session_state.sep_nm = sep_nm

    sep_ft = st.sidebar.slider(
        "Vertical separation (ft)",
        min_value=500,
        max_value=3000,
        value=st.session_state.sep_ft,
        step=500,
        key="sep_ft_slider"
    )
    st.session_state.sep_ft = sep_ft

    return lookahead, sep_nm, sep_ft


def render_sidebar(times: list) -> tuple:
    """
    Render the entire sidebar with time controls and configuration controls.
    Args:
        times: List of available timestamps
    Returns:
        Tuple of (current_time, lookahead_s, sep_nm, sep_ft)
    """
    return (
        render_time_controls(times),
        *render_configuration_controls()
    )
