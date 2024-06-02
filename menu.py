import streamlit as st

def menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("main.py", label="Summary")
    st.sidebar.page_link("pages/analysis.py", label="Analysis")
    st.sidebar.page_link("pages/relative_effort.py", label="Relative Effort")
    st.sidebar.page_link("pages/heart_rate.py", label="Heart Rate")
    st.sidebar.page_link("pages/power_curve.py", label="Power Curve")
    st.sidebar.page_link("pages/zone_distribution.py", label="Zone Distribution")
    st.sidebar.page_link("pages/watt_distribution.py", label="Watt Distribution")