import csv
import json

from model import Kline


def read_from_csv(file_path, n=None):
    with open(file_path, newline='') as file:
        reader = csv.reader(file, delimiter=',', quotechar='|')
        t = []
        x = []
        k = 0
        for row in reader:
            timestamp, bitcoin_price, _ = row[:]
            t.append(int(timestamp))
            x.append(float(bitcoin_price))
            k += 1
            if n and k >= n:
                break
    return t, x


def read_prices_from_json(file_path):
    with open(file_path, newline='') as file:
        data = json.load(file)
        t = []
        x = []
        for transaction in data:
            if ('date' not in transaction and 'time' not in transaction) or 'price' not in transaction:
                continue
            t.append(int(transaction['date'] if 'date' in transaction else transaction['time']))
            x.append(float(transaction['price']))
        if 'date' in data[0]:
            t.reverse()
            x.reverse()
        return t, x


def read_klines_from_json(file_path):
    with open(file_path, newline='') as file:
        data = json.load(file)
        klines = []
        for kline_data in data:
            klines.append(Kline(kline_data))
        return klines
