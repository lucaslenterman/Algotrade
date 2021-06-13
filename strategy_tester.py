import json
import math
import pprint
import csv
from decimal import Decimal
import websocket
# from binance.client import Client
# from binance.exceptions import BinanceAPIException
import config
import pdb
import talib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance import Client

from strategy_one import strategy_one


default_days = 10


def retrieve_data(days: int):

    if days <= 0:
        print(f"Days must be positive value")
        raise ValueError

    closes = []
    lows = []
    highs = []

    client = Client(config.API_KEY, config.API_SECRET)
    TRADE_SYMBOL = 'BTCUSDT'

    # API CALL
    strategy_one_klines = client.get_historical_klines(TRADE_SYMBOL,
                                                       Client.KLINE_INTERVAL_1MINUTE,
                                                       f"{days} days ago UTC")

    for i in strategy_one_klines:
        closes.append(float(i[4]))
        lows.append(float(i[3]))
        highs.append(float(i[2]))

    return closes, highs, lows

# to do: create time index for matching plot with trades
# trades, e.g.:     strategy_one_trades = pd.DataFrame(columns=['Time', 'Price', 'Buy'])
# x: list of y values


def plot_trades(x: list, trades: pd.DataFrame):
    plt.plot(x, label='closes', color='black')
    for ind, row in trades.iterrows():
        if row['Buy']:
            plt.axvline(row['Time'], color='blue', linewidth='0.5')
        else:
            plt.axvline(row['Time'], color='red', linewidth='0.5')

    closes = retrieve_data(default_days)[0]
    np_closes = np.array(closes)
    wma144 = talib.WMA(np_closes, 144)
    sma5 = talib.SMA(np_closes, 5)
    plt.plot(wma144, '--', color='green', linewidth='0.5', label='WMA144')
    plt.plot(sma5, color='slategrey', linewidth='0.5', label='SMA5')
    plt.legend(loc='best')
    plt.show()


def main():

    # PREP
    
    # set threshold of lags to calculate indicators
    strategy_one_threshold = 144

    closes, highs, lows = retrieve_data(default_days)

    # set statuses for strategy one to default values before beginning
    balance_one = 100
    in_position_one = False
    waiting = True
    trend = False
    trend_ind = False
    counter_one = []
    counter_two = []
    tsl_ref_close = None
    buy_round = False
    sell_round = False

    # store statuses in list to be passed to function each round
    strategy_one_statuses = [balance_one, in_position_one, waiting, trend, trend_ind,
                             counter_one, counter_two, tsl_ref_close, buy_round, sell_round]

    # run algorithm on simulated data
    strategy_one_trades = pd.DataFrame(columns=['Time', 'Price', 'Buy'])

    for ind, close in enumerate(closes):

        if ind > strategy_one_threshold:
            history = closes[ind - strategy_one_threshold:ind]
            strategy_one_statuses = strategy_one(close=close,
                                                 history=history,
                                                 statuses=strategy_one_statuses,
                                                 trades=True)
        if strategy_one_statuses[8]:
            strategy_one_trades = strategy_one_trades.append(pd.DataFrame(data=[[ind, close, True]],
                                                                          columns=strategy_one_trades.columns))
        if strategy_one_statuses[9]:
            strategy_one_trades = strategy_one_trades.append(pd.DataFrame(data=[[ind, close, False]],
                                                                          columns=strategy_one_trades.columns))
    # retrieve final balance
    strategy_return = strategy_one_statuses[0] - 100
    market_return = ((closes[-1] - closes[0]) / closes[0]) * 100

    print('------------------')
    print('STRATEGY GAIN/LOSS %')
    print(strategy_return)
    print('------------------')
    print('MARKET GAIN/LOSS %')
    print(market_return)
    print('------------------')

    plot_trades(x=closes, trades=strategy_one_trades)


if __name__ == '__main__':
    main()
