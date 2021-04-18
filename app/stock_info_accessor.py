from app.valid_stock_code import write_json
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


URL = "https://query1.finance.yahoo.com/v7/finance/chart/{stock_code}?range={range}&interval={interval}&indicators=quote&includeTimestamps=true"


def get_stockinfo(stock_code):
    res = requests.get(URL.format(stock_code=stock_code, range="30d", interval="1d"))
    text = json.load(StringIO(res.text))
    if text["chart"]["error"] is not None:
        print(text["chart"]["error"])
        return None
    return text


def parse_json_to_dataframe(json_data) -> DataFrame:
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
        raise RuntimeError("Failed to parse json") from e
    return df


def read_valid_codes(prefix: str) -> List[str]:
    with open("/out/" + prefix + "codes.txt") as f:
        return [x.strip() for x in f.readlines()]


def plot_price(file_name: str, df: DataFrame):
    fig, axes = pyplot.subplots()
    axes.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    df.plot(ax=axes, x="timestamp", sharex=True)
    pyplot.savefig(f"img/{file_name}.png")
    pyplot.close("all")


if __name__ == "__main__":
    prefix = datetime.strftime(datetime.now(), "%Y%m%d")
    stock_codes = read_valid_codes(prefix)
    for code in stock_codes:
        sleep(8)
        stock_info = get_stockinfo(code)
        if stock_info is None:
            continue
        write_json(code, prefix, stock_info)
