import json
import logging
from io import StringIO
from time import sleep
from typing import Dict, Optional

import requests
from pandas import DataFrame
from requests.exceptions import Timeout

# APIにリクエストを投げる間隔（sec）
REQUEST_INTERVAL = 2
# APIに繋がらないときのタイムアウト
REQUEST_TIMEOUT = 5.0
# APIにリクエストしてタイムアウトしたときのリトライ数
RETRY_COUNT = 3


class YahooFinanceAPIConfigure:
    """YahooFinanceAPIへの設定"""

    _URL = "https://query1.finance.yahoo.com/v7/finance/chart/{stock_code}?range={range}&interval={interval}&indicators=quote&includeTimestamps=true"

    _RANGE = {
        "1day": "1d",
        "5days": "5d",
        "1month": "1mo",
        "3months": "3mo",
        "6months": "6mo",
        "1year": "1y",
        "2years": "2y",
        "5years": "5y",
        "10years": "10y",
        "ytd": "ytd",
        "max": "max",
    }

    _INTERVAL = {"1day": "1d"}

    def __init__(self, date_range: str, interval: str) -> None:
        self._date_range = self._RANGE[date_range]
        self._interval = self._INTERVAL[interval]

    def generate_url(self, stock_code):
        return self._URL.format(
            stock_code=stock_code, range=self._date_range, interval=self._interval
        )


_yahoo_finance_api_configure = YahooFinanceAPIConfigure("6months", "1day")


def get_stockinfo(stock_code: str) -> Optional[DataFrame]:
    """APIから情報取得する"""
    url = _yahoo_finance_api_configure.generate_url(stock_code)
    logging.debug("url:%s", url)
    text = {}
    for _ in range(RETRY_COUNT):
        try:
            res = requests.get(url, timeout=REQUEST_TIMEOUT)
            text = json.load(StringIO(res.text))
        except Timeout:
            sleep(REQUEST_INTERVAL)
            continue
        except Exception:
            continue
        break
    else:
        logging.warn("timeout occurred. code is %s", stock_code)
        return None
    if text["chart"]["error"] is not None:
        logging.warn("api return error. code is %s", stock_code)
        logging.warn("api error %s", text["chart"]["error"])
        return None
    sleep(REQUEST_INTERVAL)
    try:
        return _parse_json_to_dataframe(text)
    except TypeError as e:
        logging.warn("unexpected format data returned.")
        logging.warn(e)
        return None


def _parse_json_to_dataframe(json_data: Dict) -> DataFrame:
    try:
        d = json_data["chart"]["result"][0]
        df = DataFrame()
        df["timestamp"] = d["timestamp"]
        df["open"] = d["indicators"]["quote"][0]["open"]
        df["low"] = d["indicators"]["quote"][0]["low"]
        df["high"] = d["indicators"]["quote"][0]["high"]
        df["close"] = d["indicators"]["quote"][0]["close"]
        df["volume"] = d["indicators"]["quote"][0]["volume"]
    except TypeError as e:
        logging.warn("failed to parse json")
        raise e
    return df
