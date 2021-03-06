import unittest
from unittest.mock import MagicMock, patch
import os
import json
from datetime import datetime

from interface.binance_io import BinanceInterface
from model import Kline
from interface import read_data


class BinanceInterfaceTest(unittest.TestCase):

    TEST_KLINE_DATA_FILE = "data/binance_klines_DOGEUSDT_2m_1509926400000.json"

    def setUp(self):
        if os.path.isfile(self.TEST_KLINE_DATA_FILE):
            os.remove(self.TEST_KLINE_DATA_FILE)

        self.mock_client = MagicMock()
        self.binance = BinanceInterface(self.mock_client)

        self.kline1 = [
            1509926400000,
            "1.50000000",
            "1.79900000",
            "0.50000000",
            "1.54580000",
            "15425.04000000",
            1509947999999,
            "23698.98992800",
            199,
            "2901.96000000",
            "4663.35341300",
            "102181628.99137327",
        ]
        self.kline2 = [
            1509948000000,
            "1.54580000",
            "1.68100000",
            "1.53870000",
            "1.62880000",
            "59449.05000000",
            1509969599999,
            "95921.08691000",
            338,
            "26110.78000000",
            "42788.24647100",
            "102286567.18669863",
        ]

    def tearDown(self):
        if os.path.isfile(self.TEST_KLINE_DATA_FILE):
            os.remove(self.TEST_KLINE_DATA_FILE)

    def test_recent_trades(self):
        self.mock_client.get_recent_trades.return_value = [
            {
                "time": 1564521434,
                "price": 105.23,
            },
            {
                "time": 1564555002,
                "price": 104.22,
            },
        ]
        t, x = self.binance.get_history(2, "BTCUSDT")
        self.assertEqual([1564521434, 1564555002], t)
        self.assertEqual([105.23, 104.22], x)
        self.mock_client.get_recent_trades.assert_called_once_with(
            symbol="BTCUSDT", limit=2
        )

    def test_klines(self):
        self.mock_client.get_klines.return_value = [self.kline1, self.kline2]
        kline_objects = [Kline(self.kline1), Kline(self.kline2)]
        klines = self.binance.get_klines(
            limit=2,
            interval="5m",
            symbol="BNBBTC",
            start_time="2 years ago",
            end_time="now",
        )
        self.assertEqual(kline_objects, klines)
        self.mock_client.get_klines.assert_called_once_with(
            symbol="BNBBTC",
            interval="5m",
            limit=2,
            startTime="2 years ago",
            endTime="now",
        )

    def test_klines_error(self):
        self.mock_client.get_klines.side_effect = ValueError("Not found")
        self.binance.get_klines(
            limit=2,
            interval="5m",
            symbol="BNBBTC",
            start_time="2 years ago",
            end_time="now",
        )

    def test_dump_historical_klines(self):
        self.mock_client.get_historical_klines_generator.return_value = [
            self.kline1,
            self.kline2,
        ]
        self.binance.dump_historical_klines(
            interval="2m",
            symbol="DOGEUSDT",
            start_time="2 years ago",
            end_time="now",
        )
        kline_data = read_data.read_klines_from_json(self.TEST_KLINE_DATA_FILE)
        self.assertEqual([Kline(self.kline1), Kline(self.kline2)], kline_data)

    def test_last_price(self):
        self.mock_client.get_ticker.return_value = {"lastPrice": 95.62}
        last_price = self.binance.last_price("BTCUSDT")
        self.assertEqual(95.62, last_price)
        self.mock_client.get_ticker.assert_called_once_with(symbol="BTCUSDT")

    def test_create_order_immediate(self):
        mock_order = {"orderId": 153118, "status": "FILLED"}
        self.mock_client.create_order.return_value = mock_order
        order = self.binance.create_order(is_buy=True, quantity=2.5, symbol="BTCUSDT")
        self.assertEqual(mock_order, order)
        self.mock_client.create_order.assert_called_once_with(
            symbol="BTCUSDT",
            side="BUY",
            type="MARKET",
            quantity=2.5,
        )

    def test_create_order_delay(self):
        mock_order_pending = {"orderId": 153118, "status": "PENDING"}
        mock_order_filled = {"orderId": 153118, "status": "FILLED"}
        self.mock_client.create_order.return_value = mock_order_pending
        self.mock_client.get_order.side_effect = [mock_order_pending, mock_order_filled]
        order = self.binance.create_order(is_buy=False, quantity=2.5, symbol="BTCUSDT")
        self.assertEqual(mock_order_filled, order)
        self.mock_client.create_order.assert_called_with(
            symbol="BTCUSDT",
            side="SELL",
            type="MARKET",
            quantity=2.5,
        )
        self.mock_client.get_order.assert_called_with(symbol="BTCUSDT", orderId=153118)

    def test_create_order_failure(self):
        mock_order_failure = {"status": "FAIL"}
        self.mock_client.create_order.return_value = mock_order_failure
        with self.assertRaises(ValueError) as cm:
            self.binance.create_order(is_buy=True, quantity=2.5, symbol="BTCUSDT")
        self.assertEqual("No order ID in returned order", str(cm.exception))

    def test_my_trade_history(self):
        mock_trade1 = {
            "id": 28457,
            "price": "4.00000100",
            "qty": "12.00000000",
            "time": 1499865549000,
            "isBuyer": True,
        }
        mock_trade2 = {
            "id": 28458,
            "price": "4.01000000",
            "qty": "3.00000000",
            "time": 1499865569000,
            "isBuyer": True,
        }
        mock_trade3 = {
            "id": 28459,
            "price": "4.01000000",
            "qty": "3.00000000",
            "time": 1499865570000,
            "isBuyer": False,
        }
        mock_trade4 = {
            "id": 28460,
            "price": "4.00000000",
            "qty": "32.00000000",
            "time": 1499865870000,
            "isBuyer": False,
        }
        mock_trade5 = {
            "id": 28461,
            "price": "3.99000000",
            "qty": "1.50000000",
            "time": 1499865890000,
            "isBuyer": False,
        }

        self.mock_client.get_my_trades.return_value = [
            mock_trade1,
            mock_trade2,
            mock_trade3,
            mock_trade4,
            mock_trade5,
        ]
        trades = self.binance.my_trade_history(symbol="BTCUSDT")
        self.mock_client.get_my_trades.assert_called_with(symbol="BTCUSDT")
        self.assertEqual(3, len(trades))

        self.assertEqual(float(mock_trade1["price"]), trades[0].price)
        self.assertTrue(trades[0].is_buy)
        self.assertEqual(mock_trade1["time"] / 1000.0, trades[0].time)
        self.assertEqual(
            float(mock_trade1["qty"]) + float(mock_trade2["qty"]), trades[0].quantity
        )

        self.assertEqual(float(mock_trade3["price"]), trades[1].price)
        self.assertFalse(trades[1].is_buy)
        self.assertEqual(mock_trade3["time"] / 1000.0, trades[1].time)
        self.assertEqual(float(mock_trade3["qty"]), trades[1].quantity)

        self.assertEqual(float(mock_trade4["price"]), trades[2].price)
        self.assertFalse(trades[2].is_buy)
        self.assertEqual(mock_trade4["time"] / 1000.0, trades[2].time)
        self.assertEqual(
            float(mock_trade4["qty"]) + float(mock_trade5["qty"]), trades[2].quantity
        )

    def test_last_trade(self):
        mock_trade = {
            "id": 28457,
            "price": "4.00000100",
            "qty": "12.00000000",
            "commission": "10.10000000",
            "commissionAsset": "BNB",
            "time": 1499865549590,
            "isBuyer": True,
            "isMaker": False,
            "isBestMatch": True,
        }
        self.mock_client.get_my_trades.return_value = [mock_trade]
        last_trade = self.binance.last_trade(symbol="BTCUSDT")
        self.mock_client.get_my_trades.assert_called_with(symbol="BTCUSDT")
        self.assertEqual(float(mock_trade["price"]), last_trade.price)
        self.assertEqual(mock_trade["isBuyer"], last_trade.is_buy)
        self.assertEqual(mock_trade["time"] / 1000.0, last_trade.time)
