import streamlit as st
from matplotlib import pyplot as plt
from menu import menu
from etl import map as m
from etl import base as b
from model import power
from model import speed
from model import heart_rate
from model import cadence
from pages import preprocess as p

def define_matplotlib_fig_and_ax():
    #Defining this here to ensure plots used below are always consistent
    fig, ax = plt.subplots(1, 1, figsize=(20, 4))
    return fig, ax

menu()
file_to_map = p.preprocess()
name, df = b.get_data(file_to_map)
mapped, _ = m.map_file(file_to_map, 'elev')
#map
mp = st.empty()
mp.map(mapped, latitude='lat', longitude='lon', size=0.1, color='color')

#speed
st.subheader('Speed')
fig, ax = define_matplotlib_fig_and_ax()
fig = speed.get_speed_time_plot(df,fig,ax)
st.pyplot(fig)

#power
st.subheader('Power')
fig, ax = define_matplotlib_fig_and_ax()
fig = power.get_power_time_plot(df,fig,ax)
st.pyplot(fig)

#hr
fig, ax = define_matplotlib_fig_and_ax()
has_hr, fig = heart_rate.get_hr_time_plot(df,fig,ax)
if has_hr:
    st.subheader('Heart Rate')
    st.pyplot(fig)

#cadence
fig, ax = define_matplotlib_fig_and_ax()
has_cadence, fig = cadence.get_cadence_time_plot(df,fig,ax)
if has_cadence:
    st.subheader('Cadence')
    st.pyplot(fig)
