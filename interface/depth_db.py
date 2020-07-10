import os
import json
import logging
from datetime import date
import sqlite3

from model import Depth


class DepthDb:

    def __init__(self, currency_pair, limit):
        self.currency_pair = currency_pair
        self.limit = limit
        self.file_path = 'data/depth/binance_depth_{}_{}.db'.format(currency_pair.upper(), limit)

    def read(self):
        with sqlite3.connect(self.file_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as conn:
            cur = conn.cursor()
            for depth_row in cur.execute("SELECT time, bids, asks FROM depths"):
                yield Depth(depth_row[0],
                    json.loads(depth_row[1]), json.loads(depth_row[2]))
    
    def data_count(self):
        with sqlite3.connect(self.file_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as conn:
            cur = conn.cursor()
            return cur.execute('SELECT COUNT(*) FROM depths').fetchone()[0]

    def extend(self, depth):
        logging.debug('Adding depth data to file {}'.format(self.file_path))
        with sqlite3.connect(self.file_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as conn:
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS depths (
                time TIMESTAMP,
                bids JSON,
                asks JSON
            )''')
            cur.execute(
                'INSERT INTO depths (time, bids, asks) VALUES (?, ?, ?)',
                (depth.time, json.dumps(depth.bids), json.dumps(depth.asks))
            )
        logging.debug('Depth file written')

