import streamlit as st
import seaborn as sns
from matplotlib import pyplot as plt
from etl import analysis as ay
from etl import base as b
from etl import map
from model.power import get_power_curve, get_power_curve_plot
from menu import menu

@st.cache_data
def process_data_analysis(data):
    data = ay.calculate_prior_rows(data)
    data = ay.calculate_speeds(data)
    summary_statistics, preferred_order = ay.summary_statistics(data)
    ss = [(p, summary_statistics[p]) for p in preferred_order]
    return data, ss

def fix_color_for_power(mapped, power_curve, power_window):
    if power_window is not None:
        start_power_loc, end_power_loc = power_curve.loc[power_curve['window'] == power_window, ['start', 'end']].values[0]
        max_power = power_curve.loc[power_curve['window'] == power_window,'power'].values[0]
        mapped.iloc[start_power_loc:end_power_loc].loc[:,['color']] = '#2b8cbe'
        return mapped, max_power
    else:
        return mapped, None

menu()
column_to_graph = st.selectbox('Column for Heatmap',('elev','speed','speed_10s_avg'))
file_to_map = st.selectbox('File to Map',b.get_processed_files(),index=None)
st.session_state['last_file'] = file_to_map

power_curve = get_power_curve(file_to_map)
mapped, summary_statistics = map.map_file(file_to_map, column_to_graph)

if mapped is not None:
    left_column, right_column = st.columns(2)
    with left_column:
        mp = st.empty()
        mp.map(mapped, latitude='lat', longitude='lon', size=0.1, color='color')
    with right_column:
        for description, value_units in summary_statistics:
            value, unit = value_units
            st.text(f'{description}:\t{value:0.2f} {unit}')
        power_slider = st.select_slider('Power Selector', options=power_curve['window'].values)
        mapped, max_power = fix_color_for_power(mapped, power_curve, power_slider)
        st.text(f'Max {power_slider} second power: {max_power:.0f} watts')
    mp.map(mapped, latitude='lat', longitude='lon', size=0.1, color='color')

    fig = get_power_curve_plot(power_curve)
    st.pyplot(fig)