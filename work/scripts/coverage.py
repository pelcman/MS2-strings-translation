# 実カバー率レポート(読み取り専用)
#   PYTHONIOENCODING=utf-8 python work/scripts/coverage.py
#
# status.py は「jp ファイルに存在するキー」だけを分母にしていたため、
# ko/en にあって jp に無いキー(=そもそも翻訳枠が存在しない文字列)が
# 集計から漏れ、実際には未カバーなのに「完了」と表示されていた。
# ここでは jp に無い ko キーも分母に含めた実カバー率を出す。
import json, os, glob, re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
HAN = re.compile(r"[가-힣]")
CN = re.compile(r"[一-鿿]")
SKIP = {"npc", "type", "class", "regionID", "grade", "comment", "commnet", "isTutorial"}


def countable(f, v):
    return (f not in SKIP and not f.endswith("Kor")
            and isinstance(v, str) and bool(v.strip()))


rows = []
for p in sorted(glob.glob(os.path.join(ROOT, "json_weblate", "jp", "*.json"))):
    fn = os.path.basename(p)[:-5]
    kp = os.path.join(ROOT, "json_weblate", "ko", fn + ".json")
    if not os.path.exists(kp):
        continue
    jp = json.load(open(p, encoding="utf-8"))
    ko = json.load(open(kp, encoding="utf-8"))

    have = sum(1 for k, e in jp.items() if isinstance(e, dict)
               for f, v in e.items() if countable(f, v))
    miss = 0
    for k, e in ko.items():
        if k in jp or not isinstance(e, dict):
            continue
        for f, v in e.items():
            if countable(f, v) and (HAN.search(v) or CN.search(v)):
                miss += 1
    if miss:
        rows.append((fn, have, miss))

rows.sort(key=lambda r: -r[2])
print("%-30s %10s %10s %9s" % ("ファイル", "jp既存", "jpにキー無し", "実カバー率"))
print("-" * 63)
for fn, have, miss in rows:
    print("%-30s %10d %10d %8.1f%%" % (fn, have, miss, have * 100.0 / (have + miss)))
H, M = sum(r[1] for r in rows), sum(r[2] for r in rows)
print("-" * 63)
print("%-30s %10d %10d %8.1f%%" % ("合計", H, M, H * 100.0 / (H + M)))
print("\n※ jp にキーが無い分は Weblate 上に翻訳枠が存在しないため、")
print("   キーを追加しない限り翻訳できない。")
