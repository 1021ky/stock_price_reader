# -*- coding: utf-8 -*-
import requests

URL_TEMPLATE = (
    "https://www.jpx.co.jp/listing/co/nlsgeu000005b162-att/HP-{year}.{month}.pdf"
)

OUTPUT_DIRECTORY = "data/"
OUTPUT_FILE = "codes.pdf"
OUTPUT_FILEPATH = OUTPUT_DIRECTORY + OUTPUT_FILE


def get_codes_pdf(year, month):
    url = URL_TEMPLATE.format(year=year, month=month)
    res = requests.get(url)
    if res.status_code != requests.codes.ok:
        print("not found")
        return
    prefix = f"{year}_{month}_"
    # 過去のファイルをあとから参照できるようにprefixつけて保存しておく
    with open(OUTPUT_DIRECTORY + prefix + OUTPUT_FILE, "wb") as f:
        f.write(res.content)
    with open(OUTPUT_FILEPATH, "wb") as f:
        f.write(res.content)


def main():
    from datetime import datetime, timedelta, timezone

    JST = timezone(timedelta(hours=+9), "JST")
    d = datetime.now(JST)
    get_codes_pdf(str(d.year), str(d.month - 1))


if __name__ == "__main__":
    main()
