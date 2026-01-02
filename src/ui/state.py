import streamlit as st
from src.constants import DEFAULT_LOOKAHEAD_S, DEFAULT_HORIZONTAL_SEP_NM, DEFAULT_VERTICAL_SEP_FT


def init_session_state():
    defaults = {
        "selected_pair": {"a": None, "b": None},
        "current_time_idx": 0,
        "lookahead": DEFAULT_LOOKAHEAD_S,
        "sep_nm": DEFAULT_HORIZONTAL_SEP_NM,
        "sep_ft": DEFAULT_VERTICAL_SEP_FT,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
