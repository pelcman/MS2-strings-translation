# -*- coding: utf-8 -*-
"""公式既訳サルベージ: KO->JA 公式ペアを作り、担当範囲の KO と完全一致/近似一致を探す"""
import json, os, re, sys, difflib

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(BASE))

HANGUL = re.compile(r"[가-힣]")
PLACE = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\].*)?$")
CJKSIMP = re.compile(r"[一-鿿]")
KANA = re.compile(r"[぀-ヿ]")

ko_sq = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "scriptquest.json"), encoding="utf-8"))
jp_bak = json.load(open(os.path.join(BASE, "scriptquest.backup.json"), encoding="utf-8"))

pairs = {}   # ko -> ja (official)
for k, v in jp_bak.items():
    ja = (v or {}).get("name")
    if not ja or PLACE.match(ja) or HANGUL.search(ja):
        continue
    if not KANA.search(ja):
        continue
    ko = (ko_sq.get(k) or {}).get("name")
    if not ko or not HANGUL.search(ko):
        continue
    pairs.setdefault(ko, ja)

print("official KO->JA pairs:", len(pairs), file=sys.stderr)

# questdescription_final 側
qd_pairs = {}
try:
    ko_qd = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "questdescription_final.json"), encoding="utf-8"))
    jp_qd = json.load(open(os.path.join(os.path.dirname(BASE), "questdesc", "questdescription_final.backup.json"), encoding="utf-8"))
    for k, v in jp_qd.items():
        kv = ko_qd.get(k) or {}
        for fld, ja in (v or {}).items():
            if not isinstance(ja, str):
                continue
            if PLACE.match(ja) or HANGUL.search(ja) or not KANA.search(ja):
                continue
            ko = kv.get(fld)
            if isinstance(ko, str) and HANGUL.search(ko):
                qd_pairs.setdefault(ko, ja)
except Exception as e:
    print("qd load fail", e, file=sys.stderr)
print("qd KO->JA pairs:", len(qd_pairs), file=sys.stderr)

json.dump(pairs, open(os.path.join(BASE, "_sto_b_official_sq.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(qd_pairs, open(os.path.join(BASE, "_sto_b_official_qd.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

src = json.load(open(os.path.join(BASE, "_sto_b_src.json"), encoding="utf-8"))

def norm(s):
    s = re.sub(r"\$pp2?:[^$]*\$|\$ppr?:[^$]*\$", "", s)
    s = re.sub(r"\s+", "", s)
    return s

npairs = {}
for ko, ja in pairs.items():
    npairs.setdefault(norm(ko), (ko, ja))
nqd = {}
for ko, ja in qd_pairs.items():
    nqd.setdefault(norm(ko), (ko, ja))

allkeys = list(npairs.keys())
hits = {}
for num, d in src.items():
    if d["dup_of"]:
        continue
    ko = d["ko"]
    n = norm(ko)
    if n in npairs:
        hits[num] = {"kind": "exact_sq", "ko": ko, "src_ko": npairs[n][0], "ja": npairs[n][1]}
        continue
    if n in nqd:
        hits[num] = {"kind": "exact_qd", "ko": ko, "src_ko": nqd[n][0], "ja": nqd[n][1]}
        continue
    cands = difflib.get_close_matches(n, allkeys, n=1, cutoff=0.80)
    if cands:
        r = difflib.SequenceMatcher(None, n, cands[0]).ratio()
        hits[num] = {"kind": "near_sq_%.2f" % r, "ko": ko, "src_ko": npairs[cands[0]][0], "ja": npairs[cands[0]][1]}

json.dump(hits, open(os.path.join(BASE, "_sto_b_hits.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("hits:", len(hits), file=sys.stderr)
for num in sorted(hits, key=lambda x: int(x)):
    h = hits[num]
    print("###%s [%s]" % (num, h["kind"]))
    print("   KO :", h["ko"].replace("\n", "\\n")[:160])
    print("   SRC:", h["src_ko"].replace("\n", "\\n")[:160])
    print("   JA :", h["ja"].replace("\n", "\\n")[:200])
