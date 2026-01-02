import streamlit as st


def render_footer():
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; font-size: 0.9em; color: #888;">
            Data source: 
            <a href="https://opensky-network.org/datasets/#states/2022-06-27/15/" target="_blank">
                OpenSky Network
            </a> —
            ADS-B state vectors over Germany,
            2022-06-27, 15:00–16:00 UTC<br/>
            Deterministic CPA-based conflict analysis ·
            <a href="https://github.com/your-username/your-repo" target="_blank">
                GitHub repository
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
