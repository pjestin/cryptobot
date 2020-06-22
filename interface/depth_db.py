import os
import json
import logging
from datetime import date

from model import Depth


class DepthDb:

    def __init__(self, currency_pair, limit, file_date):
        self.currency_pair = currency_pair
        self.limit = limit
        self.file_date = file_date
        self.file_path = 'data/depth/binance_depth_{}_{}_{}.json'.format(currency_pair.upper(), limit, file_date.isoformat())

    def read(self):
        with open(self.file_path, mode='r') as file:
            return (Depth.from_db_json(json.loads(line)) for line in file.readlines())

    def extend(self, depth):
        logging.debug('Adding depth data to file {}'.format(self.file_path))
        with open(self.file_path, mode='a') as file:
            file.write('{}\n'.format(json.dumps(depth.to_json())))
        logging.debug('Depth file written')

