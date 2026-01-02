import streamlit as st


def render_footer():
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; font-size: 0.9em; color: #888;">
            Demo uses <strong>synthetic ADS-B data</strong> generated for visualization
            and method demonstration purposes.<br/>
            Deterministic CPA-based conflict analysis ·
            <a href="https://github.com/GR0ZA/AirCPA" target="_blank">
                GitHub repository
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
