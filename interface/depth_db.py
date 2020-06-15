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
            depth_data = [Depth.from_db_json(depth_data_as_json) for depth_data_as_json in json.load(file)]
        logging.debug('Depth data size: {}'.format(len(depth_data)))
        return sorted(depth_data, key=lambda depth: depth.time)

    def extend(self, depth):
        logging.debug('Adding depth data to file {}'.format(self.file_path))

        if not os.path.isfile(self.file_path):
            with open(self.file_path, mode='a') as file:
                json.dump([], file)

        with open(self.file_path, mode='r') as file:
            depth_data = json.load(file)
        depth_data.append(depth.to_json())
        with open(self.file_path, mode='w') as file:
            json.dump(depth_data, file)
