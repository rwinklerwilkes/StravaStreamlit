import streamlit as st
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
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