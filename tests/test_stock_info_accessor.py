import unittest

from app.stock_info_accessor import YahooFinanceAPIConfigure as Configure
from app.stock_info_accessor import get_stockinfo


class TestYahooFinanceAPIConfigure(unittest.TestCase):
    def test_init(self):
        # test set range
        param_and_excepted = [
            # param(range, interval) expected(_data_range, _interval)
            (("1day", "1day"), ("1d", "1d")),
            (("5days", "1day"), ("5d", "1d")),
            (("1month", "1day"), ("1mo", "1d")),
            (("3months", "1day"), ("3mo", "1d")),
            (("6months", "1day"), ("6mo", "1d")),
            (("1year", "1day"), ("1y", "1d")),
            (("2years", "1day"), ("2y", "1d")),
            (("5years", "1day"), ("5y", "1d")),
            (("10years", "1day"), ("10y", "1d")),
            (("ytd", "1day"), ("ytd", "1d")),
            (("max", "1day"), ("max", "1d")),
        ]
        for param, expected in param_and_excepted:
            r, i = param
            date_range, interval = expected
            configure = Configure(r, i)
            self.assertEqual(configure._date_range, date_range)
            self.assertEqual(configure._interval, interval)

        with self.assertRaises(KeyError):
            configure = Configure("1day", "dummy")
        with self.assertRaises(KeyError):
            configure = Configure("dummy", "1day")

    def test_generate_url(self):
        configure = Configure("6months", "1day")
        actual_url = configure.generate_url("1234.T")
        expected = "https://query1.finance.yahoo.com/v7/finance/chart/1234.T?range=6mo&interval=1d&indicators=quote&includeTimestamps=true"
        self.assertEqual(
            actual_url,
            expected,
        )


class TestGetStockinfo(unittest.TestCase):
    def test_get_stockinfo(self):
        pass
