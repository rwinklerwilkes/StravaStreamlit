import streamlit as st
from menu import menu
from etl import map as m
from etl import base as b
from model import power
from model import speed
from model import heart_rate
from pages import preprocess as p


menu()
file_to_map = p.preprocess()
name, df = b.get_data(file_to_map)
mapped, _ = m.map_file(file_to_map, 'elev')
#map
mp = st.empty()
mp.map(mapped, latitude='lat', longitude='lon', size=0.1, color='color')

#speed
st.subheader('Speed')
fig = speed.get_speed_time_plot(df)
st.pyplot(fig)

#power
st.subheader('Power')
fig = power.get_power_time_plot(df)
st.pyplot(fig)

#hr
has_hr, fig = heart_rate.get_hr_time_plot(df)
if has_hr:
    st.subheader('Heart Rate')
    st.pyplot(fig)

#cadence
# fig = get_cadence_time_plot(df)
# st.pyplot(fig)