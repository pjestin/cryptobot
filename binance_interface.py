import json
import logging
import time

from binance.client import Client
from model import Kline

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
        trades = self.client.get_recent_trades(symbol=currency_pair, limit=limit)
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
        except:
            logging.error('Error retrieving klines')
        if not klines:
            logging.error('Kline data invalid')
            return None
        return [Kline(kline_data) for kline_data in klines]

    def dump_historical_klines(self, interval, currency_pair, start_time, end_time):
        klines = []
        for kline in self.client.get_historical_klines_generator(
            symbol=currency_pair,
            interval=interval,
            start_str=start_time,
            end_str=end_time
        ):
            klines.append(kline)
        logging.debug('Number of klines: {}'.format(len(klines)))
        first_time = klines[0][0]
        file_name = 'data/binance_klines_{}_{}_{}.json'.format(currency_pair, interval, first_time)
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
        logging.debug(order)
        if not order or 'orderId' not in order:
            raise ValueError('No order ID in returned order')
        order_id = order['orderId']
        for _ in range(0, self.TIMEOUT): 
            if not order or 'status' not in order or order['status'] != Client.ORDER_STATUS_FILLED:
                logging.debug('Awaiting order filling...')
                time.sleep(1)
                order = self.client.get_order(
                    symbol=currency_pair,
                    orderId=order_id
                )
                logging.debug(order)
        return order

    def server_time_diff(self):
        for _ in range(1, 10):
            local_time1 = int(time.time() * 1000)
            server_time = self.client.get_server_time()
            diff1 = server_time['serverTime'] - local_time1
            local_time2 = int(time.time() * 1000)
            diff2 = local_time2 - server_time['serverTime']
            print("local1: %s server:%s local2: %s diff1:%s diff2:%s" % (local_time1, server_time['serverTime'], local_time2, diff1, diff2))
            time.sleep(2)


def main():
    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=log_format, level=logging.DEBUG)

    binance = BinanceInterface()

    # Dump klines
    binance.dump_historical_klines('5m', 'EOSUSDT', '2 years ago', 'now')

    # Create order
    # binance.create_order(is_buy=True, quantity=0.1, currency_pair='BNBETH')

    # Figure out time sync
    # binance.server_time_diff()


if __name__ == '__main__':
    main()
