import unittest

from strategy.indicators import Indicators

class IndicatorsTest(unittest.TestCase):

    def setUp(self):
        self.x = [1., 3., 2.5, 3.4, .4, 4.5, .9, 0.1, .4]

    def test_exp_weights(self):
        self.assertEqual([1.], Indicators.get_exp_weights(nb_period=1))
        self.assertEqual([0.7499999999999999, 0.25], Indicators.get_exp_weights(nb_period=2))
        self.assertEqual([0.5714285714285714, 0.2857142857142857, 0.14285714285714285], Indicators.get_exp_weights(nb_period=3))

    def test_exp_moving_average(self):
        self.assertEqual(.4, Indicators.exp_moving_average(self.x, K=8, nb_period=1))
        self.assertEqual(.325, Indicators.exp_moving_average(self.x, K=8, nb_period=2))
        self.assertEqual(.806985294117647, Indicators.exp_moving_average(self.x, K=8, nb_period=4))

    def test_rsi(self):
        self.assertEqual(0., Indicators.rsi(self.x, 0, 0))
        self.assertEqual(0., Indicators.rsi(self.x, 0, 1))
        self.assertEqual(.48026315789473684, Indicators.rsi(self.x, 0, 9))
        self.assertEqual(.4999999999999999, Indicators.rsi(self.x, 4, 9))

    def test_stoch_rsi(self):
        Indicators.STOCH_RSI_RANGE = 3
        self.assertEqual(None, Indicators.stoch_rsi(self.x, 0, 0))
        self.assertEqual(None, Indicators.stoch_rsi(self.x, 0, 1))
        self.assertEqual(0., Indicators.stoch_rsi(self.x, 0, 5))
        self.assertEqual(.20290607161390783, Indicators.stoch_rsi(self.x, 0, 7))
        self.assertEqual(.39258693609022444, Indicators.stoch_rsi(self.x, 0, 9))

    def test_mfi(self):
        volumes = [500., 200., 59., 550., 770., 1200., 1150., 100., .4]
        self.assertEqual(0., Indicators.mfi(self.x, volumes, 0, 0))
        self.assertEqual(0., Indicators.mfi(self.x, volumes, 0, 1))
        self.assertEqual(.4825582531454046, Indicators.mfi(self.x, volumes, 0, 9))
        self.assertEqual(.4853295513465703, Indicators.mfi(self.x, volumes, 4, 9))

    def test_log_returns(self):
        expected_returns = [
            0.,
            1.0986122886681098,
            -0.1823215567939546,
            0.30748469974796055,
            -2.1400661634962708,
            2.4203681286504293,
            -1.6094379124341003,
            -2.197224577336219,
            1.3862943611198906
        ]
        self.assertEqual(expected_returns, Indicators.log_returns(self.x))
