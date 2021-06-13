import config
import matplotlib.pyplot as plt
from binance import Client
import numpy as np


client = Client(config.API_KEY, config.API_SECRET)
trade_symbol = 'ETHUSDT'


def fetch_orders(symbol):
    orders = client.get_all_orders(symbol=symbol)
    return orders


def plot_order_data(order_data, ignore_orders):
    buys = []
    sells = []
    buys_quantities = []
    sells_quantities = []
    coin_quant_buy = []
    coin_quant_sell = []
    buy_prices = []
    sell_prices = []

    for item in order_data:
        if item['side'] == 'BUY':
            buys.append(float(item['price']))
            buys_quantities.append(float(item['cummulativeQuoteQty']))
            coin_quant_buy.append(float(item['executedQty']))
        if item['side'] == 'SELL':
            sells.append(float(item['price']))
            sells_quantities.append(float(item['cummulativeQuoteQty']))
            coin_quant_sell.append(float(item['executedQty']))

    for a, b in zip(buys_quantities[ignore_orders:], coin_quant_buy[ignore_orders:]):
        if a and b != 0:
            buy_prices.append(a/b)

    for a, b in zip(sells_quantities[ignore_orders:], coin_quant_sell[ignore_orders:]):
        if a and b != 0:
            sell_prices.append(a/b)

    for a in sell_prices:
        round(a, 2)

    for a in buy_prices:
        round(a, 2)

    sell_qs = sells_quantities[ignore_orders:]
    buy_qs = buys_quantities[ignore_orders:]

    sell_len = len(sell_qs)
    buy_len = len(buy_qs)

    indexes = []
    sell_indexes = []
    buy_indexes = []
    differences = []
    diff_index = []

    i = 0

    while i <= sell_len + buy_len:
        indexes.append(i)
        i = i + 1

    for num in indexes:
        if num % 2 != 0:
            sell_indexes.append(num)
        else:
            buy_indexes.append(num)

    for a, b in zip(buy_prices, sell_prices):
        differences.append((b - a)/a * 100)

    i = 0
    while i <= len(differences):
        diff_index.append(i)
        i = i + 1

    while len(differences) > len(diff_index):
        differences.remove(differences[-1])

    while len(diff_index) > len(differences):
        diff_index.remove(diff_index[-1])

    while len(buy_qs) > len(sell_qs):
        buy_qs.remove(buy_qs[-1])

    while len(sell_qs) > len(buy_qs):
        sell_qs.remove(sell_qs[-1])

    result = [None]*(len(buy_qs)+len(sell_qs))
    result[::2] = buy_qs
    result[1::2] = sell_qs


    plt.style.use('Solarize_Light2')


    plt.figure(1)

    for a, b in zip(buy_indexes, buy_qs):
        plt.bar(a, b, color='blue')

    for a, b in zip(sell_indexes, sell_qs):
        plt.bar(a, b, color='red', joinstyle='bevel')

    coef = np.polyfit(diff_index, differences, 1)
    poly1d_fn = np.poly1d(coef)


    plt.figure(2)
    plt.scatter(diff_index, differences, s=10)
    plt.plot(diff_index, poly1d_fn(diff_index), color='red', linewidth='0.7')
    plt.axhline(0, color='black', linestyle='--', linewidth='0.7')

    plt.figure(3)
    plt.plot(result)

    plt.show()


def main():
    plot_order_data(fetch_orders(trade_symbol), 7)


if __name__ == '__main__':
    main()

