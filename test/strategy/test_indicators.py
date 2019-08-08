import unittest

from strategy.indicators import Indicators

class IndicatorsTest(unittest.TestCase):

    def setUp(self):
        self.x = [-1., 0., 2.5, 3.4, .4, -4.5, -.9, 0., .4]

    def test_exp_weights(self):
        self.assertEqual([], Indicators.get_exp_weights(nb_period=0))
        self.assertEqual([1.], Indicators.get_exp_weights(nb_period=1))
        self.assertEqual([0.47751517520819986, 0.5224848247918001], Indicators.get_exp_weights(nb_period=2))
        self.assertEqual([0.30382285285436134, 0.33243515239519433, 0.3637419947504442], Indicators.get_exp_weights(nb_period=3))

    def test_exp_moving_average(self):
        self.assertEqual(0., Indicators.exp_moving_average(self.x, K=8, nb_period=0))
        self.assertEqual(.4, Indicators.exp_moving_average(self.x, K=8, nb_period=1))
        self.assertEqual(.20899392991672006, Indicators.exp_moving_average(self.x, K=8, nb_period=2))
        self.assertEqual(-1.0781106634350017, Indicators.exp_moving_average(self.x, K=8, nb_period=4))

    def test_rsi(self):
        self.assertEqual(0., Indicators.rsi(self.x, 0, 0))
        self.assertEqual(0., Indicators.rsi(self.x, 0, 1))
        self.assertEqual(.5406976744186046, Indicators.rsi(self.x, 0, 9))
        self.assertEqual(.5, Indicators.rsi(self.x, 4, 9))

    def test_stoch_rsi(self):
        Indicators.STOCH_RSI_RANGE = 3
        self.assertEqual(None, Indicators.stoch_rsi(self.x, 0, 0))
        self.assertEqual(None, Indicators.stoch_rsi(self.x, 0, 1))
        self.assertEqual(0., Indicators.stoch_rsi(self.x, 0, 5))
        self.assertEqual(.6139251583995519, Indicators.stoch_rsi(self.x, 0, 7))
        self.assertEqual(1., Indicators.stoch_rsi(self.x, 0, 9))

    def test_mfi(self):
        volumes = [500., 200., 59., 550., 770., 1200., 1150., 100., .4]
        self.assertEqual(0., Indicators.mfi(self.x, volumes, 0, 0))
        self.assertEqual(0., Indicators.mfi(self.x, volumes, 0, 1))
        self.assertEqual(0.5166274826863544, Indicators.mfi(self.x, volumes, 0, 9))
        self.assertEqual(0.4861435197188373, Indicators.mfi(self.x, volumes, 4, 9))