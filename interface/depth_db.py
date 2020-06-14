import os
import json
import re
import logging
from datetime import date

from model import Depth


class DepthDb:

    @classmethod
    def read(cls, currency_pair, limit):
        depth_data = []
        rootdir = "data/depth/"
        regex = re.compile('binance_depth_{}_{}_.*'.format(currency_pair.upper(), limit))
        files = [file_path for file_path in os.listdir(rootdir) if os.path.isfile(os.path.join(rootdir, file_path)) and regex.match(file_path)]
        for file_path in files:
            with open(os.path.join(rootdir, file_path), mode='r') as file:
                depth_data.extend(Depth.from_db_json(depth_data_as_json) for depth_data_as_json in json.load(file))
        logging.debug('Depth data size: {}'.format(len(depth_data)))
        return sorted(depth_data, key=lambda depth: depth.time)

    @classmethod
    def extend(cls, depth, currency_pair, limit):
        current_time = depth.time
        file_path = 'data/depth/binance_depth_{}_{}_{}.json'.format(
            currency_pair, limit, current_time.date().isoformat())
        logging.debug('Adding depth data to file {}'.format(file_path))

        if not os.path.isfile(file_path):
            with open(file_path, mode='a') as file:
                json.dump([], file)

        with open(file_path, mode='r') as file:
            depth_data = json.load(file)
        depth_data.append(depth.to_json())
        with open(file_path, mode='w') as file:
            json.dump(depth_data, file)
