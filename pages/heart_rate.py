import streamlit as st
from etl import base as b
from menu import menu
from model import heart_rate
from pages import preprocess as p

menu()
file_to_map = p.preprocess()
name, df = b.get_data(file_to_map)

fig = heart_rate.get_hr_zone_plot(df)
st.pyplot(fig)