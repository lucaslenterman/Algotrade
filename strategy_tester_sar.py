import config
import talib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance import Client

from strategy_two import strategy_two


def retrieve_data(days: int, TRADE_SYMBOL: str):

    if days <= 0:
        print(f"Days must be positive value")
        raise ValueError

    closes = []
    lows = []
    highs = []

    client = Client(config.API_KEY, config.API_SECRET)

    # API CALL
    strategy_one_klines = client.get_historical_klines(TRADE_SYMBOL,
                                                       Client.KLINE_INTERVAL_5MINUTE,
                                                       f"{days} days ago UTC")

    for i in strategy_one_klines:
        closes.append(float(i[4]))
        lows.append(float(i[3]))
        highs.append(float(i[2]))

    return closes, highs, lows


def retrieve_data_string(time_start, time_end, TRADE_SYMBOL: str):

    closes = []
    lows = []
    highs = []

    client = Client(config.API_KEY, config.API_SECRET)

    # API CALL
    strategy_one_klines = client.get_historical_klines(TRADE_SYMBOL,
                                                       Client.KLINE_INTERVAL_5MINUTE,
                                                       time_start, time_end)

    for i in strategy_one_klines:
        closes.append(float(i[4]))
        lows.append(float(i[3]))
        highs.append(float(i[2]))

    return closes, highs, lows


def plot_trades(x: list, trades: pd.DataFrame, days: int, TRADE_SYMBOL: str):
    plt.style.use('Solarize_Light2')
    plt.plot(x, label='closes', color='black')
    for ind, row in trades.iterrows():
        if row['Buy']:
            plt.axvline(row['Time'], color='blue', linewidth='0.5')
        else:
            plt.axvline(row['Time'], color='red', linewidth='0.5')

    highs = np.array(retrieve_data(days=days, TRADE_SYMBOL=TRADE_SYMBOL)[1])
    lows = np.array(retrieve_data(days=days, TRADE_SYMBOL=TRADE_SYMBOL)[0])
    sar = talib.SAR(highs, lows)
    plt.plot(sar, label='SAR', color='green', linestyle=(0, (1, 5)))

    plt.legend(loc='best')
    plt.show()


def main():

    # PREP
    TRADE_SYMBOL = 'ETHUSDT'
    default_balance = 100
    default_days = 2
    start = "9 Jun, 2021"
    end = "21 Jun 2021"
    by_start_and_end = True

    # set threshold of lags to calculate indicators
    strategy_two_threshold = 5

    balance_one = default_balance
    in_position_one = False
    waiting = True
    buy_round = False
    sell_round = False
    strategy_two_statuses = [balance_one, in_position_one, waiting, buy_round, sell_round]

    if by_start_and_end:
        closes, highs, lows = retrieve_data_string(start, end, TRADE_SYMBOL=TRADE_SYMBOL)
    else:
        closes, highs, lows = retrieve_data(days=default_days, TRADE_SYMBOL=TRADE_SYMBOL)
    strategy_two_trades = pd.DataFrame(columns=['Time', 'Price', 'Buy'])

    for ind, (close, high, low) in enumerate(zip(closes, highs, lows)):
        if ind > strategy_two_threshold:
            high_history = highs[ind - strategy_two_threshold:ind]
            low_history = lows[ind - strategy_two_threshold:ind]
            close_history = closes[ind - strategy_two_threshold:ind]
            strategy_two_statuses = strategy_two(close=close,
                                                 high_history=high_history,
                                                 low_history=low_history,
                                                 close_history=close_history,
                                                 statuses=strategy_two_statuses,
                                                 trades=True)
        if strategy_two_statuses[3]:
            strategy_two_trades = strategy_two_trades.append(pd.DataFrame(data=[[ind, close, True]],
                                                                          columns=strategy_two_trades.columns))
        if strategy_two_statuses[4]:
            strategy_two_trades = strategy_two_trades.append(pd.DataFrame(data=[[ind, close, False]],
                                                                          columns=strategy_two_trades.columns))
    # retrieve final balance
    strategy_return = strategy_two_statuses[0] - balance_one
    market_return = ((closes[-1] - closes[0]) / closes[0]) * 100

    print('------------------')
    print('STRATEGY GAIN/LOSS %')
    print(strategy_return)
    print('------------------')
    print('MARKET GAIN/LOSS %')
    print(market_return)
    print('------------------')

    plot_trades(x=closes, trades=strategy_two_trades, days=default_days, TRADE_SYMBOL=TRADE_SYMBOL)


if __name__ == '__main__':
    main()
