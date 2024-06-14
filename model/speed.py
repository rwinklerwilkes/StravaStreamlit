from matplotlib import pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd
import numpy as np
from geopy import distance

def calculate_speed(df):
    #Calculates 5 second average speed
    SECONDS_PER_HOUR = 3600
    df = df.sort_values(by='time')
    df['time_dt'] = pd.to_datetime(df['time'])
    df['lat_lon'] = list(zip(df['lat'], df['lon']))
    df['prev_lat_lon'] = df['lat_lon'].shift(1).fillna(df['lat_lon'])
    df['prev_time_dt'] = df['time_dt'].shift(1)
    df['elapsed'] = (df['time_dt'] - df['prev_time_dt']).dt.total_seconds().fillna(0)
    df['distance_calculated'] = df.apply(lambda x: distance.distance(x['lat_lon'], x['prev_lat_lon']).miles, axis=1)
    df['distance'] = df['distance'].fillna(df['distance_calculated'])
    df['distance_5r'] = df['distance'].rolling(5).sum()
    df['elapsed_5r'] = df['elapsed'].rolling(5).sum()
    df['speed'] = (df['distance_5r'] / df['elapsed_5r']).fillna(0) * SECONDS_PER_HOUR
    return df

@st.cache_data
def get_speed_time_plot(df):
    if 'speed' not in df.columns:
        df = calculate_speed(df)

    fig, ax = plt.subplots(1,1,figsize=(14,8))
    lp = sns.lineplot(x='time',y='speed',data=df, ax=ax)
    lp.set(xscale='log')
    lp.set(xticks=[1,15,60,300,600,1200, 2400, 3600])
    lp.set(xticklabels=[1,15,60,300,600,1200, 2400, 3600])
    ax.set_xlim(1,df.shape[0])
    ax.set_ylim(0,1000)
    return fig