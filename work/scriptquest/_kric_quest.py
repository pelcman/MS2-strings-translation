# 担当行がどのクエスト群に属するか調べる
import json, os, re
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
LO, HI = 1, 400

rows = {}
for ln in open(os.path.join(BASE, "todo_kritias.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    n = int(num[3:])
    if LO <= n <= HI:
        rows[n] = ko.replace("⏎", "\n")

targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
ko2keys = defaultdict(list)
for k, v in targets.items():
    ko2keys[v[0]].append(k)

grp = Counter()
for n in sorted(rows):
    ks = ko2keys.get(rows[n], [])
    for k in ks:
        parts = k.split("-")
        grp["-".join(parts[1:]) if len(parts) > 1 else k] += 1
print("グループ:", sorted(grp.items(), key=lambda x: -x[1]))
print()
# 各行のキー例
for n in [1, 39, 44, 56, 66, 199, 364, 370, 400]:
    print(n, ko2keys.get(rows[n], [])[:3])
