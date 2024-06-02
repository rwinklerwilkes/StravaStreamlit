import streamlit as st
from etl import base as b

def preprocess():
    pf = b.get_processed_files()
    if 'last_file' not in st.session_state:
        last_file = None
        idx = None
    else:
        last_file = st.session_state['last_file']
        idx = pf.index(last_file)

    file_to_map = st.selectbox('File to Map',pf,index=idx)
    return file_to_map