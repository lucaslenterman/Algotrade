import numpy as np
import talib


def strategy_one(close: float,
                 history: list,
                 statuses: list,
                 trades: bool):

    # percentage loss at which we sell (e.g., sell threshold is 10% (0.1) then the pct loss we sell at is 1 - 0.1 = 90%)
    tsl_sell_pct = 0.95
    sma_multiplier = 1.01

    # define the default values for our indicators
    default_in_position = False
    default_waiting = True
    default_trend = False
    default_trend_ind = False
    default_buy_round = False
    default_sell_round = False

    # unpack statuses
    balance = statuses[0]
    in_position = statuses[1]
    waiting = statuses[2]
    trend = statuses[3]
    trend_ind = statuses[4]
    counter_one = statuses[5]
    counter_two = statuses[6]
    tsl_reference_value = statuses[7]
    buy_round = default_buy_round
    sell_round = default_sell_round

    # calculate indicators from past asset prices
    prior_closes = np.array(history)
    wma144 = talib.WMA(prior_closes, 144)[-1]
    sma5 = talib.SMA(prior_closes, 5)[-1]
    rsi14 = talib.RSI(prior_closes, 14)[-1]

    # decide when to buy
    if not in_position:
        if waiting:  # WAITING FOR SMA TO CROSS OVER WMA
            if sma5 > wma144:
                trend = True
                waiting = False

        if not waiting:
            if trend:  # WAITING FOR WMA TO CROSS BACK OVER SMA
                counter_one.append(close)
                if wma144 > sma5:
                    trend_ind = True
                    trend = False
                if len(counter_one) > 3000000:
                    waiting = default_waiting
                    trend = default_trend
                    counter_one.clear()

            if trend_ind:  # WAITING FOR BULLISH CONFIRMATION
                counter_two.append(close)
                if sma5 > wma144 and rsi14 < 100:
                    # BUYS
                    waiting = False
                    in_position = True
                    buy_round = True
                    if trades:
                        print(f"Bought at ${close}")
                if len(counter_two) > 1000000:
                    waiting = default_waiting
                    trend_ind = default_trend_ind
                    counter_two.clear()

    if in_position:

        #  IF WE JUST BOUGHT:
        if buy_round:
            # set TSL reference value as current close
            tsl_reference_value = close

        # IF WE DIDN'T JUST BUY:
        else:
            # update balance
            balance = (close / history[-1]) * balance

            # update TSL reference value if current close is greater
            if close > tsl_reference_value:
                tsl_reference_value = close

            # decide whether we sell
            if close < tsl_reference_value * tsl_sell_pct or wma144 > sma5*sma_multiplier:
                # reset indicators to default values
                in_position = default_in_position
                waiting = default_waiting
                trend = default_trend
                trend_ind = default_trend_ind
                sell_round = True

                if trades:
                    print(f"Sold at ${close}. Updated balance: {balance}")

    updated_statuses = [balance, in_position, waiting, trend, trend_ind,
                        counter_one, counter_two, tsl_reference_value, buy_round, sell_round]

    return updated_statuses
