import streamlit as st
from menu import menu
from etl import map as m
from pages import preprocess as p

menu()
file_to_map = p.preprocess()

mapped = m.map_file(file_to_map, 'elev')
