import config
from binance import Client
import json
from matplotlib import pyplot as plt
import pprint

client = Client(config.API_KEY, config.API_SECRET)

TRADE_SYMBOL = 'ETHUSDT'


def retrieve_data(days):

    if days <= 0:
        print(f"Days must be positive value")
        raise ValueError

    closes = []

    strategy_one_klines = client.get_historical_klines(TRADE_SYMBOL,
                                                       Client.KLINE_INTERVAL_1MINUTE,
                                                       f"{days} days ago UTC")

    for i in strategy_one_klines:
        closes.append(float(i[4]))

    return closes


def plot_data(closes):
    plt.style.use('Solarize_Light2')
    plt.plot(closes, color='black')
    ask_label = 'ASK PRICE: ' + str(round(float(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[2]), 2))\
                + ' SIZE: ' + str(round(float(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[1]), 2))
    bid_label = 'BID PRICE: ' + str(round(float(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[4]), 2))\
                + ' SIZE: ' + str(round(float(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[3]), 2))

    ask_label2 = '2ND ASK PRICE: ' + str(round(float(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[6]), 2))\
                 + ' SIZE: ' + str(round(float(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[5]), 2))
    bid_label2 = '2ND BID PRICE: ' + str(round(float(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[8]), 2))\
                 + ' SIZE: ' + str(round(float(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[7]), 2))

    plt.axhline(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[2], color='red', linestyle='--', label=ask_label)
    plt.axhline(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[4], color='blue', linestyle='--', label=bid_label)
    plt.axhline(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[6], color='red', linestyle='--', label=ask_label2,
                linewidth='0.7')
    plt.axhline(fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[8], color='blue', linestyle='--', label=bid_label2,
                linewidth='0.7')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()


def fetch_orderbook_ticker(trade_symbol):
    orderbook_ticker_info = client.get_orderbook_ticker(symbol=trade_symbol)
    bid_price = round(float(orderbook_ticker_info['bidPrice']), 2)
    ask_price = round(float(orderbook_ticker_info['askPrice']), 2)
    return ask_price, bid_price


def fetch_orderbook(trade_symbol):
    book = client.get_order_book(symbol=trade_symbol)
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


def orderbook(cycle):
    counter = 0
    while counter < cycle:
        market_d = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[0]
        largest_ask_s = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[1]
        corr_ask_price = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[2]
        largest_bid_s = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[3]
        corr_bid_price = fetch_largest_orders(fetch_orderbook(TRADE_SYMBOL))[4]
        ask_price = fetch_orderbook_ticker(TRADE_SYMBOL)[0]
        bid_price = fetch_orderbook_ticker(TRADE_SYMBOL)[1]
        market_d_round = round(market_d, 6)

        book = [['DEPTH', market_d_round], ['LARGEST BID', largest_bid_s, 'PRICE', corr_bid_price],
                ['LARGEST ASK', largest_ask_s, 'PRICE', corr_ask_price], ['FIRST ASK', ask_price],
                ['FIRST BID', bid_price]]

        pprint.pprint(book)
        print()
        counter = counter + 1


def main():
    plot_data(retrieve_data(1))
    orderbook(100)


if __name__ == '__main__':
    main()
