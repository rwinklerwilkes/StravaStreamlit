# Example token refresh
# curl -X POST https://www.strava.com/api/v3/oauth/token \
#   -d client_id=ReplaceWithClientID \
#   -d client_secret=ReplaceWithClientSecret \
#   -d grant_type=refresh_token \
#   -d refresh_token=ReplaceWithRefreshToken

import pandas as pd
from pandas import DataFrame as PandasDataFrame

def load_activities_from_archive() -> PandasDataFrame:
    activities = pd.read_csv('data/strava/activities.csv')
    activities['original_filename'] = activities['Filename'].str.split('/').str[-1].str.split('.').str[0]
    return activities

activities = load_activities_from_archive()

def get_activity_detail(activity_id, column):
    try:
        detail = activities.loc[activities['Activity ID'] == activity_id, column][0]
    except KeyError:
        print(f"Couldn't locate activity ID {activity_id}")
        detail = None
    return detail

def get_activity_name(activity_id):
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
    return get_activity_detail(activity_id, 'Activity Date')

def get_name_and_date(files_available) -> PandasDataFrame:
    fa_pd = pd.DataFrame(files_available, columns=['original_filename_with_ext'])
    fa_pd['original_filename'] = fa_pd['original_filename_with_ext'].str.split('.').str[0]
    files_with_details = pd.merge(fa_pd,activities,on='original_filename',how='left')
    details = files_with_details[['original_filename','Activity Name', 'Activity Date']]
    details.columns = ['original_filename','name','date']
    #Ensure dates are formatted correctly so they get ordered correctly later
    details['date'] = pd.to_datetime(details['date'], format='%b %d, %Y, %I:%M:%S %p')
    return details