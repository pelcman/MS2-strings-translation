# -*- coding: utf-8 -*-
"""番号キーの訳マップ(_sto_b_jaNNN.json) から sq_stoNNN.json を生成"""
import json, os, sys, re

BASE = os.path.dirname(os.path.abspath(__file__))
src = json.load(open(os.path.join(BASE, "_sto_b_src.json"), encoding="utf-8"))
targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
kos = {v[0] for v in targets.values()}
HANGUL = re.compile(r"[가-힣]")
PP = re.compile(r"\$pp[2r]?:[^$]*\$")

ja_file, out_file, comment = sys.argv[1], sys.argv[2], sys.argv[3]
ja = json.load(open(os.path.join(BASE, ja_file), encoding="utf-8"))

out = {"_comment": comment}
bad = []
for num, t in ja.items():
    d = src.get(num)
    if d is None:
        bad.append(("NO_SUCH_NUM", num)); continue
    ko = d["ko"]
    if ko not in kos:
        bad.append(("KO_NOT_TARGET", num))
    if HANGUL.search(t):
        bad.append(("HANGUL", num))
    if PP.search(t):
        bad.append(("PP", num))
    if ko in out:
        bad.append(("DUP_KO", num))
    kl, tl = ko.split("\n"), t.split("\n")
    if len(kl) != len(tl):
        bad.append(("LINECOUNT %d!=%d" % (len(kl), len(tl)), num))
    else:
        for i, (a, b) in enumerate(zip(kl, tl)):
            ta = len(a) - len(a.rstrip(" "))
            tb = len(b) - len(b.rstrip(" "))
            if ta != tb:
                bad.append(("TRAILSP L%d %d!=%d" % (i + 1, ta, tb), num))
    out[ko] = t

with open(os.path.join(BASE, out_file), "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(out_file, "entries:", len(out) - 1, "problems:", bad)
