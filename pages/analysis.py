import streamlit as st
from menu import menu
from etl import map as m
from etl import base as b
from model import power
from model import speed
from pages import preprocess as p


menu()
file_to_map = p.preprocess()
name, df = b.get_data(file_to_map)
mapped, _ = m.map_file(file_to_map, 'elev')
#map
mp = st.empty()
mp.map(mapped, latitude='lat', longitude='lon', size=0.1, color='color')

#speed
#TODO: These two plotting functions aren't working as expected, plots are currently blank
fig = speed.get_speed_time_plot(df)
st.pyplot(fig)

#power
fig = power.get_power_time_plot(df)
st.pyplot(fig)

#hr
# fig = hr.get_hr_time_plot(df)
# st.pyplot(fig)

#cadence
# fig = get_cadence_time_plot(df)
# st.pyplot(fig)