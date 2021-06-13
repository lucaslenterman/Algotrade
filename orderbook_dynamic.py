import config
from binance import Client
import json
from matplotlib import pyplot as plt
import pprint
from matplotlib.animation import FuncAnimation
from orderbook import fetch_orderbook, fetch_largest_orders
from strategy_tester_sar import retrieve_data

client = Client(config.API_KEY, config.API_SECRET)

TRADE_SYMBOL = 'ETHUSDT'


recent_prices = []


def retrieve_prices(symbol):
    tickers = client.get_ticker(symbol=symbol)
    recent_prices.append(float(tickers['lastPrice']))
    return recent_prices


def plot_data(i):
    plt.style.use('Solarize_Light2')
    prices = retrieve_prices(TRADE_SYMBOL)
    largest_ask_size = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[1]
    largest_bid_size = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[3]
    largest_ask_price = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[2]
    largest_bid_price = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[4]
    second_largest_ask_price = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[6]
    second_largest_ask_size = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[5]
    second_largest_bid_price = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[8]
    second_largest_bid_size = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[7]

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
ani = FuncAnimation(fig, plot_data, interval=10)
plt.show()



