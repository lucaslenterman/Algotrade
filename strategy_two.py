import numpy as np
import talib as ta


def strategy_two(close: float,
                 high_history: list,
                 low_history: list,
                 close_history: list,
                 statuses: list,
                 trades: bool):



    default_in_position = False
    default_waiting = True
    default_buy_round = False
    default_sell_round = False

    balance = statuses[0]
    in_position = statuses[1]
    waiting = statuses[2]
    buy_round = default_buy_round
    sell_round = default_sell_round

    prior_highs = np.array(high_history)
    prior_lows = np.array(low_history)
    sar = ta.SAR(prior_highs, prior_lows)[-1]

    if not in_position:
        if waiting:
            if sar > close:
                waiting = False
                in_position = True
                buy_round = True
                if trades:
                    print(f"Bought at ${close}")

    if in_position:
        if not buy_round:
            balance = (close / close_history[-1]) * balance
        if sar < close:
            waiting = default_waiting
            in_position = default_in_position
            sell_round = True
            if trades:
                print(f"Sold at ${close}. Updated balance: {balance}")


    updated_statuses = [balance, in_position, waiting, buy_round, sell_round]

    return updated_statuses
