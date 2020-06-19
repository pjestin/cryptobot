from datetime import datetime

import numpy as np


class TradeAction:
    BUY_ACTION = 'buy'
    SELL_ACTION = 'sell'
    ACTIONS = [BUY_ACTION, SELL_ACTION, None]

    def __init__(self, action_type, quantity_factor=1.):
        if action_type not in self.ACTIONS:
            raise ValueError('Action type is not in {}'.format(self.ACTIONS))
        self.action_type = action_type
        self.quantity_factor = quantity_factor

    def is_buy(self):
        return self.action_type and self.action_type == self.BUY_ACTION

    def is_sell(self):
        return self.action_type and self.action_type == self.SELL_ACTION


class Kline:

    KLINE_LABELS = ['open_time', 'open_price', 'high_price', 'low_price',
                    'close_price', 'volume', 'close_time', 'quote_asset_volume', 'nb_trades']

    def __init__(self, kline_data):
        for k in range(len(self.KLINE_LABELS)):
            setattr(self, self.KLINE_LABELS[k], float(kline_data[k]) if isinstance(
                kline_data[k], str) else kline_data[k])

    def __eq__(self, other):
        if not isinstance(other, Kline):
            return False
        return self.__dict__ == other.__dict__

    def diff(self):
        return self.close_price - self.open_price


class Trade:

    def __init__(self, trade_data):
        self.id = trade_data['id']
        self.price = float(trade_data['price'])
        self.time = float(trade_data['time'] / 1000)
        self.is_buy = trade_data['isBuyer']
        self.quantity = float(trade_data['qty'])

    def __eq__(self, other):
        if not isinstance(other, Trade):
            return False
        return self.id == other.id

    def __repr__(self):
        return '<Trade id={} price={} time={} is_buy={} quantity={}>'.format(self.id, self.price, self.time, self.is_buy, self.quantity)


class Depth:

    class Unit:
        def __init__(self, price, quantity):
            self.price = price
            self.quantity = quantity
        
        def to_json(self):
            return [self.price, self.quantity]
        
        @classmethod
        def from_json(cls, unit_data):
            return cls(unit_data[0], unit_data[1])
        
        def __eq__(self, other):
            return self.price == other.price and self.quantity == other.quantity

    def __init__(self, depth_time, depth_bids, depth_asks):
        self.time = depth_time
        self.bids = depth_bids
        self.asks = depth_asks

    @classmethod
    def from_binance_json(cls, binance_json_data):
        depth_time = datetime.fromisoformat(binance_json_data['time'])
        depth_bids = [cls.Unit(float(price), float(quantity)) for price, quantity in binance_json_data['bids']]
        depth_asks = [cls.Unit(float(price), float(quantity)) for price, quantity in binance_json_data['asks']]
        return cls(depth_time, depth_bids, depth_asks)

    @classmethod
    def from_db_json(cls, db_json_data):
        depth_time = datetime.fromisoformat(db_json_data['time'])
        depth_bids = [cls.Unit.from_json(unit) for unit in db_json_data['bids']]
        depth_asks = [cls.Unit.from_json(unit) for unit in db_json_data['asks']]
        return cls(depth_time, depth_bids, depth_asks)

    def to_json(self):
        return {
            'time': self.time.isoformat(),
            'bids': [unit.to_json() for unit in self.bids],
            'asks': [unit.to_json() for unit in self.asks]
        }

    def bid_prices(self):
        return np.array([unit.price for unit in self.bids])

    def bid_quantities(self):
        return np.array([unit.quantity for unit in self.bids])

    def ask_prices(self):
        return np.array([unit.price for unit in self.asks])

    def ask_quantities(self):
        return np.array([unit.quantity for unit in self.asks])
