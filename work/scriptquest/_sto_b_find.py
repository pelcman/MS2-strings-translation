# -*- coding: utf-8 -*-
"""公式 KO->JA ペア(scriptquest/questdescription_final)を部分文字列で検索"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
sq = json.load(open(os.path.join(BASE, "_sto_b_official_sq.json"), encoding="utf-8"))
qd = json.load(open(os.path.join(BASE, "_sto_b_official_qd.json"), encoding="utf-8"))

pat = sys.argv[1]
lim = int(sys.argv[2]) if len(sys.argv) > 2 else 8
src = sys.argv[3] if len(sys.argv) > 3 else "both"

n = 0
for tag, d in (("SQ", sq), ("QD", qd)):
    if src != "both" and src.upper() != tag:
        continue
    for ko, ja in d.items():
        if pat in ko:
            print("[%s] KO: %s" % (tag, ko.replace("\n", "\\n")))
            print("     JA: %s" % ja.replace("\n", "\\n"))
            print()
            n += 1
            if n >= lim:
                sys.exit()
print("(total %d)" % n)
