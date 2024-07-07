from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
import seaborn as sns
import streamlit as st
from geopy import distance
import numpy as np
from model import utilities as u


def calculate_speed(df):
    # Calculates 5 second average speed
    SECONDS_PER_HOUR = 3600
    df = u.sort_and_add_times(df)

    df['lat_lon'] = list(zip(df['lat'], df['lon']))
    df['prev_lat_lon'] = df['lat_lon'].shift(1).fillna(df['lat_lon'])

    if not np.isnan(df['distance'].max()):
        df['prev_distance'] = df['distance'].shift(1)
        # Only want distance difference between this row and prior row
        df['distance'] = df['distance'] - df['prev_distance']
        df['distance'] = df['distance'].fillna(0)
        units = 'meters'
    else:
        units = 'miles'
    df['distance_calculated'] = df.apply(lambda x: distance.distance(x['lat_lon'], x['prev_lat_lon']).miles, axis=1)
    df['distance'] = df['distance'].fillna(df['distance_calculated'])
    df['distance_5r'] = df['distance'].rolling(5).sum()
    df['elapsed_5r'] = df['elapsed'].rolling(5).sum()
    df['speed'] = (df['distance_5r'] / df['elapsed_5r']).fillna(0) * SECONDS_PER_HOUR

    if units == 'meters':
        METERS_TO_MILES_FACTOR = 1609
        df['speed'] = df['speed'] / METERS_TO_MILES_FACTOR
    return df

@st.cache_data
def get_speed_time_plot(df, _fig, _ax):
    # underscore in params ensures Streamlit won't try to hash
    if 'speed' not in df.columns:
        df = calculate_speed(df)

    lp = sns.lineplot(x='elapsed_total', y='speed', data=df, ax=_ax)
    _ax.set_xlim(1, df.shape[0])
    max_speed = df['speed'].max()
    _ax.set_ylim(0, max_speed * 1.1)
    _ax.xaxis.set_major_locator(MultipleLocator(60))  # show every 5th tick
    _ax.set(xlabel='Time Elapsed (Seconds)', ylabel='Speed (MPH)')

    return _fig