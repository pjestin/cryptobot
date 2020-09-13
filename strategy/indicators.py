import math
import logging
import time

import numpy as np


class Indicators:

    STOCH_RSI_RANGE = 100
    EMA_1_RANGE = 12
    EMA_2_RANGE = 26
    MACD_EMA_RANGE = 9

    @classmethod
    def simple_moving_average(cls, x, K, nb_period):
        return sum(x[K : K - nb_period : -1]) / nb_period

    exp_weights_cache = {}

    @classmethod
    def get_exp_weights(cls, nb_period):
        if nb_period == 1:
            return [1.]
        if nb_period not in cls.exp_weights_cache:
            A = math.log(1 - 2 / (nb_period + 1))
            exp_weights = [math.exp(k * A) for k in range(0, nb_period)]
            cls.exp_weights_cache[nb_period] = [exp_weight / sum(exp_weights) for exp_weight in exp_weights]
        return cls.exp_weights_cache[nb_period]

    @classmethod
    def exp_moving_average(cls, x, K, nb_period):
        normalized_exp_weights = cls.get_exp_weights(nb_period)
        return np.dot(normalized_exp_weights, x[K:K - nb_period:-1])

    @classmethod
    def moving_average_conv_div(cls, x, K):
        ema_1 = cls.exp_moving_average(x, K, cls.EMA_1_RANGE)
        ema_2 = cls.exp_moving_average(x, K, cls.EMA_2_RANGE)
        return ema_1 - ema_2

    @classmethod
    def moving_average_conv_div_ema(cls, x, K):
        nb_period = cls.MACD_EMA_RANGE
        macd_list = [None] + [cls.moving_average_conv_div(x, K + k - nb_period + 1) for k in range(0, nb_period)]
        return cls.exp_moving_average(macd_list, nb_period, nb_period)

    @classmethod
    def macd_difference(cls, x, K):
        macd = cls.moving_average_conv_div(x, K)
        signal = cls.moving_average_conv_div_ema(x, K)
        return macd - signal

    @classmethod
    def rsi(cls, x, begin, end):
        increases = 0.
        decreases = 0.
        for k in range(begin + 1, end):
            diff = x[k] - x[k - 1]
            if diff > 0:
                increases += diff
            else:
                decreases -= diff
        return 0. if increases == 0 and decreases == 0 else increases / (increases + decreases)

    @classmethod
    def stoch_rsi(cls, x, begin, end):
        rsi_on_range = [cls.rsi(x, begin, end - i) for i in reversed(range(0, cls.STOCH_RSI_RANGE))]
        if not rsi_on_range:
            logging.error('Not enough points')
            return None
        current_rsi = rsi_on_range[-1]
        min_rsi = min(rsi_on_range)
        max_rsi = max(rsi_on_range)
        if min_rsi == max_rsi:
            logging.error('Not enough points: min and max are equal')
            return None
        return (current_rsi - min_rsi) / (max_rsi - min_rsi)

    @classmethod
    def mfi(cls, x, volumes, begin, end):
        increases = 0.
        decreases = 0.
        for k in range(begin + 1, end):
            diff = x[k] * volumes[k] - x[k - 1] * volumes[k - 1]
            if diff > 0:
                increases += diff
            else:
                decreases -= diff
        return 0. if increases == 0 and decreases == 0 else increases / (increases + decreases)

    @classmethod
    def log_returns(cls, x):
        result = [0.]
        previous_price = None
        for price in x:
            if previous_price:
                result.append(math.log(price / previous_price))
            previous_price = price
        return result
    
    @classmethod
    def standard_deviation(cls, x, K, nb_period):
        sma = cls.simple_moving_average(x, K, nb_period)
        return math.sqrt(sum((price - sma) ** 2 for price in x[K : K - nb_period : -1]) / nb_period)
