# KO 語を全データ種の ko ファイルから探し、対応する jp 値(公式優先)を出す
import json, os, re, sys, glob
from collections import Counter

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PH = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+")
FILES = sorted(glob.glob(os.path.join(ROOT, "json_weblate", "ko", "*.json")))

terms = sys.argv[1:]
cache = {}
for p in FILES:
    name = os.path.basename(p)
    jpp = os.path.join(ROOT, "json_weblate", "jp", name)
    if not os.path.exists(jpp):
        continue
    ko = json.load(open(p, encoding="utf-8"))
    jp = json.load(open(jpp, encoding="utf-8"))
    cache[name] = (ko, jp)

for t in terms:
    print("=== ", t)
    hits = Counter()
    for name, (ko, jp) in cache.items():
        for k, e in ko.items():
            if not isinstance(e, dict):
                continue
            for f, v in e.items():
                if v != t:
                    continue
                jv = jp.get(k, {}).get(f) if isinstance(jp.get(k), dict) else None
                if isinstance(jv, str) and jv and not PH.match(jv) and not re.search(r"[가-힣]", jv):
                    hits[(name, f, jv)] += 1
    for (n, f, jv), c in hits.most_common(8):
        print("   %-32s %-10s %s  x%d" % (n, f, jv, c))
    if not hits:
        print("   (なし)")
