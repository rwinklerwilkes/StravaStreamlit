import streamlit as st
import numpy as np
import pandas as pd
from etl import analysis as ay
from etl import base as b

def hex_to_RGB(hex_str):
    """ #FFFFFF -> [255,255,255]"""
    #Pass 16 to the integer function for change of base
    return [int(hex_str[i:i+2], 16) for i in range(1,6,2)]

def get_color_gradient(c1, c2, n):
    """
    Given two hex colors, returns a color gradient
    with n colors.
    """
    assert n > 1
    c1_rgb = np.array(hex_to_RGB(c1))/255
    c2_rgb = np.array(hex_to_RGB(c2))/255
    mix_pcts = [x/(n-1) for x in range(n)]
    rgb_colors = [((1-mix)*c1_rgb + (mix*c2_rgb)) for mix in mix_pcts]
    return ["#" + "".join([format(int(round(val*255)), "02x") for val in item]) for item in rgb_colors]

def val_to_color(data, column_to_use):
    data['scaled'] = (data[column_to_use]-min(data[column_to_use]))/(max(data[column_to_use])-min(data[column_to_use]))
    uniq = data['scaled'].drop_duplicates().sort_values()
    uniq = uniq.reset_index().drop('index',axis=1)
    n = len(uniq)
    start = '#ffffff'
    end = '#562929'
    color_gradient = get_color_gradient(start, end, n)
    uniq['color'] = color_gradient
    mapped = pd.merge(data,uniq,left_on='scaled',right_on='scaled')
    return mapped

@st.cache_data
def process_data_analysis(data):
    data = ay.calculate_prior_rows(data)
    data = ay.calculate_speeds(data)
    summary_statistics, preferred_order = ay.summary_statistics(data)
    ss = [(p, summary_statistics[p]) for p in preferred_order]
    return data, ss

@st.cache_data
def map_file(file_to_map, column_to_use='elev'):
    assert column_to_use in ('elev','speed','speed_10s_avg'), 'Choose one of elev, speed, speed_10s_avg'
    if file_to_map:
        track_name, data = b.get_data(file_to_map)
        data, summary_statistics = process_data_analysis(data)
        mapped = val_to_color(data, column_to_use)
        return mapped, summary_statistics
    else:
        return None, None