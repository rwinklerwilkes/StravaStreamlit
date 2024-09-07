import streamlit as st
import seaborn as sns
from matplotlib.ticker import MaxNLocator

from menu import menu
from pages import preprocess as p
from utilities.strava import activites_with_effort, effort_by_week
from matplotlib import pyplot as plt
from etl import base as b


menu()
file_idx, file_to_map = p.preprocess()
name, df = b.get_data(file_idx)

"""How I'd like to build out this page:
1. Fetch the relative effort from the activities.csv file
    a. Refactor the load process for that CSV file using the code within calculate_relative_effort_by_week
        - This is necessary because the perceived/actual relative efforts need to be reconciled. 
2. Calculate the relative effort by week using calculate_relative_effort_by_week from utilities.strava
3. Get the relative effort for a 12-week window - not clear how Strava decides which 12 to show.
    Best option may be to figure out how many following weeks are available, grab up to 5 of those, then do 6 trailing
    + current window for the 12. Essentially try to center the activity within the window.
4. Graph all twelve points with the Monday starting the week as the X axis label
"""
detail = activites_with_effort.loc[activites_with_effort['original_filename'] == file_idx, :]
year = detail['year'].values[0]
week = detail['week'].values[0]
effort_by_week = effort_by_week.sort_values(by=['year','week'])
effort_by_week['row_number'] = effort_by_week.index

current_rn = effort_by_week.loc[(effort_by_week['year']==year)&(effort_by_week['week']==week),'row_number'].values[0]
nearby_weeks = effort_by_week.loc[(effort_by_week['row_number']>= current_rn-6)&(effort_by_week['row_number']<= current_rn+5)]
nearby_weeks['label'] = nearby_weeks.apply(lambda x: f"{x['year']}, Week {x['week']}", axis=1)

st.table(nearby_weeks)

fig, ax = plt.subplots(1,1,figsize=(14,8))
labels = nearby_weeks['label'].values
min_rn = min(nearby_weeks['row_number'])
def format_fn(tick_val, tick_pos):
    if int(tick_val) in nearby_weeks['row_number'].values:
        return labels[int(tick_val)-min_rn]
    else:
        return ''

# A FuncFormatter is created automatically.
ax.xaxis.set_major_formatter(format_fn)
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
lp = sns.lineplot(data=nearby_weeks, x='row_number', y='combined_relative_effort', ax=ax)

ax.set(xlabel='Week Number', ylabel='Relative Effort')
st.pyplot(fig)
