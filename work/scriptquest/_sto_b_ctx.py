# -*- coding: utf-8 -*-
"""担当範囲の一意 KO をバッチごとに読みやすく出力"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
src = json.load(open(os.path.join(BASE, "_sto_b_src.json"), encoding="utf-8"))
a, b = int(sys.argv[1]), int(sys.argv[2])
for n in range(a, b + 1):
    d = src.get(str(n))
    if d is None or d["dup_of"]:
        continue
    print("###%d |%s|" % (n, d["spk"]))
    print(d["ko"])
    print("--EN: " + d["en"])
    print("=" * 4)
