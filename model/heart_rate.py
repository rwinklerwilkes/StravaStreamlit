import streamlit as st
import numpy as np
import seaborn as sns
from matplotlib.ticker import MultipleLocator
from matplotlib import pyplot as plt
from model import utilities as u

def calculate_hr_zones(max_heart_rate):
    #set max at 2 so that any HRs above .97 are considered anaerobic
    breakpoints = {'Endurance':0,
                   'Moderate':0.59,
                   'Tempo':0.78,
                   'Threshold':0.87,
                   'Anaerobic':0.97}
    zones = {name: pct * max_heart_rate for name, pct in breakpoints.items()}
    return zones

@st.cache_data
def get_hr_time_plot(df, _fig, _ax):
    # underscore in params ensures Streamlit won't try to hash
    df = u.sort_and_add_times(df)
    if np.isnan(df['heart_rate'].max()):
        has_hr = False
    else:
        has_hr = True

    if not has_hr:
        return False, None
    else:
        lp = sns.lineplot(x='elapsed_total', y='heart_rate', data=df, ax=_ax)
        _ax.set_xlim(1, df.shape[0])

        max_hr = df['heart_rate'].max()
        _ax.set_ylim(0, max_hr * 1.1)
        _ax.xaxis.set_major_locator(MultipleLocator(60))  # show every 5th tick
        _ax.set(xlabel='Time Elapsed (Seconds)', ylabel='Heart Rate')
        return True, _fig

@st.cache_data
def get_hr_zone_plot(df):
    df = u.sort_and_add_times(df)
    zones = calculate_hr_zones(191)

    zone_labels = zones.keys()
    zone_mins = list(zones.values())
    for i, label in enumerate(zone_labels):
        mn = zone_mins[i]
        try:
            mx = zone_mins[i+1]
        except IndexError:
            mx = np.inf
        df.loc[(df['heart_rate']>=mn)&(df['heart_rate']<mx),'label'] = label

    fig, ax = plt.subplots(1,1,figsize=(14,8))
    df_agg = df.groupby('label').agg({'heart_rate':'count'}).reset_index()
    bp = sns.barplot(data=df_agg, x='heart_rate', y='label', ax=ax)
    ax.set(xlabel='Time in Zone (Seconds)', ylabel='Heart Rate Zone')

    return fig

# from etl.base import get_data
# from model import utilities as u
# name, df = get_data('10216028842')
# df = u.sort_and_add_times(df)
# zones = calculate_hr_zones(191)

# import seaborn as sns
# sns.histplot(data=df, x='heart_rate', bins=list(zones.values()))