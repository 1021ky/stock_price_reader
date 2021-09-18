from pandas.core.frame import DataFrame
from simulator import Portfolio, simulate, SellMarketOrder, BuyMarketOrderMoreThan
from datetime import datetime, date, timezone, timedelta
from collections import defaultdict
import pickle

from logging import getLogger, config


import json

with open("log_conf.json", "r") as f:
    log_conf = json.load(f)
    config.dictConfig(log_conf)

logger = getLogger("app")


def generate_cross_date_list(stock: DataFrame):
    """指定した日足データよりゴールデンクロス・デッドクロスが生じた日のリストを生成"""
    # 移動平均を求める
    sma_5 = stock.rolling(window=5, on="timestamp").mean()
    sma_25 = stock.rolling(window=25, on="timestamp").mean()

    sma_65 = stock.rolling(window=65, on="timestamp").mean()
    sma_130 = stock.rolling(window=130, on="timestamp").mean()

    # ゴールデンクロス・デッドクロスが発生した場所を得る
    golden_cross = sma_5[
        (sma_5["close"] * 0.9 >= sma_25["close"])  # TODO これほんとにゴールデンクロスのとこだけとれてる？
        & (sma_65["close"] * 0.95 >= sma_130["close"])
        & (sma_5["close"] >= 100)
        & (sma_5["close"] <= 1000)
        & (sma_5["volume"] >= 50000)  # 流動性があるもの
    ]
    dead_cross = sma_5[(sma_5["close"] < sma_25["close"])]

    golden_cross = golden_cross[25:]
    dead_cross = dead_cross[25:]

    # 日付のリストに変換
    golden_list = [
        datetime.fromtimestamp(x).date() for x in golden_cross["timestamp"].values
    ]
    dead_list = [
        datetime.fromtimestamp(x).date() for x in dead_cross["timestamp"].values
    ]
    return golden_list, dead_list


JST = timezone(timedelta(hours=+9), "JST")

start_date = date(2021, 7, 15)
end_date = date(2021, 8, 7)
deposit = 300_000
order_under_limit = 1  # ゴールデンクロス時の最小購入金額


with open("stocks.pickle", "rb") as f:
    stocks = pickle.load(f)


golden_dict = defaultdict(list)
dead_dict = defaultdict(list)
for code, stock in stocks.items():
    if not stock.empty:
        golden, dead = generate_cross_date_list(stock)
        for l, d in zip((golden, dead), (golden_dict, dead_dict)):
            for day in l:
                d[day].append(code)


def trade_func(date: date, portfolio: Portfolio):
    """

    :param date: 取引を実施する日
    :param portfolio: 取引する時点のポートフォリオ
    :return: 注文リスト
    :rtype: SellMarketOrder
    """
    order_list = []
    # Dead crossが発生していて持っている株があれば売る
    if date in dead_dict.keys():
        order_list = [
            SellMarketOrder(code, portfolio.stocks[code].current_count)
            for code in dead_dict[date]
            if code in portfolio.stocks
        ]
    # 保有していない株でgolden crossが発生していたら買う
    if date in golden_dict.keys():
        for code in golden_dict[date]:
            # if code not in portfolio.stocks:
            order_list.append(BuyMarketOrderMoreThan(code, 100, order_under_limit))
    return order_list


def get_open_price_func(date, code):
    stock = stocks[code]
    for _, row in stock.iterrows():
        if date == datetime.fromtimestamp(row["timestamp"]).date():
            return row["open"]
    return 0


def get_close_price_func(date, code):
    stock = stocks[code]
    for _, row in stock.iterrows():
        if date == datetime.fromtimestamp(row["timestamp"]).date():
            return row["close"]
    return 0


_, result = simulate(
    start_date,
    end_date,
    deposit,
    trade_func,
    get_open_price_func,
    get_close_price_func,
)

print(result)
