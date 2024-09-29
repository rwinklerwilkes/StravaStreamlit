import functools

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
import seaborn as sns
import streamlit as st
import pandas as pd
import numpy as np
from etl import base as b
from model import utilities as u


def validate_power(func):
    @functools.wraps(func)
    def wrapper(df, *args, **kwargs):
        has_power = df.loc[~df['power'].isna(), ['power']].count()['power'] > 0
        if not has_power:
            return False, None
        else:
            return True, func(df, *args, **kwargs)
    return wrapper

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

@validate_power
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

@validate_power
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
def get_power_curve_zone_plot(df: pd.DataFrame, ftp:int) -> Figure:
    """
    Mimics the functionality on the "Zone Distribution" tab of Strava. Categorizes a ride into the amount of time
    spent in each power zone, https://www.trainingpeaks.com/blog/power-training-levels/.
    FTP is a necessary param because it determines the breakpoints for each zone.
    :param df: Dataframe containing the second-level details for the ride.
    :param ftp: Rider's functional threshold power
    :return: Matplotlib figure with the power zone plot
    """
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


def calculate_average_power(data:pd.DataFrame) -> float:
    has_power = np.sum(data['power'].count()) > 0
    average_power = None
    if has_power:
        average_power = data['power'].mean()
    return average_power

#Both of these calculated per https://medium.com/critical-powers/formulas-from-training-and-racing-with-a-power-meter-2a295c661b46
#In case it ever gets broken, this URL references Training and Racing with a Power Meter by Hunter and Allen

def calculate_normalized_power(data:pd.DataFrame) -> float:
    has_power = np.sum(data['power'].count()) > 0
    normalized_power = None

    if has_power:
        rolling_average = data['power'].rolling(30).mean()
        rolling_average = rolling_average[rolling_average>0]
        rolling_average = rolling_average**4
        normalized_power = rolling_average.mean()**0.25

    return normalized_power

def calculate_intensity_factor(data:pd.DataFrame, ftp: float) -> tuple[float,float]:
    has_power = np.sum(data['power'].count()) > 0
    intensity_factor = None
    tss = None
    if has_power:
        norm_power = calculate_normalized_power(data)
        t = (max(data['time']) - min(data['time'])).seconds
        intensity_factor = norm_power/ftp
        tss = (t*intensity_factor*norm_power)/(ftp*36)

    return intensity_factor, tss