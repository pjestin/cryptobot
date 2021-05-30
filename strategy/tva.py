import logging

from tradingview_ta import TA_Handler

from model import TradeAction

SCREENER = "crypto"
EXCHANGE = "binance"
CLOSE = "close"
RECOMMENDATION = "RECOMMENDATION"
TAKE_PROFIT = 0.003
STOP_LOSS = -0.01


class TradingViewAnalysisStrategy:
    def __init__(self, symbol: str, interval: str):
        self.handler = TA_Handler(
            symbol=symbol,
            screener=SCREENER,
            exchange=EXCHANGE,
            interval=interval,
        )

    def decide_action(self, acquired: float, previous_price: float):
        analysis = self.handler.get_analysis()
        recommendation = analysis.summary[RECOMMENDATION]
        price = analysis.indicators[CLOSE]
        logging.info("Recommendation from Trading View: {}".format(recommendation))
        if acquired:
            if recommendation == "STRONG_SELL":
                return TradeAction("sell")
            potential_profit = price / previous_price - 1.0
            if recommendation == "SELL" and (
                potential_profit > TAKE_PROFIT or potential_profit < STOP_LOSS
            ):
                return TradeAction("sell")
            return TradeAction(None)
        else:
            if recommendation in ["STRONG_BUY", "BUY"]:
                return TradeAction("buy")
            return TradeAction(None)
