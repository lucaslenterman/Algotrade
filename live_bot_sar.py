import json
import websocket
from binance.client import Client
import config
import talib as ta
import numpy as np
import math

client = Client(config.API_KEY, config.API_SECRET)
socket = "wss://stream.binance.com:9443/ws/ethusdt@kline_5m"
trade_symbol = 'ETHUSDT'
in_position = False
waiting = True
sell_coin = 'ETH'


def retrieve_data(days: int):

    if days <= 0:
        print(f"Days must be positive value")
        raise ValueError

    close = []
    low = []
    high = []

    # API CALL
    strategy_one_klines = client.get_historical_klines(trade_symbol,
                                                       Client.KLINE_INTERVAL_5MINUTE,
                                                       f"{days} days ago UTC")

    for i in strategy_one_klines:
        close.append(float(i[4]))
        low.append(float(i[3]))
        high.append(float(i[2]))

    return close, high, low


closes_pre = retrieve_data(1)[0]
closes = closes_pre[-7:-1]
highs_pre = retrieve_data(1)[1]
highs = highs_pre[-6:-1]
lows_pre = retrieve_data(1)[2]
lows = lows_pre[-6:-1]


def round_decimals_down(number, decimals):
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor


def fetch_tradable_quantity(symbol):

    balance = client.get_asset_balance(asset='USDT')
    trades = client.get_recent_trades(symbol=symbol)
    quantity = (float(balance['free'])) / (float(trades[0]['price'])) * 0.995
    quantity_round = round_decimals_down(quantity, 5)
    return quantity_round


def fetch_sell_balance(asset):

    balance = client.get_asset_balance(asset=asset)
    quantity = float(balance['free']) * 0.995
    quantity_round = round_decimals_down(quantity, 5)
    return quantity_round


def market_buy_order(symbol, quantity):
    try:
        buy_order = client.order_market_buy(symbol=symbol, quantity=quantity)
        print(buy_order)
    except Exception as e:
        print(e)
        return False

    return buy_order, True


def market_sell_order(symbol, quantity):
    try:
        sell_order = client.order_market_sell(symbol=symbol, quantity=quantity)
        print(sell_order)
    except Exception as e:
        print(e)
        return False

    return sell_order, True


def on_open(ws):
    print("opened connection")


def on_close(ws):
    print("closed connections")


def on_error(ws, error):
    print(error)


def on_message(ws, message):
    global in_position
    global waiting
    candle_data = json.loads(message)
    candle = candle_data['k']
    is_candle_closed = candle['x']
    close_price = candle['c']
    high_price = candle['h']
    low_price = candle['l']

    if is_candle_closed:
        closes.append(float(close_price))
        highs.append(float(high_price))
        lows.append(float(low_price))
        print('new close')
        if len(closes) > 5:
            del highs[:-5]
            del lows[:-5]

    print(highs)
    print(lows)
    np_highs = np.array(highs)
    np_lows = np.array(lows)
    sar = ta.SAR(np_highs, np_lows)
    print(sar)

    if not in_position:
        if waiting:
            if sar[-1] > closes[-1]:
                print('in position... waiting to sell')
                print('CLOSE:', closes[-1])
                print('SAR:', sar[-1])
                # market_buy_order(trade_symbol, fetch_tradable_quantity(trade_symbol))
                in_position = True
                waiting = False

    if in_position:
        if sar[-1] < closes[-1]:
            print('sold... restarting')
            print('CLOSE:', closes[-1])
            print('SAR:', sar[-1])
            # market_sell_order(trade_symbol, fetch_sell_balance(sell_coin))
            waiting = True
            in_position = False


ws = websocket.WebSocketApp(socket, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
ws.run_forever()
