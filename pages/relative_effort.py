import streamlit as st

from menu import menu
from pages import preprocess as p
from utilities import strava
from etl import base as b
import plotly.express as px


menu()
file_idx, file_to_map = p.preprocess()
name, df = b.get_data(file_idx)

def identify_nearby_weeks(file_idx):
    detail = strava.activites_with_effort.loc[strava.activites_with_effort['original_filename'] == file_idx, :]
    year = detail['year'].values[0]
    week = detail['week'].values[0]
    effort_by_week = strava.effort_by_week.sort_values(by=['year','week'])
    effort_by_week['row_number'] = effort_by_week.index

    current_rn = effort_by_week.loc[(effort_by_week['year']==year)&(effort_by_week['week']==week),'row_number'].values[0]
    nearby_weeks = effort_by_week.loc[(effort_by_week['row_number']>= current_rn-6)&(effort_by_week['row_number']<= current_rn+5)]
    nearby_weeks['label'] = nearby_weeks.apply(lambda x: f"{x['activity_min_date']:%Y-%m-%d}", axis=1)
    return nearby_weeks

nearby_weeks = identify_nearby_weeks(file_idx)
st.table(nearby_weeks)

fig = px.line(nearby_weeks, x="row_number", y="combined_relative_effort", title='Relative Effort',
              labels={"row_number": "Row Number","combined_relative_effort": "Relative Effort"})

fig.update_layout(xaxis = dict(
    tickmode='array', #change 1
    tickvals = nearby_weeks['row_number'].values, #change 2
    ticktext = nearby_weeks['label'].values),
    font=dict(size=18, color="black"))
# fig.show()
st.plotly_chart(fig,use_container_width=True)