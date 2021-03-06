from datetime import datetime


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
