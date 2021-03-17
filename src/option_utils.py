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
    
    call_setup = False
    attempts = 0
    while not call_setup and attempts < 10:
        try:
            wc = Call(ticker, d=day, m=month, y=year, strict=strict)
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


def calculate_gains(strike_price, share_price, call_price, initial=None):
    """ Calculate the net gains given option data and a share price """
    
    # Calculate current value
    gains = (share_price - strike_price) * 100
    # OTM is worth nothing, not negative
    gains[gains < 0] = 0.0
    
    # Cost of a single contract
    cost = call_price * 100
    
    if initial:
        n_contracts = initial / cost
        net = gains * n_contracts
    else:
        net = ((gains - cost) / cost) * 100
    
    return net


def plot_option_percent_gain(ticker, year, month, day, strict_date=True):
    """
    Plot mesh grid of scenarios for a given call option and the
    resulting percent gain
    """
    
    fig, ax = plt.subplots()
    
    data = collect_option_data(ticker, year, month, day, strict=strict_date)
    stock = Stock(ticker)
    current_price = stock.price

    # Make data.
    strike_price = data['strike']
    share_price = np.arange(0, data['strike'].max() * 1.5, current_price / 100)
    call_price_mesh = np.tile(data['price'].T, (len(share_price), 1))
    strike_mesh, stock_mesh = np.meshgrid(strike_price, share_price)
    percent_gains = calculate_gains(strike_mesh, stock_mesh, call_price_mesh)

    # Plot the mesh grid and percent gain surfaces
    pg_min = percent_gains.min()
    pg_max = percent_gains.max()
    positive = np.concatenate((np.arange(0, 100, 5), np.arange(100, 1100, 100)))
    negative = np.linspace(-100, 0, len(positive))
    bounds = np.concatenate((negative, positive))
    norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)
    c = ax.pcolormesh(
        strike_mesh,
        stock_mesh,
        percent_gains,
        cmap='RdYlGn',
        norm=norm
    )
    
    # Plot mesh grid evaluating option results
    ax.set_ylabel('Stock Price ($)')
    ax.set_xlabel('Strike Price ($)')
    cbar = fig.colorbar(c, ax=ax, extend='neither', orientation='vertical')
    cbar.set_label('Percent Gains (%)')

    # Plot Current Price
    ax.axhline(current_price, linestyle='--', color='black', label='Current Price')
    ax.legend()
    ax.grid(True)
    
    return fig, ax


def plot_option_asset_value(ticker, year, month, day, initial, strict_date=True):
    """
    Plot mesh grid of scenarios for a given call option and the
    resulting asset value (exercised if ITM)
    """
    
    fig, ax = plt.subplots()
    
    data = collect_option_data(ticker, year, month, day, strict=strict_date)
    stock = Stock(ticker)
    current_price = stock.price

    # Make data.
    strike_price = data['strike']
    share_price = np.arange(0, data['strike'].max() * 1.5, current_price / 100)
    call_price_mesh = np.tile(data['price'].T, (len(share_price), 1))
    strike_mesh, stock_mesh = np.meshgrid(strike_price, share_price)
    asset_value = calculate_gains(
        strike_mesh,
        stock_mesh,
        call_price_mesh,
        initial=initial
    )

    # Plot the mesh grid and percent gain surfaces
    av_min = asset_value.min()
    av_max = asset_value.max()
    bounds = np.geomspace(av_min + 0.00001, av_max / 100000, num=50) * 100000
    bounds[0] = 0.0 # Maintain 0 as min
    positive = np.geomspace(initial / 1000, av_max / 1000, num=25) * 1000
    positive = np.round(positive / 10) * 10
    negative = np.linspace(0, initial, len(positive))
    bounds = np.concatenate((negative, positive))
    norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256, clip=True)
    c = ax.pcolormesh(
        strike_mesh,
        stock_mesh,
        asset_value,
        cmap='RdYlGn',
        norm=norm
    )
    
    # Plot mesh grid evaluating option results
    ax.set_ylabel('Stock Price ($)')
    ax.set_xlabel('Strike Price ($)')
    cbar = fig.colorbar(c, ax=ax, extend='neither', orientation='vertical')
    cbar.set_label('Value of Assets ($)')

    # Plot Current Price
    ax.axhline(current_price, linestyle='--', color='black', label='Current Price')
    ax.legend()
    ax.grid(True)
    
    return fig, ax