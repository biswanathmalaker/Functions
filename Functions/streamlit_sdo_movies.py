import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
import copy
# Downloading all the movies in 193 and 171;
# Marging them and keeping them aside for future use.

# Given start date and end date and wavelength;
# On selecting check box generate movie links.


start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
st.write("Dates include both start date and end date")
DATES = []

d = copy.deepcopy(start_date)
# while d<end_date:
#     DATES.append(d.strftime("%Y-%m-%d"))




