import asyncio
import pprint
import math
from kucoin.client import Client
import requests
import json
from matplotlib import pyplot as plt
import pprint
from matplotlib.animation import FuncAnimation

api_key = '6086e6115dcad70006dc5ce5'
api_secret = '6bf2eebd-456f-474a-82e5-9cec9dd408b9'
api_passphrase = 'Lenterman01'
trade_symbol = 'ETH-USDT'

recent_prices = []

client = Client(api_key, api_secret, api_passphrase)


def fetch_orderbook(symbol):
    book = client.get_order_book(symbol=symbol)
    return book


def fetch_largest_orders(depth):

    depth1 = json.dumps(depth)
    depth2 = json.loads(depth1)

    bids = depth2['bids']
    asks = depth2['asks']

    bid_prices = []
    bid_sizes = []

    ask_prices = []
    ask_sizes = []

    i = 0

    while i < len(bids) and len(asks):
        bid_sizes.append(float(bids[i][1]))
        bid_prices.append(float(bids[i][0]))
        ask_sizes.append(float(asks[i][1]))
        ask_prices.append(float(asks[i][0]))
        i = i + 1

    smallest_ask_price = min(ask_prices)
    highest_bid_price = max(bid_prices)

    largest_ask_size = max(ask_sizes)
    largest_bid_size = max(bid_sizes)

    ask_size_index = ask_sizes.index(largest_ask_size)
    corresponding_ask_price = ask_prices[ask_size_index]

    bid_size_index = bid_sizes.index(largest_bid_size)
    corresponding_bid_price = bid_prices[bid_size_index]

    new_ask_s = ask_sizes
    new_ask_p = ask_prices
    new_bid_s = bid_sizes
    new_bid_p = bid_prices

    new_ask_s.remove(largest_ask_size)
    new_ask_p.remove(corresponding_ask_price)
    new_bid_s.remove(largest_bid_size)
    new_bid_p.remove(corresponding_bid_price)

    new_ask_s_max = max(new_ask_s)
    new_ask_s_max_i = new_ask_s.index(new_ask_s_max)
    new_ask_p_max = new_ask_p[new_ask_s_max_i]

    new_bid_s_max = max(new_bid_s)
    new_bid_s_max_i = new_bid_s.index(new_bid_s_max)
    new_bid_p_max = new_bid_p[new_bid_s_max_i]

    market_depth = smallest_ask_price - highest_bid_price

    return market_depth, largest_ask_size, corresponding_ask_price, largest_bid_size, corresponding_bid_price, \
           new_ask_s_max, new_ask_p_max, new_bid_s_max, new_bid_p_max


def retrieve_prices(symbol):
    tickers = client.get_ticker(symbol=symbol)
    recent_prices.append(float(tickers['price']))
    return recent_prices



def plot_data(i):
    plt.style.use('Solarize_Light2')
    prices = retrieve_prices(trade_symbol)
    largest_ask_size = fetch_largest_orders(fetch_orderbook(trade_symbol))[1]
    largest_bid_size = fetch_largest_orders(fetch_orderbook(trade_symbol))[3]
    largest_ask_price = fetch_largest_orders(fetch_orderbook(trade_symbol))[2]
    largest_bid_price = fetch_largest_orders(fetch_orderbook(trade_symbol))[4]
    second_largest_ask_price = fetch_largest_orders(fetch_orderbook(trade_symbol))[6]
    second_largest_ask_size = fetch_largest_orders(fetch_orderbook(trade_symbol))[5]
    second_largest_bid_price = fetch_largest_orders(fetch_orderbook(trade_symbol))[8]
    second_largest_bid_size = fetch_largest_orders(fetch_orderbook(trade_symbol))[7]

    plt.cla()

    plt.plot(prices, label='PRICE: ' + str(prices[-1]))
    plt.axhline(largest_ask_price,
                color='red',
                linestyle='--',
                label='LARGEST ASK: ' + str(largest_ask_price) + ' SIZE: ' + str(largest_ask_size))
    plt.axhline(largest_bid_price,
                color='blue',
                linestyle='--',
                label='LARGEST BID: ' + str(largest_bid_price) + ' SIZE: ' + str(largest_bid_size))
    plt.axhline(second_largest_ask_price,
                color='red', linestyle='--',
                linewidth='0.7',
                label='2ND LARGEST ASK: ' + str(second_largest_ask_price) + ' SIZE: ' + str(second_largest_ask_size))
    plt.axhline(second_largest_bid_price,
                color='blue',
                linestyle='--',
                linewidth='0.7',
                label='2ND LARGEST BID: ' + str(second_largest_bid_price) + ' SIZE: ' + str(second_largest_bid_size))
    plt.legend(loc='upper left', prop={'size': 10})


fig = plt.figure()
ani = FuncAnimation(fig, plot_data, interval=100)
plt.show()

