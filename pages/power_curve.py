import streamlit as st
from menu import menu
from pages import preprocess as p
from etl import base as b

menu()
file_idx, file_to_map = p.preprocess()
name, df = b.get_data(file_idx)

