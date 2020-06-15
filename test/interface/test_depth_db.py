import unittest
from datetime import datetime
import os

from model import Depth
from interface.depth_db import DepthDb


class DepthDbTest(unittest.TestCase):

    def setUp(self):
        self.TEST_DB_FILE = 'data/depth/binance_depth_DOGEUSDT_500_2019-10-25.json'
        if os.path.isfile(self.TEST_DB_FILE):
            os.remove(self.TEST_DB_FILE)
        self.now = datetime(2019, 10, 25, 15, 2)
        self.depth = Depth.from_db_json({
            'time': self.now.isoformat(),
            'bids': [[10., 1.], [11., 3.]],
            'asks': [[9., 2.], [9.5, 1.]],
        })
        self.currency_pair = 'DOGEUSDT'
        self.limit = 500
        self.depth_db = DepthDb(self.currency_pair, self.limit, self.now.date())
    
    def tearDown(self):
        if os.path.isfile(self.TEST_DB_FILE):
            os.remove(self.TEST_DB_FILE)

    def test_extend(self):
        self.depth_db.extend(self.depth)
        self.assertTrue(os.path.isfile(self.TEST_DB_FILE))

    def test_read(self):
        self.depth_db.extend(self.depth)
        depth_data = self.depth_db.read()
        self.assertEqual(1, len(depth_data))
        self.assertEqual(self.depth.time, depth_data[0].time)
        self.assertEqual(self.depth.bids, depth_data[0].bids)
        self.assertEqual(self.depth.asks, depth_data[0].asks)
    
    def test_multiple_extends(self):
        self.depth_db.extend(self.depth)
        self.depth_db.extend(self.depth)
        depth_data = self.depth_db.read()
        self.assertEqual(2, len(depth_data))
