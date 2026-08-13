# 担当範囲の話者ごとに、公式JA訳が存在する行を数件ずつ出力(口調合わせ用)
import json, os, re, sys
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", ".."))
PH_RE = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+")

LO, HI = int(sys.argv[1]), int(sys.argv[2])
spk = []
for ln in open(os.path.join(BASE, "todo_story.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    n = int(num[3:])
    if LO <= n <= HI and npc not in spk:
        spk.append(npc)

sq_ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "scriptquest.json"), encoding="utf-8"))
sq_jp = json.load(open(os.path.join(BASE, "scriptquest.backup.json"), encoding="utf-8"))
by = defaultdict(list)
for k, e in sq_ko.items():
    npc = e.get("npc")
    if npc not in spk:
        continue
    jv = sq_jp.get(k, {}).get("name")
    if not isinstance(jv, str) or not jv or PH_RE.match(jv) or re.search(r"[가-힣]", jv):
        continue
    by[npc].append((e.get("name", ""), jv))

for s in spk:
    rows = by.get(s, [])
    print("=== %s : 公式訳 %d 件" % (s, len(rows)))
    for ko, ja in rows[:6]:
        print("   KO", repr(ko)[:130])
        print("   JA", repr(ja)[:130])
