import streamlit as st
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
from model import utilities as u

@st.cache_data
def get_cadence_time_plot(df, _fig, _ax):
    df = u.sort_and_add_times(df)
    if np.isnan(df['cadence'].max()):
        has_cadence = False
    else:
        has_cadence = True

    if not has_cadence:
        return False, None
    else:
        lp = sns.lineplot(x='elapsed_total', y='cadence', data=df, ax=_ax)
        _ax.set_xlim(1, df.shape[0])

        max_cadence = df['cadence'].max()
        _ax.set_ylim(0, max_cadence * 1.1)
        _ax.xaxis.set_major_locator(MultipleLocator(60))  # show every 5th tick
        _ax.set(xlabel='Time Elapsed (Seconds)', ylabel='Cadence')
        return True, _fig
