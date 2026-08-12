# 担当範囲(###1-400 / 再生成後 K-C)の KO 原文を抽出し、既存訳・TM ヒットを調べる
import json, os, glob, sys
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
LO, HI = 1, 400

rows = {}
for ln in open(os.path.join(BASE, "todo_kritias.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    n = int(num[3:])
    if LO <= n <= HI:
        rows[n] = (npc, ko.replace("⏎", "\n"), en)

targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
kos = {v[0] for v in targets.values()}
print("rows:", len(rows), "not-in-targets:", [n for n in rows if rows[n][1] not in kos])

exist = {}
for p in sorted(glob.glob(os.path.join(BASE, "sq_*.json"))):
    d = json.load(open(p, encoding="utf-8"))
    d.pop("_comment", None)
    for k, v in d.items():
        exist.setdefault(k, (os.path.basename(p), v))

tms = json.load(open(os.path.join(BASE, "tm_self.json"), encoding="utf-8"))
tmc = json.load(open(os.path.join(BASE, "tm_cross.json"), encoding="utf-8"))

hit = {}
print("---- 既存 sq_* にある行 ----")
for n in sorted(rows):
    k = rows[n][1]
    if k in exist:
        hit[n] = exist[k][1]
        print(n, exist[k][0], repr(k)[:60], "=>", repr(exist[k][1])[:80])
print("---- tm_self(公式 scriptquest 既訳)にある行 ----")
for n in sorted(rows):
    k = rows[n][1]
    if n not in hit and k in tms:
        hit[n] = tms[k]
        print(n, repr(k)[:60], "=>", repr(tms[k])[:90])
print("---- tm_cross にある行 ----")
for n in sorted(rows):
    k = rows[n][1]
    if n not in hit and k in tmc:
        hit[n] = tmc[k]
        print(n, repr(k)[:60], "=>", repr(tmc[k])[:90])
print("TMヒット合計:", len(hit))

seen = defaultdict(list)
for n in rows:
    seen[rows[n][1]].append(n)
print("内部重複:", [v for v in seen.values() if len(v) > 1])
print("ユニークKO:", len(seen))

json.dump({str(n): rows[n][1] for n in sorted(rows)},
          open(os.path.join(BASE, "_kric_ko.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump({str(n): hit[n] for n in sorted(hit)},
          open(os.path.join(BASE, "_kric_tm.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
sp = defaultdict(int)
for n in rows:
    sp[rows[n][0]] += 1
print("話者:", sorted(sp.items(), key=lambda x: -x[1]))
