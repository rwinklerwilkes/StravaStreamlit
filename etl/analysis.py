import numpy as np
import pandas as pd
from numpy import radians, sin, cos, sqrt, arcsin

def haversine(lat1, lon1, lat2, lon2):
    Rkm = 6372.8  # Earth radius in kilometers
    R = 3958.8

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat / 2)**2 + cos(lat1) * cos(lat2) * sin(dLon / 2)**2
    c = 2 * arcsin(sqrt(a))

    return R * c

def get_data(filename):
    data = pd.read_csv(f'data/processed/{filename}.csv', header=None, names=['time','lat','lon','elev','power'])
    data['time'] = pd.to_datetime(data['time'], format='%Y-%m-%d %H:%M:%S')
    return data

def calculate_prior_rows(data):
    data['prev_time'] = data['time'].shift(1)
    data['prev_lat'] = data['lat'].shift(1)
    data['prev_lon'] = data['lon'].shift(1)
    data['prev_elev'] = data['elev'].shift(1)
    data['time_diff'] = data['time'] - data['prev_time']
    data['elev_diff'] = data['elev'] - data['prev_elev']
    return data

def calculate_speeds(data):
    data['distance'] = haversine(data['lat'], data['lon'], data['prev_lat'], data['prev_lon'])
    data['distance_feet'] = data['distance'] * 5280
    data['speed_fts'] = data['distance_feet']/data['time_diff'].dt.total_seconds()
    SECONDS_PER_HOUR = 3600
    MILE_PER_FOOT = 1/5280
    data['speed'] = data['speed_fts']*SECONDS_PER_HOUR*MILE_PER_FOOT
    data['speed'] = data['speed'].fillna(0)
    data['speed_10s_avg'] = data['speed'].rolling(10).mean()
    data['speed_10s_avg'] = data['speed_10s_avg'].combine_first(data['speed'])
    return data

def summary_statistics(data):
    output = {}
    output['Distance'] = (data['distance'].sum(),'miles')
    output['Total Elevation'] = (data.loc[data['elev_diff'] > 0,'elev_diff'].sum(),'feet')
    output['Time Elapsed'] = ((data['time'].max() - data['time'].min()).total_seconds()/60,'minutes')
    output['Average Speed'] = (data['speed'].mean(),'mph')
    output['Max Speed'] = (data['speed'].max(),'mph')
    preferred_order = ('Distance','Total Elevation','Time Elapsed','Average Speed', 'Max Speed')
    return output, preferred_order


def calculate_power_curve(data):
    SECONDS_MAX = 300
    FIVE_SECONDS_MAX = 600
    TEN_SECONDS_MAX = 1200
    THIRTY_SECONDS_MAX = data.shape[0]

    power_curve = np.hstack([np.arange(1, SECONDS_MAX * 5 + 1),
                             np.arange(SECONDS_MAX + 5, FIVE_SECONDS_MAX + 5, 5),
                             np.arange(FIVE_SECONDS_MAX + 10, TEN_SECONDS_MAX + 10, 10),
                             np.arange(TEN_SECONDS_MAX + 30, THIRTY_SECONDS_MAX + 30, 30)])
    power_curve = pd.DataFrame(power_curve.T, columns=['window'])
    power_curve = power_curve.loc[power_curve['window'] <= THIRTY_SECONDS_MAX, :]

    power_curve['power'] = 0
    for i, row in power_curve.iterrows():
        power_curve.loc[i, 'power'] = data['power'].rolling(window=row.window).mean().max()
    power_curve = power_curve.dropna(axis=0)
    return power_curve

def example():
    data = get_data('3934663673')
    data = calculate_prior_rows(data)
    data = calculate_speeds(data)
    stats, _ = summary_statistics(data)
    return data, stats