# Example token refresh
# curl -X POST https://www.strava.com/api/v3/oauth/token \
#   -d client_id=ReplaceWithClientID \
#   -d client_secret=ReplaceWithClientSecret \
#   -d grant_type=refresh_token \
#   -d refresh_token=ReplaceWithRefreshToken

import pandas as pd
import numpy as np
from pandas import DataFrame as PandasDataFrame
import streamlit as st

@st.cache_data
def load_activities_from_archive() -> PandasDataFrame:
    activities = pd.read_csv('data/strava/activities.csv')
    activities['original_filename'] = activities['Filename'].str.split('/').str[-1].str.split('.').str[0]
    activities['Activity Date'] = pd.to_datetime(activities['Activity Date'], format='%b %d, %Y, %I:%M:%S %p')
    return activities

def get_activity_detail(activities, activity_id, column):
    try:
        detail = activities.loc[activities['Activity ID'] == activity_id, column][0]
    except KeyError:
        print(f"Couldn't locate activity ID {activity_id}")
        detail = None
    return detail

def get_activity_name(activities, activity_id):
    try:
        detail = activities.loc[activities['Activity ID'] == activity_id, 'Activity Name'][0]
    except KeyError:
        try:
            details = activities.loc[activities['Filename'].str.contains(str(activity_id), na=False), 'Activity Name']
            assert details.shape[0] == 1
            detail = details.values[0]
        except KeyError:
            print(f"Couldn't locate activity ID {activity_id}")
            detail = None
    return detail

def get_activity_date(activity_id):
    activities = load_activities_from_archive()
    return get_activity_detail(activities, activity_id, 'Activity Date')

def get_name_and_date(files_available) -> PandasDataFrame:
    fa_pd = pd.DataFrame(files_available, columns=['original_filename_with_ext'])
    fa_pd['original_filename'] = fa_pd['original_filename_with_ext'].str.split('.').str[0]
    files_with_details = pd.merge(fa_pd,activities,on='original_filename',how='left')
    details = files_with_details[['original_filename','Activity Name', 'Activity Date']]
    details.columns = ['original_filename','name','date']
    #Ensure dates are formatted correctly so they get ordered correctly later
    return details

@st.cache_data
def calculate_relative_effort_by_week(activities:PandasDataFrame) -> tuple[PandasDataFrame,PandasDataFrame]:
    """Calculates the relative effort for each activity. Uses a flag from Strava's data indicating whether
    to use the calculated relative effort based on heart rate or the user's perceived effort imported manually.
    The "Prefer Perceived Exertion" flag isn't perfect because it will be set to 0 even where the relative effort
    isn't calculated on a row, so we need to make it 1 if a. it's already 1 or b. there is no relative effort.
    :param activities: Pandas Dataframe containing a row for each activity
    :return effort_by_week: Pandas Dataframe containing relative effort summed up to the year and week level

    """
    activities = activities.copy()
    activities['year'] = activities['Activity Date'].dt.isocalendar().year
    activities['week'] = activities['Activity Date'].dt.isocalendar().week
    activities['pr_weighting'] = np.where((activities['Relative Effort'].isnull())&(~activities['Perceived Relative Effort'].isnull()),1,activities['Prefer Perceived Exertion'])
    activities['pf_effort'] = activities['pr_weighting']*activities['Perceived Relative Effort']
    activities['pf_effort'] = np.where(activities['pf_effort']==0,np.nan,activities['pf_effort'])
    activities['combined_relative_effort'] = activities['pf_effort'].combine_first(activities['Relative Effort'])
    effort_by_week = activities.groupby(['year','week']).agg({'combined_relative_effort':'sum','Activity Date':['min','max']}).reset_index()
    effort_by_week.columns=['year','week','combined_relative_effort','activity_min_date','activity_max_date']

    _ = """By the way, relative effort seems to be calculated something like:
    0.25 * minutes at Heart Rate Z1
    0.50 * minutes at Heart Rate Z2
    1.50 * minutes at Heart Rate Z3
    2.00 * minutes at Heart Rate Z4
    ???? * minutes at Heart Rate Z5 - I basically never hit this zone so no idea what the factor may be. Maybe 3?
    This isn't exactly right, but I got pretty close for the few activities that I spot checked with these factors.
    """

    return activities, effort_by_week

activities = load_activities_from_archive()
activites_with_effort, effort_by_week = calculate_relative_effort_by_week(activities)