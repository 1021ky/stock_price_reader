import json
from datetime import datetime, timedelta, timezone
from io import StringIO
from time import CLOCK_THREAD_CPUTIME_ID, sleep
from typing import List, Optional, Tuple
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pandas.core.series import Series

import requests
import talib
from matplotlib import pyplot
from pandas import DataFrame
import pandas
from matplotlib import dates as mdates


def get_valid_stock_code():
    with open("codes.txt") as f:
        return f.readlines()


URL = "https://query1.finance.yahoo.com/v7/finance/chart/{stock_code}?range={range}&interval={interval}&indicators=quote&includeTimestamps=true"


def get_stockinfo(stock_code):
    res = requests.get(URL.format(stock_code=stock_code, range="30d", interval="1d"))
    text = json.load(StringIO(res.text))
    if text["chart"]["error"] is not None:
        print(text["chart"]["error"])
        return None
    return text


def parse_json_to_dataframe(json_data) -> DataFrame:
    df = DataFrame()
    df["timestamp"] = json_data["chart"]["result"][0]["timestamp"]
    df["open"] = json_data["chart"]["result"][0]["indicators"]["quote"][0]["open"]
    df["low"] = json_data["chart"]["result"][0]["indicators"]["quote"][0]["low"]
    df["high"] = json_data["chart"]["result"][0]["indicators"]["quote"][0]["high"]
    df["close"] = json_data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    df["volume"] = json_data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
    return df


def read_valid_codes() -> List[str]:
    with open("valid_stock_code.txt") as f:
        return f.readlines()


def calc_short_term_SMA(df: DataFrame) -> Series:
    return talib.SMA(df["close"], 5)


def calc_long_term_SMA(df: DataFrame) -> Series:
    return talib.SMA(df["close"], 25)


def is_down(sma):
    # 下降傾向かみる
    pass


def calc_gradients(df: DataFrame) -> List:
    # 傾きを調べる
    d = df.diff()
    print(f"calc_gradient:{d.values[-1]}")
    try:
        return d.values
    except ValueError as e:
        raise e


def get_cross_day(short: Series, long: Series) -> Optional[int]:
    # 交わる日があれば何日前にあったか返す
    diff = short - long
    for i in range(1, len(long.values) - 1):
        if diff.values[-i] >= 0 and diff.values[-i - 1] < 0:
            return i
    return None


def get_time_of_purchase_codes(codes):
    # 買い時の銘柄コードを返す
    time_of_purchase_codes = []
    for code in codes:
        res = get_stockinfo(code)
        if res is None:
            continue
        data = parse_json_to_dataframe(res)
        short_sma = calc_short_term_SMA(data)
        long_sma = calc_long_term_SMA(data)
        short_gradients = calc_gradients(short_sma)
        print(short_gradients)
        long_gradients = calc_gradients(long_sma)
        print(long_gradients)
        # 短期的には上昇していないのならばパス
        if short_gradients[-1] <= 0:
            print("pass 1")
            continue
        # 長期的にも一定期間(5日間)安定していなければパス
        if len([x for x in long_gradients[-5:] if x > -2 and x < 3]) < 5:
            print("pass 2")
            print([x for x in long_gradients[-5:] if x > -2 and x < 3])
            continue
        if short_gradients[-1] <= long_gradients[-1]:
            print("pass 3")
            continue
        passed_days = get_cross_day(short_sma, long_sma)
        if passed_days is None:
            print("pass 4")
            continue
        # 2日以上前だったらパス。遅い。
        if passed_days > 1:
            print("pass 5")
            continue
        time_of_purchase_codes.append(code)
    return time_of_purchase_codes


def plot_price(file_name: str, df: DataFrame):
    fig, axes = pyplot.subplots()
    axes.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    df.plot(ax=axes, x="timestamp", sharex=True)
    pyplot.savefig(f"img/{file_name}.png")
    pyplot.close("all")


if __name__ == "__main__":
    # stock_codes = get_valid_stock_code()
    # codes = get_time_of_purchase_codes(stock_codes)
    stock_codes = ["1301.T"]
    for code in stock_codes:
        stock_info = get_stockinfo(code)
        data = parse_json_to_dataframe(stock_info)
        data["timestamp"] = pandas.to_datetime(data["timestamp"], unit="s")
        data["5sma"] = calc_short_term_SMA(data)
        data["25sma"] = calc_long_term_SMA(data)
        data["volume"] = None
        plot_price(code, data)

    codes = get_time_of_purchase_codes(["1301.T"])
    print(codes)
