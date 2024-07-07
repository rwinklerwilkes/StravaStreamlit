import streamlit as st
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from matplotlib.ticker import MultipleLocator

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
def get_hr_time_plot(df):
    df = u.sort_and_add_times(df)
    if np.isnan(df['heart_rate'].max()):
        has_hr = False
    else:
        has_hr = True

    if not has_hr:
        return False, None
    else:
        fig, ax = plt.subplots(1, 1, figsize=(14, 8))
        lp = sns.lineplot(x='elapsed_total', y='heart_rate', data=df, ax=ax)
        ax.set_xlim(1, df.shape[0])

        max_hr = df['heart_rate'].max()
        ax.set_ylim(0, max_hr * 1.1)
        ax.xaxis.set_major_locator(MultipleLocator(60))  # show every 5th tick
        ax.set(xlabel='Time Elapsed (Seconds)', ylabel='Heart Rate')
        return True, fig