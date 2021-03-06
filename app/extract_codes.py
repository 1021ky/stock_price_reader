# -*- coding: utf-8 -*-
from pdfminer.high_level import extract_text
from re import compile

"""上場している銘柄一覧を抽出する。
抽出元は日本取引所グループJPX(https://www.jpx.co.jp/listing/co/01.html)で公開されている上場株式数のpdfファイル
"""

INPUT_DIRECTORY = "data/"
OUTPUT_DIRECTORY = "data/"
OUTPUT_FILE = "codes.txt"
INPUT_FILE = "codes.pdf"
INPUT_FILEPATH = INPUT_DIRECTORY + INPUT_FILE
OUTPUT_FILEPATH = OUTPUT_DIRECTORY + OUTPUT_FILE


def extract_codes(input_filepath=INPUT_FILEPATH, output_filepath=OUTPUT_FILEPATH):
    prog = compile(r"\((\d...)\)")
    text = extract_text(input_filepath)
    result = prog.findall(text)
    with open(output_filepath, "w") as f:
        f.write("\n".join(result))


def main():
    extract_codes()


if __name__ == "__main__":
    main()
