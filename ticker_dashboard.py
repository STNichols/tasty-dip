"""
Description: Dashboard to interact with option visuals
"""

import datetime
import streamlit as st
from wallstreet import Stock

from option_utils import (
    collect_option_data,
    plot_option_percent_gain,
    plot_option_asset_value
)

# Constants
FRIDAY_WEEKDAY = 4
TODAY = datetime.datetime.today()
DAYS_BACK = {
    'week':7,
    'month':30,
    'year':365
}

# Streamlit Configuration
st.set_page_config(layout="wide")

# Find next Friday
day_diff = FRIDAY_WEEKDAY - TODAY.weekday()
if day_diff < 0:
    day_diff = 7 + day_diff
next_friday = TODAY + datetime.timedelta(days=day_diff)

# Title
col1, col2 = st.beta_columns((1, 2))
col1.title("Do I like the Stock?")
col2.image('imgs/wsb.jpg')

# Column 1 inputs
col1, col2, col3, col4 = st.beta_columns((3, 1, 1, 5))
ticker = col1.text_input('Ticker:')
if ticker == "GME":
    col2.image('imgs/diamond.jpg')
    col3.image('imgs/hands.jpg')

# Check for Ticker
if ticker:
    
    stock = Stock(ticker)
    
    # Stock Information Section
    st.header(stock.name)
    
    col1, col2, col3, col4, col5 = st.beta_columns(5)
    
    # Show Info
    col1.write('Current Price ($)')
    col1.write(stock.price)
    
    col2.write('Daily Change:')
    col2.write(f"${stock.change}")
    col2.write(f"{stock.cp} %")
    
    # Historicals 
    price_view = col3.radio("Select Time Period:", ('week', 'month', 'year'), index=1)
    stock_data = stock.historical(days_back=DAYS_BACK[price_view])
    price = stock_data['Close'].values
    pc = price[-1] - price[0]
    pcp = int(100 * (price[-1] - price[0]) / price[0] * 100) / 100
    
    col4.write(price_view.capitalize() + 'ly Change:')
    col4.write(f"${pc}")
    col4.write(f"{pcp} %")
    
    if pc < 0:
        col5.image('imgs/hanginthere.jpg')
    else:
        col5.image('imgs/rocket.jpg')
    
    # Visualize
    st.line_chart(stock_data[['Date', 'Close', 'Low', 'High']].set_index('Date'))
    st.bar_chart(stock_data[['Date', 'Volume']].set_index('Date'), width=200)
    
    # Collect Options Information
    col1, col2, col3 = st.beta_columns(3)
    col1.title(f"Call Options: {ticker}")
    col1.write('Cause stonks only go up')
    col3.image('imgs/stonks.jpg')
    
    col1, col2 = st.beta_columns(2)
    option_date = col1.date_input("Call Option Expiration Date:", next_friday)
    col1.write('(Defaults to closest available date)')
        
    initial = col2.number_input('$ purchase of contracts:', value=10000.0, step=1000.0)
    col2.write('(Buy N contracts up to this amount)')

    # Collect initial date
    year = option_date.year
    month = option_date.month
    day = option_date.day
    
    # Collect the data
    data = collect_option_data(ticker, year, month, day, strict=False)
    actual_date = data['date'][0]
    year = actual_date.year
    month = actual_date.month
    day = actual_date.day
    
    st.subheader(f"Options Date: {month}/{day}/{year}")
    
    st.subheader('Percent Gain')
    pc_fig, pc_ax = plot_option_percent_gain(
        ticker, year, month, day, data=data
    )
    st.pyplot(pc_fig)
    
    st.subheader('Net Value of Assets')
    st.write('(Note: Areas of no change may imply that no contracts' +
             ' are available at that initial investment or strike price)')
    asset_fig, asset_ax = plot_option_asset_value(
        ticker, year, month, day, initial=initial, data=data
    )
    st.pyplot(asset_fig)
    
    st.image('imgs/loss.jpg')
    st.subheader('(Not a financial advisor)')