import json
from datetime import datetime, timedelta, timezone
from io import StringIO
import os
from time import CLOCK_THREAD_CPUTIME_ID, sleep
from typing import List, Optional, Tuple, Dict
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pandas.core.series import Series

import requests
from requests.exceptions import Timeout
import talib
from matplotlib import pyplot
from pandas import DataFrame
import pandas
from matplotlib import dates as mdates
from time import sleep


def get_valid_stock_code():
    with open("codes.txt") as f:
        return f.readlines()


URL = "https://query1.finance.yahoo.com/v7/finance/chart/{stock_code}?range={range}&interval={interval}&indicators=quote&includeTimestamps=true"

# APIにリクエストを投げる間隔（sec）
REQUEST_INTARVAL = 2
# APIに繋がらない
REQUEST_TIMEOUT = 5.0
# APIにリクエストしてタイムアウトしたときのリトライ数
RETRY_COUNT = 3

# 保存先
work_dir = os.getcwd()
LOG_DIR = f"{work_dir}/log/"
STOCK_CODE_DIR = f"{work_dir}/out/code/"
JSON_CODE_DIR = f"{work_dir}/out/json/"


def get_stockinfo(stock_code: str, selected_range: int) -> Optional[Dict]:
    """APIから情報取得する"""
    param = URL.format(
        stock_code=stock_code, range=str(selected_range) + "d", interval="1d"
    )
    text = {}
    for _ in range(RETRY_COUNT):
        try:
            res = requests.get(param, timeout=REQUEST_TIMEOUT)
            text = json.load(StringIO(res.text))
        except Timeout:
            sleep(REQUEST_INTARVAL)
            continue
        except Exception:
            continue
        break
    else:
        print(f"timeout occured. code:{stock_code}")
        return None
    if text["chart"]["error"] is not None:
        print(stock_code + ": ", end="")
        print(text["chart"]["error"])
        return None
    sleep(REQUEST_INTARVAL)
    return text


def parse_json_to_dataframe(json_data) -> DataFrame:
    try:
        df = DataFrame()
        df["timestamp"] = json_data["chart"]["result"][0]["timestamp"]
        df["open"] = json_data["chart"]["result"][0]["indicators"]["quote"][0]["open"]
        df["low"] = json_data["chart"]["result"][0]["indicators"]["quote"][0]["low"]
        df["high"] = json_data["chart"]["result"][0]["indicators"]["quote"][0]["high"]
        df["close"] = json_data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        df["volume"] = json_data["chart"]["result"][0]["indicators"]["quote"][0][
            "volume"
        ]
    except TypeError as e:
        raise RuntimeError("Failed to parse json") from e
    return df


def read_valid_codes() -> List[str]:
    with open("codes.txt") as f:
        return [x.strip() for x in f.readlines()]


def calc_daily_short_term_SMA(df: DataFrame) -> Series:
    return talib.SMA(df["close"], 5)


def calc_daily_long_term_SMA(df: DataFrame) -> Series:
    return talib.SMA(df["close"], 25)


# TODO 週足・月足でみるにはAPIから値の取り方をかえないと無理
def calc_weekly_short_term_SMA(df: DataFrame) -> Series:
    return talib.SMA(df["close"], 30 * 3)


def calc_weekly_long_term_SMA(df: DataFrame) -> Series:
    return talib.SMA(df["close"], 30 * 6)


def calc_monthly_long_term_SMA(df: DataFrame) -> Series:
    return talib.SMA(df["close"], 30 * 5)


def calc_monthly_short_term_SMA(df: DataFrame) -> Series:
    return talib.SMA(df["close"], 30 * 25)


def is_down(sma):
    # 下降傾向かみる
    pass


def calc_gradients(df: Series) -> List:
    # 傾きを調べる
    d = df.diff()
    # print(f"calc_gradient:{d.values[-1]}")
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
        res = get_stockinfo(code, 30)
        if res is None:
            continue
        data = DataFrame()
        try:
            data = parse_json_to_dataframe(res)
        except Exception:
            continue
        short_sma = calc_daily_short_term_SMA(data)
        long_sma = calc_daily_long_term_SMA(data)
        short_gradients = calc_gradients(short_sma)
        print(short_gradients)
        long_gradients = calc_gradients(long_sma)
        print(long_gradients)
        # 短期的には上昇していないのならばパス
        if short_gradients[-1] <= 0:
            continue
        # 長期的にも一定期間(5日間)安定していなければパス
        if len([x for x in long_gradients[-5:] if x > -2 and x < 3]) < 5:
            continue
        # ゴールデンクロスがなければパス
        if short_gradients[-1] <= long_gradients[-1]:
            continue
        passed_days = get_cross_day(short_sma, long_sma)
        if passed_days is None:
            continue
        # 2日以上前だったらパス。遅い。
        if passed_days > 1:
            continue
        time_of_purchase_codes.append(code)
    return time_of_purchase_codes


def is_time_of_purchase(data) -> bool:
    latest_close = data["close"][0]
    short_sma = calc_daily_short_term_SMA(data)
    long_sma = calc_daily_long_term_SMA(data)
    short_gradients = calc_gradients(short_sma)
    print(short_gradients)
    long_gradients = calc_gradients(long_sma)
    print(long_gradients)
    # 短期的には上昇していないのならばパス
    if short_gradients[-1] <= 0:
        return False
    # 長期的にも一定期間(5日間)安定していなければパス
    if len([x for x in long_gradients[-5:] if x > -2 and x < 3]) < 5:
        return False
    if short_gradients[-1] <= long_gradients[-1]:
        return False
    # +3％以上の乖離率ならばパス
    rate = calc_divergence_rate(short_sma.values[-1], latest_close)
    print(
        f"rate:{rate} base(short_sma):{short_sma.values[-1]} compared(latest_close):{latest_close}"
    )
    # if rate >= 3:
    #     return False
    passed_days = get_cross_day(short_sma, long_sma)
    if passed_days is None:
        return False
    # 2日以上前だったらパス。遅い。
    if passed_days > 1:
        return False
    return True


def calc_divergence_rate(base: float, compared: float) -> float:
    return (compared - base) * 100 / base


def get_time_to_sell_codes(codes: List) -> List[str]:
    return []


def get_time_to_abandon_codes(codes: List) -> List[str]:
    return []


def plot_price(file_name: str, df: DataFrame):
    fig, axes = pyplot.subplots()
    axes.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    df.plot(ax=axes, x="timestamp", sharex=True)
    pyplot.savefig(f"out/img/{file_name}.png")
    pyplot.close("all")


if __name__ == "__main__":
    stock_codes = read_valid_codes()
    for code in stock_codes:
        try:
            stock_info = get_stockinfo(code, 30)
            data = parse_json_to_dataframe(stock_info)
        except Exception as e:
            print(e)
            continue
        if is_time_of_purchase(data):
            print(f"{code} is time to purchase!!")
        data["timestamp"] = pandas.to_datetime(data["timestamp"], unit="s")
        data["5sma"] = calc_daily_short_term_SMA(data)
        data["25sma"] = calc_daily_long_term_SMA(data)
        data["volume"] = None
        plot_price(code, data)
