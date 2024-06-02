import pandas as pd
import os
import streamlit as st


@st.cache_data
def get_processed_files() -> list:
    files_available = os.listdir('data/processed/')
    return [i[:-4] for i in files_available]

def get_activity_name(track_name) -> str:
    metadata = pd.read_csv('data/metadata/processed_files.csv',header=None)
    metadata.columns = ['original_filename','track_name','activity_name']
    activity_name = metadata.loc[metadata['track_name']==track_name,'activity_name'].drop_duplicates().values[0]
    return activity_name

@st.cache_data
def get_data(filename):
    data = pd.read_csv(f'data/processed/{filename}.csv', header=None, names=['time','lat','lon','elev','power'])
    data['time'] = pd.to_datetime(data['time'], format='%Y-%m-%d %H:%M:%S')
    activity_name = get_activity_name(filename)
    return activity_name, data[['time','lat','lon','elev','power']]