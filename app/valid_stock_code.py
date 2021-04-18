"""有効な銘柄コードとそのデータを一覧にして書き出す"""

import json
import os
from datetime import datetime
from io import StringIO
from time import sleep
from typing import Dict, List, Optional

import requests
from requests import Timeout
from matplotlib import pyplot
from pandas import DataFrame


class IndustryCodeRange:
    # 業種別コード帯
    NORIN_SUISAN = range(1300, 1500)
    KOGYO = range(1500, 1700)
    KENSETSU = range(1700, 2000)
    SHOKUHIN = range(2000, 3000)
    SENISEIHIN = range(3000, 3600)
    UNKNOWN_1 = range(3600, 3700)
    PARUPU_KAMI = range(3700, 4000)
    KAGAKU_IYAKUHIN = range(4000, 5000)
    SEKIYU_SEKITAN = range(5000, 5100)
    GOMU = range(5100, 5200)
    YOGYO = range(5200, 5400)
    TETSUUKO = range(5400, 5700)
    HITESSUKKINZOKU = range(5700, 5800)
    UNKNOWN_2 = range(5800, 5900)
    KINZOKUSEIHIN = range(5900, 6000)
    KIKAI = range(6000, 6500)
    DENKI = range(6500, 7000)
    YUSOYOKIKAI = range(7000, 7500)
    UNKNOWN_3 = range(7500, 7700)
    SEIMITSUKIKAI = range(7700, 7800)
    SONOTASEIHIN = range(7800, 7900)
    UNKNOWN_4 = range(7900, 8000)
    SHOGYO = range(8000, 8300)
    GINKO_NONBANKU = range(8300, 8600)
    SHOKEN_SHOKENSAKIMONO = range(8600, 8700)
    HOKEN = range(8700, 8800)
    FUDOSAN = range(8800, 9000)
    RIKUUN = range(9000, 9100)
    KAIUN = range(9100, 9200)
    KUUN = range(9200, 9300)
    SOKO_UNYU = range(9300, 9400)
    JOHOTSUSHIN = range(9400, 9500)
    DENKIGASU = range(9500, 9600)
    SABISU = range(9600, 10000)
    ALL_RANGES = (
        NORIN_SUISAN,
        KOGYO,
        KENSETSU,
        SHOKUHIN,
        SENISEIHIN,
        PARUPU_KAMI,
        KAGAKU_IYAKUHIN,
        SEKIYU_SEKITAN,
        GOMU,
        YOGYO,
        TETSUUKO,
        HITESSUKKINZOKU,
        KINZOKUSEIHIN,
        KIKAI,
        DENKI,
        YUSOYOKIKAI,
        SONOTASEIHIN,
        SHOGYO,
        GINKO_NONBANKU,
        SHOKEN_SHOKENSAKIMONO,
        HOKEN,
        FUDOSAN,
        RIKUUN,
        KAIUN,
        KUUN,
        SOKO_UNYU,
        JOHOTSUSHIN,
        DENKIGASU,
        SABISU,
        UNKNOWN_1,
        UNKNOWN_2,
        UNKNOWN_3,
        UNKNOWN_4,
    )


# データ取得元
URL = "https://query1.finance.yahoo.com/v7/finance/chart/{stock_code}?range={selected_range}&interval={interval}&indicators=quote&includeTimestamps=true"

# APIにリクエストを投げる間隔（sec）
REQUEST_INTARVAL = 3
# APIに繋がらない
REQUEST_TIMEOUT = 10.0
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
        stock_code=stock_code, selected_range=str(selected_range) + "d", interval="1d"
    )
    for _ in range(RETRY_COUNT):
        text = {}
        try:
            res = requests.get(param, timeout=REQUEST_TIMEOUT)
            text = json.load(StringIO(res.text))
        except Timeout as e:
            print(stock_code)
            print(e)

        if text["chart"]["error"] is not None:
            print(stock_code + ": ", end="")
            print(text["chart"]["error"])
            return None
        return text
    else:
        print(f"timeout occured. code:{stock_code}")
        return None


def write_code(prefix: str, code: str):
    """codeのリストをファイルに書き出す"""
    with open(STOCK_CODE_DIR + prefix + "codes.txt", mode="a") as f:
        f.write(code + "\n")


def write_json(code: str, prefix: str, data: Dict):
    """銘柄の情報をjsonファイルに書き出す"""

    with open(JSON_CODE_DIR + prefix + "_" + code + ".json", mode="w") as f:
        json.dump(data, f)


def get_valid_stock_codes(filename_prefix: str, selected_range: range):
    """有効な銘柄コードを取得する"""

    for i in selected_range:
        sleep(REQUEST_INTARVAL)
        assumed_code = str(i).zfill(4) + ".T"
        stock_info = get_stockinfo(assumed_code, 30)
        if stock_info is None:
            continue
        write_json(assumed_code, filename_prefix, stock_info)
        write_code(filename_prefix, assumed_code)


if __name__ == "__main__":
    prefix = datetime.strftime(datetime.now(), "%Y%m%d")
    for r in IndustryCodeRange.ALL_RANGES:
        get_valid_stock_codes(prefix, r)
