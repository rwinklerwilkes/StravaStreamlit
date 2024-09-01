import streamlit as st
from etl import base as b

def preprocess():
    pf, details = b.get_processed_files()
    last_file = st.session_state.get('last_file')

    details['selectbox_name'] = details['original_filename'].str.cat(details['name'], sep=' - ')
    details = details.sort_values(by='date', inplace=False)
    select_list = list(details['selectbox_name'].values)
    if not last_file:
        idx = None
    else:
        idx = select_list.index(last_file)

    file_to_map = st.selectbox('File to Map',select_list,index=idx)
    if file_to_map is not None:
        file_idx = file_to_map.split(' - ')[0]
    else:
        file_idx = None

    return file_idx, file_to_map