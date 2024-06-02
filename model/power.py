import pandas as pd
import numpy as np

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

def calculate_power_curve_file(filename_without_ext):
    df = pd.read_csv(f'data/processed/{filename_without_ext}.csv',
                     header=None,
                     names=['time', 'lat', 'lon', 'elev', 'power'])
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
