# scriptquest の未訳エントリから、指定グループのものだけを抜き出して todo ファイルを作る
#   PYTHONIOENCODING=utf-8 python work/scriptquest/extract_subset.py Kritias todo_kritias.txt
# 出力形式は todo.txt と同じ: ###n|話者NPC(KO)|KO原文(⏎=改行)|EN参考訳(110字で切詰)
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", ".."))
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")

pattern = sys.argv[1]
outname = sys.argv[2]

targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
jp = json.load(open(os.path.join(ROOT, "json_weblate", "jp", "scriptquest.json"), encoding="utf-8"))
ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "scriptquest.json"), encoding="utf-8"))

rows = []
for k, (kov, env) in targets.items():
    if pattern not in k:
        continue
    cur = jp.get(k, {}).get("name")
    if not (isinstance(cur, str) and PH.search(cur)):
        continue                      # 適用済み
    npc = ko.get(k, {}).get("npc") or "?"
    rows.append((k, npc, kov, env or ""))

with open(os.path.join(BASE, outname), "w", encoding="utf-8", newline="\n") as fh:
    for i, (k, npc, kov, env) in enumerate(rows, 1):
        fh.write("###%d|%s|%s|%s\n" % (
            i, npc, kov.replace("\n", "⏎"), env.replace("\n", "⏎")[:110]))

print("%s: %d 行 (%s 系の未訳)" % (outname, len(rows), pattern))
