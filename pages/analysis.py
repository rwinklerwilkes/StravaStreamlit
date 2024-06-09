import streamlit as st
from menu import menu
from etl import map as m
from etl import base as b
from model import power
from pages import preprocess as p


menu()
file_to_map = p.preprocess()
name, df = b.get_data(file_to_map)
mapped, _ = m.map_file(file_to_map, 'elev')
#map
mp = st.empty()
mp.map(mapped, latitude='lat', longitude='lon', size=0.1, color='color')

#speed


#power
power_curve = power.get_power_curve(file_to_map)
fig = power.get_power_curve_plot(power_curve)
st.pyplot(fig)

#hr


#cadence

