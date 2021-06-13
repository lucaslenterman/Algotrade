import plotly.graph_objects as go
from binance import Client
import pandas as pd
import config
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State


TRADE_SYMBOL = 'ETHUSDT'
client = Client(config.API_KEY, config.API_SECRET)


def retrieve_data(days: int):

    if days <= 0:
        print(f"Days must be positive value")
        raise ValueError

    close = []
    low = []
    high = []
    openx = []

    # API CALL
    strategy_one_klines = client.get_historical_klines(TRADE_SYMBOL,
                                                       Client.KLINE_INTERVAL_5MINUTE,
                                                       f"{days} days ago UTC")

    for i in strategy_one_klines:
        close.append(float(i[4]))
        low.append(float(i[3]))
        high.append(float(i[2]))
        openx.append(float(i[1]))

    return close, high, low, openx


def get_x(close_no):
    i = 0
    x = []
    while i <= close_no:
        x.append(i)
        i = i + 1
    return x


closes = retrieve_data(10)[0]
highs = retrieve_data(10)[1]
lows = retrieve_data(10)[2]
opens = retrieve_data(10)[3]
x_len = get_x(len(closes))



fig = go.Figure(data=go.Candlestick(x=x_len, open=opens, high=highs, low=lows, close=closes))

fig.show()



