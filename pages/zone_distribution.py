import streamlit as st
from menu import menu
from pages import preprocess as p
from model import power as pw
from etl import base as b

menu()
file_idx, file_to_map = p.preprocess()
name, df = b.get_data(file_idx)

ftp = st.number_input(label='Current FTP', min_value=0, max_value=1000, value=270)

fig = pw.get_power_curve_zone_plot(df, ftp)
st.pyplot(fig)