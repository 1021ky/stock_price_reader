import json
import logging
from io import StringIO
from time import sleep
from typing import Dict, Optional

import requests
from pandas import DataFrame
from requests.exceptions import Timeout


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


class YahooFinanceAPIClient:
    # APIにリクエストを投げる間隔（sec）
    _REQUEST_INTERVAL = 2
    # APIに繋がらないときのタイムアウト
    _REQUEST_TIMEOUT = 5.0
    # APIにリクエストしてタイムアウトしたときのリトライ数
    _RETRY_COUNT = 3

    def __init__(self) -> None:
        self._configure = YahooFinanceAPIConfigure("6months", "1day")

    def get_stockinfo(self, stock_code: str) -> Optional[DataFrame]:
        """APIから銘柄情報を取得する"""
        url = self._configure.generate_url(stock_code)
        logging.info("url:%s", url)
        response = self._request(url)
        logging.debug("response:%s", response)
        parsed = self._parse_response(response)
        logging.debug("parsed response:%s", parsed)
        return parsed

    def _request(self, url: str) -> Optional[Dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }

        for _ in range(self._RETRY_COUNT):
            try:
                res = requests.get(url, timeout=self._REQUEST_TIMEOUT, headers=headers)
                sleep(self._REQUEST_INTERVAL)
                if res.status_code == requests.codes.ok:
                    jsondata = res.json()
                    return jsondata
            except Timeout as e:
                logging.debug(e)
                sleep(self._REQUEST_INTERVAL)
                continue
            except Exception as e:
                logging.debug(e)
                continue
        else:
            logging.warn("timeout occurred. url is %s", url)
            return None

    def _parse_response(self, response: Optional[Dict]) -> Optional[DataFrame]:
        if response is None:
            return None
        if response["chart"]["error"] is not None:
            logging.warn("api error %s", response["chart"]["error"])
            return None
        try:
            return self._parse_json_to_dataframe(response)
        except TypeError as e:
            logging.warn("unexpected format data returned.")
            logging.warn(e)
            return None

    def _parse_json_to_dataframe(self, json_data: Dict) -> DataFrame:
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
