# 担当範囲の各行が属する scriptquest キー(=クエストID/名)を調べる
import json, os
from collections import defaultdict, OrderedDict

BASE = os.path.dirname(os.path.abspath(__file__))
LO, HI = 1, 400
rows = OrderedDict()
for ln in open(os.path.join(BASE, "todo_kritias.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    n = int(num[3:])
    if LO <= n <= HI:
        rows[n] = ko.replace("⏎", "\n")

targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
byko = defaultdict(list)
for k, v in targets.items():
    byko[v[0]].append(k)

out = OrderedDict()
for n, ko in rows.items():
    out[n] = byko[ko]

groups = []
prev = None
for n, ks in out.items():
    tag = sorted({k.split("-", 1)[1] if "-" in k else "?" for k in ks})
    tag = tuple(tag)
    if tag != prev:
        groups.append([n, n, tag])
        prev = tag
    else:
        groups[-1][1] = n
for a, b, t in groups:
    print(f"{a}-{b}: {t}")
json.dump({str(n): out[n] for n in out}, open(os.path.join(BASE, "_krib_keys.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
