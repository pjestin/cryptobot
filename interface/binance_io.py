import json
import logging
import time

from binance.client import Client
from model import Kline, Trade


class BinanceInterface():

    TIMEOUT = 20
    BINANCE_KEY_FILE = '.binance'

    def __init__(self, client=None):
        if client:
            self.client = client
        else:
            with open(self.BINANCE_KEY_FILE, newline='\n') as file:
                api_key = next(file).rstrip('\n')
                secret_key = next(file).rstrip('\n')
            self.client = Client(api_key, secret_key)

    def get_history(self, limit, currency_pair):
        trades = self.client.get_recent_trades(
            symbol=currency_pair, limit=limit)
        t = [int(trade['time']) for trade in trades]
        x = [float(trade['price']) for trade in trades]
        return t, x

    def get_klines(self, limit, interval, currency_pair, start_time=None, end_time=None):
        klines = None
        try:
            klines = self.client.get_klines(
                symbol=currency_pair,
                interval=interval,
                limit=limit,
                startTime=start_time,
                endTime=end_time
            )
        except Exception as e:
            logging.error('Error retrieving klines: {}'.format(e))
        if not klines:
            logging.error('Kline data invalid')
            return None
        return [Kline(kline_data) for kline_data in klines]

    def dump_historical_klines(self, interval, currency_pair, start_time, end_time):
        klines = list(self.client.get_historical_klines_generator(
            symbol=currency_pair,
            interval=interval,
            start_str=start_time,
            end_str=end_time
        ))
        logging.info('Number of klines: {}'.format(len(klines)))
        first_time = klines[0][0]
        file_name = 'data/binance_klines_{}_{}_{}.json'.format(
            currency_pair, interval, first_time)
        with open(file_name, mode='w') as file:
            json.dump(klines, file)

    def last_price(self, currency_pair):
        try:
            ticker = self.client.get_ticker(symbol=currency_pair)
        except:
            logging.error('Error retrieving last price')
        if not ticker or 'lastPrice' not in ticker:
            logging.error('Price data invalid')
            return None
        return float(ticker['lastPrice'])

    def create_order(self, is_buy, quantity, currency_pair):
        order = self.client.create_order(
            symbol=currency_pair,
            side=Client.SIDE_BUY if is_buy else Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,
        )
        logging.info('Order: {}'.format(order))
        if not order or 'orderId' not in order:
            raise ValueError('No order ID in returned order')
        order_id = order['orderId']
        for _ in range(0, self.TIMEOUT):
            if not order or 'status' not in order or order['status'] != Client.ORDER_STATUS_FILLED:
                logging.info('Awaiting order filling...')
                time.sleep(1)
                order = self.client.get_order(
                    symbol=currency_pair,
                    orderId=order_id
                )
                logging.info('Waiting on order: {}'.format(order))
        return order

    def server_time_diff(self):
        for _ in range(1, 10):
            local_time1 = int(time.time() * 1000)
            server_time = self.client.get_server_time()
            diff1 = server_time['serverTime'] - local_time1
            local_time2 = int(time.time() * 1000)
            diff2 = local_time2 - server_time['serverTime']
            print("local1: %s server:%s local2: %s diff1:%s diff2:%s" % (
                local_time1, server_time['serverTime'], local_time2, diff1, diff2))
            time.sleep(2)

    def my_trade_history(self, currency_pair):
        trade_data = self.client.get_my_trades(symbol=currency_pair)
        trades = [Trade(trade) for trade in trade_data]
        merged_trades = []
        previous_trade_time = None
        previous_trade_is_buy = None
        for trade in trades:
            if previous_trade_time and abs(trade.time - previous_trade_time) < 60. \
                    and trade.is_buy == previous_trade_is_buy:
                merged_trades[-1].quantity += trade.quantity
            else:
                merged_trades.append(trade)
            previous_trade_time = trade.time
            previous_trade_is_buy = trade.is_buy
        return merged_trades

    def last_trade(self, currency_pair):
        return self.my_trade_history(currency_pair)[-1]
