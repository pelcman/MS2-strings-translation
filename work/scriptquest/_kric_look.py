# tm_self / tm_cross / 既存 sq_*.json から KO 部分文字列で既訳を検索
import json, os, sys, glob

BASE = os.path.dirname(os.path.abspath(__file__))
q = sys.argv[1]
lim = int(sys.argv[2]) if len(sys.argv) > 2 else 12

srcs = []
srcs.append(("tm_self", json.load(open(os.path.join(BASE, "tm_self.json"), encoding="utf-8"))))
srcs.append(("tm_cross", json.load(open(os.path.join(BASE, "tm_cross.json"), encoding="utf-8"))))
sq = {}
for p in sorted(glob.glob(os.path.join(BASE, "sq_*.json"))):
    d = json.load(open(p, encoding="utf-8"))
    d.pop("_comment", None)
    for k, v in d.items():
        sq.setdefault(k, v)
srcs.append(("sq_*", sq))

for name, d in srcs:
    n = 0
    for k, v in d.items():
        if q in k:
            print("[%s] %s\n    => %s" % (name, k.replace("\n", "⏎")[:130], (v if isinstance(v, str) else str(v)).replace("\n", "⏎")[:130]))
            n += 1
            if n >= lim:
                break
    print("--- %s: %d 件表示" % (name, n))
