import pandas as pd

def sort_and_add_times(df):
    df = df.sort_values(by='time')
    df['time_dt'] = pd.to_datetime(df['time'])
    df['prev_time_dt'] = df['time_dt'].shift(1)
    df['elapsed'] = (df['time_dt'] - df['prev_time_dt']).dt.total_seconds().fillna(0)
    df['elapsed_total'] = (df['time_dt'] - df['time_dt'].min()).dt.total_seconds().fillna(0)
    return df