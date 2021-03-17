"""
Description: Utility functions to transform option data
"""

import datetime
import numpy as np
import pandas as pd
from wallstreet import Stock, Call, Put
import matplotlib.pyplot as plt
import matplotlib.colors as colors


def collect_option_data(ticker, year, month, day, strict=True):
    """ Collect the option data for the given date """
    
    date = datetime.datetime(year=year, month=month, day=day)

    dates = []
    strikes = []
    prices = []
    prices_pc = []
    
    print(f"Call for year:{year}, month:{month}, day:{day}")

    call_setup = False
    attempts = 0
    while not call_setup and attempts < 10:
        try:
            wc = Call(ticker, d=day, m=month, y=year, strict=strict)
            print("Success!")
            call_setup = True
        except:
            attempts += 1
    attempts = 0

    if call_setup:
        for cdata in wc.data:
            strikes.append(cdata['strike'])
            prices.append(cdata['lastPrice'])
            prices_pc.append(cdata['percentChange'])
            dates.append(date)

    data = pd.DataFrame({'date':dates, 'price':prices, 'strike':strikes})

    return data


def calculate_gains(strike_price, share_price, call_price, n_calls=1, percentage=True):
    """ Calculate the percent gain given N call options and a share price """
    
    gains = (share_price - strike_price) * 100 * n_calls
    cost = call_price * 100 * n_calls
    
    if percentage:
        net = (gains - cost) / cost
    else:
        net = gains - cost
    
    return net


def plot_option_percent_gain(ticker, year, month, day, strict_date=True):
    """
    Plot mesh grid of scenarios for a given call option and the
    resulting percent gain
    """
    
    fig, ax = plt.subplots(figsize=(15,10))
    
    data = collect_option_data(ticker, year, month, day, strict=strict_date)
    stock = Stock(ticker)
    current_price

    # Make data.
    strike_price = data['strike']
    share_price = np.arange(0, data['strike'].max() * 1.5, current_price / 100)
    call_price_mesh = np.tile(data['price'].T, (len(share_price), 1))
    strike_mesh, stock_mesh = np.meshgrid(strike_price, share_price)
    percent_gains = calculate_gains(strike_mesh, stock_mesh, call_price_mesh, n_calls=1)

    # Plot the mesh grid and percent gain surfaces
    pg_min = percent_gains.min()
    pg_max = percent_gains.max()
    pos_array = np.concatenate((np.arange(0, 100, 5), np.arange(100, 1100, 100)))
    bounds = np.sort(np.concatenate((-1 * pos_array, pos_array)))
    norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256, clip=True)
    c = ax.pcolormesh(
        strike_mesh,
        stock_mesh,
        percent_gains,
        cmap='RdYlGn',
        norm=norm
    )

    ax.set_title(f'Call Options {ticker} {month}/{day}')
    ax.set_ylabel('Stock Price ($)')
    ax.set_xlabel('Strike Price ($)')
    cbar = fig.colorbar(c, ax=ax, extend='neither', orientation='vertical')
    cbar.set_label('Percent Gains (%)')

    ax.axhline(s.price, linestyle='--', color='black')
    
    return fig, ax