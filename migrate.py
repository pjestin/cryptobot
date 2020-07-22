import json
from datetime import datetime, date

from model import Depth
from interface.depth_db import DepthDb

LIMITS = [100, 1000]
CURRENCY_PAIR = 'BNBUSDT'
FILE_DATE = date(2020, 6, 19)


def main():
    for limit in LIMITS:
        depth_db = DepthDb(CURRENCY_PAIR, limit)
        file_path = 'data/depth/binance_depth_{}_{}_{}.json'.format(CURRENCY_PAIR.upper(), limit, FILE_DATE.isoformat())
        with open(file_path, mode='r') as file:
            for line in file.readlines():
                json_line = json.loads(line)
                depth = Depth(datetime.fromisoformat(json_line['time']), json_line['bids'], json_line['asks'])
                depth_db.extend(depth)


if __name__ == '__main__':
    main()
