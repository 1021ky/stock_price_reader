# -*- coding: utf-8 -*-
from pdfminer.high_level import extract_text
from re import compile

INPUT_DIRECTORY = "data/"
OUTPUT_DIRECTORY = "data/"
OUTPUT_FILE = "codes.txt"

prog = compile(r"\((\d...)\)")
text = extract_text(INPUT_DIRECTORY + "HP-2021.6.pdf")
result = prog.findall(text)
with open(OUTPUT_DIRECTORY + OUTPUT_FILE, "w") as f:
    f.write("\n".join(result))
