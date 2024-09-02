import streamlit as st
from menu import menu
from pages import preprocess as p

menu()
p.preprocess()

"""How I'd like to build out this page:
1. Fetch the relative effort from the activities.csv file
    a. Refactor the load process for that CSV file using the code within calculate_relative_effort_by_week
        - This is necessary because the perceived/actual relative efforts need to be reconciled. 
2. Calculate the relative effort by week using calculate_relative_effort_by_week from utilities.strava
3. Get the relative effort for a 12-week window - not clear how Strava decides which 12 to show.
    Best option may be to figure out how many following weeks are available, grab up to 5 of those, then do 6 trailing
    + current window for the 12. Essentially try to center the activity within the window.
4. Graph all twelve points with the Monday starting the week as the X axis label
"""