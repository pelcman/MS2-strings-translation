# questdescription_final.backup.json の Kritias_2018_12 公式訳を抽出
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", ".."))
p = os.path.join(ROOT, "work", "questdesc", "questdescription_final.backup.json")
d = json.load(open(p, encoding="utf-8"))
out = []
for k, v in d.items():
    if "Kritias" not in k:
        continue
    out.append((k, v))
print("Kritias 系エントリ数:", len(out))
keys = sorted({k.split("-", 1)[1] if "-" in k else k for k, _ in out})
print("グループ:", keys[:20])

sel = [(k, v) for k, v in out if "2018_12" in k]
print("2018_12:", len(sel))
with open(os.path.join(BASE, "_kric_qd_dump.txt"), "w", encoding="utf-8") as fh:
    for k, v in sel:
        fh.write("=== " + k + "\n")
        for fld, val in v.items():
            if isinstance(val, str) and val.strip():
                fh.write("  [%s] %s\n" % (fld, val.replace("\n", " ⏎ ")))
print("dump written")
