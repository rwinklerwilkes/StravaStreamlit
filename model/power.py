from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
import seaborn as sns
import streamlit as st
import pandas as pd
import numpy as np
from etl import base as b
from model import utilities as u

def power_curve_breakpoints(df):
    SECONDS_MAX = 300
    FIVE_SECONDS_MAX = 600
    TEN_SECONDS_MAX = 1200
    THIRTY_SECONDS_MAX = df.shape[0]

    power_curve = np.hstack([np.arange(1, SECONDS_MAX * 5 + 1),
                             np.arange(SECONDS_MAX + 5, FIVE_SECONDS_MAX + 5, 5),
                             np.arange(FIVE_SECONDS_MAX + 10, TEN_SECONDS_MAX + 10, 10),
                             np.arange(TEN_SECONDS_MAX + 30, THIRTY_SECONDS_MAX + 30, 30)])

    return power_curve

def calculate_power_curve(df):
    power_curve = power_curve_breakpoints(df)
    power_curve_df = pd.DataFrame(power_curve.T, columns=['window'])
    power_curve_df['power'] = 0
    power_curve_df['start'] = 0
    power_curve_df['end'] = 0
    for i, row in power_curve_df.iterrows():
        power_curve_df.loc[i,'power'] = df['power'].rolling(window=row.window).mean().max()
        power_curve_df.loc[i,'end'] = df['power'].rolling(window=row.window).mean().argmax()

        start = power_curve_df.loc[i,'end'] - row.window
        if start < 0:
            start = 0
        power_curve_df.loc[i,'start'] = start

    power_curve_df = power_curve_df.dropna(axis=0)
    return power_curve_df

@st.cache_data
def get_power_curve(file_to_map):
    if file_to_map:
        power_curve = calculate_power_curve_file(file_to_map)
        return power_curve
    else:
        return None

def calculate_power_curve_file(filename_without_ext):
    _, df = b.get_data(filename_without_ext)
    return calculate_power_curve(df)


def calculate_power_zones(ftp):
    breakpoints = {'Active Recovery':0,
                   'Endurance':0.55,
                   'Tempo':0.75,
                   'Threshold':0.90,
                   'VO2Max':1.05,
                   'Anaerobic':1.20,
                   'Neuromuscular':1.5}
    zones = {name:ftp*pct for name,pct in breakpoints.items()}
    return zones

@st.cache_data
def get_power_curve_plot(power_curve):
    fig, ax = plt.subplots(1,1,figsize=(14,8))
    lp = sns.lineplot(x='window',y='power',data=power_curve, ax=ax)
    lp.set(xscale='log')
    lp.set(xticks=[1,15,60,300,600,1200, 2400, 3600])
    lp.set(xticklabels=[1,15,60,300,600,1200, 2400, 3600])
    ax.set_xlim(1,power_curve.shape[0])
    ax.set_ylim(0,1000)
    return fig

@st.cache_data
def get_power_time_plot(df, _fig, _ax):
    # underscore in params ensures Streamlit won't try to hash
    df = u.sort_and_add_times(df)
    lp = sns.lineplot(x='elapsed_total',y='power',data=df, ax=_ax)
    _ax.set_xlim(1,df.shape[0])

    max_power = df['power'].max()
    _ax.set_ylim(0, max_power * 1.1)
    _ax.xaxis.set_major_locator(MultipleLocator(60))  # show every 5th tick
    _ax.set(xlabel='Time Elapsed (Seconds)', ylabel='Power (W)')
    return _fig

@st.cache_data
def get_power_curve_zone_plot(df, ftp):
    df = u.sort_and_add_times(df)
    zones = calculate_power_zones(ftp)

    zone_labels = zones.keys()
    zone_mins = list(zones.values())
    for i, label in enumerate(zone_labels):
        mn = zone_mins[i]
        try:
            mx = zone_mins[i+1]
        except IndexError:
            mx = np.inf
        df.loc[(df['power']>=mn)&(df['power']<mx),'label'] = label

    fig, ax = plt.subplots(1,1,figsize=(14,8))
    df_agg = df.groupby('label').agg({'power':'count'}).reset_index()

    for label in zone_labels:
        if df_agg.loc[df_agg['label']==label,:].count()['label'] == 0:
            new_label = pd.DataFrame([[label,0]],columns=['label','power'])
            df_agg = pd.concat([df_agg, new_label])

    df_agg['sort_order'] = df_agg['label'].apply(lambda x: list(zone_labels).index(x))
    df_agg = df_agg.sort_values(by='sort_order')

    bp = sns.barplot(data=df_agg, x='power', y='label', ax=ax)
    ax.set(xlabel='Time in Zone (Seconds)', ylabel='Power Zone')

    return fig