"""
Description: Dashboard to interact with option visuals
"""

# Base Python
import datetime
import streamlit as st

# Pkg
from option_utils import (
    plot_option_percent_gain,
    plot_option_asset_value
)

# Constants
FRIDAY_WEEKDAY = 4
TODAY = datetime.datetime.today()

# Streamlit Configuration
st.set_page_config(layout="wide")

# Find next Friday
day_diff = FRIDAY_WEEKDAY - TODAY.weekday()
if day_diff < 0:
    day_diff = 7 - day_diff
next_friday = TODAY + datetime.timedelta(days=day_diff)

# Title
st.title("Visualizing Option Scenarios")

# Setup two columns of inputs
col1, col2 = st.beta_columns(2)

# Column 1 inputs
ticker = col1.text_input('Ticker:')
option_date = col1.date_input("Call Option Expiration Date:", next_friday)
flex_date = col1.checkbox('Find closest date if not found')
strict_date = not flex_date

# Column 2 inputs
initial = col2.number_input('$ of contracts bought:', value=1000.0, step=1000.0)
col2.write(initial)

# Check for Ticker
if ticker:
    st.header(f"Analyzing Call Options: {ticker} - " +
              f"{option_date.month}/{option_date.day}/{option_date.year}")
    
    col1, col2 = st.beta_columns(2)
    
    col1.subheader('Percent Gain')
    col1.write('     ')
    pc_fig, pc_ax = plot_option_percent_gain(
        ticker,
        option_date.year,
        option_date.month,
        option_date.day,
        strict_date=(not strict_date)
    )
    col1.pyplot(pc_fig)
    
    col2.subheader('Net Value of Assets')
    col2.write('(Exercised if ITM)')
    asset_fig, asset_ax = plot_option_asset_value(
        ticker,
        option_date.year,
        option_date.month,
        option_date.day,
        initial,
        strict_date=strict_date
    )
    col2.pyplot(asset_fig)