# EN 一致による自動補完のうち、曖昧な英語名に基づくものを洗い出す(読み取り専用)
#   PYTHONIOENCODING=utf-8 python work/scripts/audit_en_tm.py
#
# 同じ英語名が複数の異なる韓国語・日本語に対応している場合(Rice / Love / ing など)、
# EN 一致だけを根拠にすると無関係な訳が入りうる。
# ここでは「同一 (フィールド, EN) が複数の異なる JA を持つ」= 曖昧語を検出し、
# その曖昧語で補完されたキーを列挙する。
import json, os, re, glob, collections

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MIS = os.path.join(ROOT, "work", "missing")
PH = re.compile(r"^[A-Z0-9$]+(_+[A-Z0-9$]+)+(:\[F\].*)?$")
SKIP = {"npc", "type", "class", "regionID", "grade", "comment", "commnet", "isTutorial"}

en2ja = collections.defaultdict(set)
for p in sorted(glob.glob(os.path.join(ROOT, "json_weblate", "jp", "*.json"))):
    fn = os.path.basename(p)[:-5]
    enp = os.path.join(ROOT, "json_weblate", "en", fn + ".json")
    if not os.path.exists(enp):
        continue
    jp = json.load(open(p, encoding="utf-8"))
    en = json.load(open(enp, encoding="utf-8"))
    for k, e in jp.items():
        ee = en.get(k)
        if not isinstance(e, dict) or not isinstance(ee, dict):
            continue
        for f, v in e.items():
            ev = ee.get(f)
            if f in SKIP or not isinstance(v, str) or not isinstance(ev, str):
                continue
            if not v.strip() or not ev.strip() or PH.match(v.strip()):
                continue
            en2ja[(f, ev)].add(v)

ambiguous = {k for k, s in en2ja.items() if len(s) > 1}
print("曖昧な英語名(同一ENに複数のJA): %d 種" % len(ambiguous))

hits = []
for p in sorted(glob.glob(os.path.join(ROOT, "json_weblate", "jp", "*.json"))):
    fn = os.path.basename(p)[:-5]
    bk = os.path.join(MIS, fn + ".backup.json")
    enp = os.path.join(ROOT, "json_weblate", "en", fn + ".json")
    if not os.path.exists(bk) or not os.path.exists(enp):
        continue
    base = json.load(open(bk, encoding="utf-8"))
    cur = json.load(open(p, encoding="utf-8"))
    ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", fn + ".json"), encoding="utf-8"))
    en = json.load(open(enp, encoding="utf-8"))
    for k, e in cur.items():
        if k in base or not isinstance(e, dict):
            continue
        for f, v in e.items():
            ev = en.get(k, {}).get(f) if isinstance(en.get(k), dict) else None
            kv = ko.get(k, {}).get(f) if isinstance(ko.get(k), dict) else None
            if isinstance(ev, str) and (f, ev) in ambiguous and isinstance(v, str):
                hits.append((fn, k, kv or "", ev, v))

print("曖昧語で補完された可能性のあるキー: %d 件" % len(hits))
for fn, k, kv, ev, v in hits[:40]:
    print("  %-20s %-24s KO:%-14s EN:%-14s JA:%s" % (fn, k, kv[:14], ev[:14], v[:24]))
