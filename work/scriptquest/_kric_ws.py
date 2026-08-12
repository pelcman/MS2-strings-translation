# 指定範囲の KO 原文を、行頭/行末空白を可視化して出力
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
lo, hi = int(sys.argv[1]), int(sys.argv[2])
rows = {}
for ln in open(os.path.join(BASE, "todo_kritias.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    rows[int(num[3:])] = (npc, ko.replace("⏎", "\n"))

for n in range(lo, hi + 1):
    npc, ko = rows[n]
    marks = []
    for i, line in enumerate(ko.split("\n")):
        pre = len(line) - len(line.lstrip(" \t"))
        suf = len(line) - len(line.rstrip(" \t"))
        t = "TAB" if "\t" in line else ""
        if pre or suf or t:
            marks.append("L%d:pre=%d,suf=%d%s" % (i, pre, suf, ("," + t) if t else ""))
    if marks:
        print("###%d [%s] %s" % (n, npc, " ".join(marks)))
