from pandas.core.frame import DataFrame
from collections import defaultdict
import pickle
from stock_info_accessor import YahooFinanceAPIClient as Client


def read_valid_codes():
    with open("./data/codes.txt") as f:
        return [x.strip() + ".T" for x in f.readlines()]


def create_stock_data():
    """指定した銘柄(code_list)それぞれの単元株数と日足(始値・終値）を含む辞書を作成"""

    stocks = defaultdict(DataFrame)
    client = Client("2years")
    code_list = read_valid_codes()
    for code in code_list:
        res = client.get_stockinfo(code)
        if res is not None:
            stocks[code] = res
    return stocks


def save_to_pickle(stocks):
    with open("stocks.pickle", "wb") as f:
        stocks = pickle.dump(stocks, f)


def main():
    stocks = create_stock_data()
    save_to_pickle(stocks)


if __name__ == "__main__":
    main()
