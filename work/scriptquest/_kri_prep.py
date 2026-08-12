# 担当範囲(###1-400)の KO 原文を抽出し、既存 sq_map*.json に同一キーがあるか確認する
import json, os, glob, sys

BASE = os.path.dirname(os.path.abspath(__file__))
lines = open(os.path.join(BASE, "todo_kritias.txt"), encoding="utf-8").read().split("\n")
rows = {}
for ln in lines:
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    n = int(num[3:])
    if 1 <= n <= 400:
        rows[n] = (npc, ko.replace("⏎", "\n"), en)

targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
kos = {v[0] for v in targets.values()}

missing = [n for n, (a, k, e) in rows.items() if k not in kos]
print("rows:", len(rows), "not-in-targets:", missing)

# 既存 sq_map の訳
exist = {}
for p in sorted(glob.glob(os.path.join(BASE, "sq_map*.json"))):
    d = json.load(open(p, encoding="utf-8"))
    d.pop("_comment", None)
    for k, v in d.items():
        exist.setdefault(k, (os.path.basename(p), v))

dup = {n: exist[k] for n, (a, k, e) in rows.items() if k in exist}
print("already-translated:", len(dup))
for n in sorted(dup):
    print(n, dup[n][0], repr(rows[n][1])[:70], "=>", repr(dup[n][1])[:90])

# KO 内の重複
from collections import defaultdict
seen = defaultdict(list)
for n, (a, k, e) in rows.items():
    seen[k].append(n)
print("internal-dup groups:", [v for v in seen.values() if len(v) > 1])
json.dump({str(n): rows[n][1] for n in sorted(rows)}, open(os.path.join(BASE, "_kri_ko.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
