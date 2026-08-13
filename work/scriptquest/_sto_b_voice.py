# -*- coding: utf-8 -*-
"""話者ごとの公式 JA セリフを列挙(口調採取用)"""
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(BASE))
HANGUL = re.compile(r"[가-힣]")
PLACE = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\].*)?$")
KANA = re.compile(r"[぀-ヿ]")

jp_bak = json.load(open(os.path.join(BASE, "scriptquest.backup.json"), encoding="utf-8"))
ko_sq = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "scriptquest.json"), encoding="utf-8"))

want = sys.argv[1:]
cnt = {}
for k, v in jp_bak.items():
    npc = (v or {}).get("npc") or ""
    if npc not in want:
        continue
    ja = (v or {}).get("name") or ""
    if not ja or PLACE.match(ja) or HANGUL.search(ja) or not KANA.search(ja):
        continue
    cnt[npc] = cnt.get(npc, 0) + 1
    ko = (ko_sq.get(k) or {}).get("name") or ""
    print("[%s] %s" % (npc, k))
    print("  KO:", ko.replace("\n", "\\n")[:200])
    print("  JA:", ja.replace("\n", "\\n")[:250])
print("---- counts:", cnt, file=sys.stderr)
