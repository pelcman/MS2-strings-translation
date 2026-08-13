# 翻訳メモリによる自動補完
#   PYTHONIOENCODING=utf-8 python work/scripts/tm_prefill.py scriptquest
#
# 同じ韓国語原文が別のキーで既に翻訳されていることが多いため、
# 全ファイルの ko→jp 対訳から索引を作り、欠落キーの KO 原文と完全一致するものを
# 自動で埋める。残りだけを翻訳ワーカーに回せば効率が大きく上がる。
#
# 出力:
#   work/missing/<file>.ja.auto.tsv  — 自動補完できた分(そのまま apply 可能)
#   work/missing/<file>.tsv          — 残り(未一致)だけに絞り込んで上書き
import json, os, re, sys, glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MIS = os.path.join(ROOT, "work", "missing")
PH = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\].*)?$")
HAN = re.compile(r"[가-힣]")
SKIP = {"npc", "type", "class", "regionID", "grade", "comment", "commnet", "isTutorial"}


def build_index():
    """全ファイルの (フィールド名, KO原文) -> JA訳 索引"""
    idx = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "json_weblate", "jp", "*.json"))):
        fn = os.path.basename(p)[:-5]
        kp = os.path.join(ROOT, "json_weblate", "ko", fn + ".json")
        if not os.path.exists(kp):
            continue
        jp = json.load(open(p, encoding="utf-8"))
        ko = json.load(open(kp, encoding="utf-8"))
        for k, e in jp.items():
            ke = ko.get(k)
            if not isinstance(e, dict) or not isinstance(ke, dict):
                continue
            for f, v in e.items():
                kv = ke.get(f)
                if f in SKIP or f.endswith("Kor"):
                    continue
                if not isinstance(v, str) or not isinstance(kv, str):
                    continue
                if not v.strip() or not kv.strip() or PH.match(v.strip()):
                    continue
                if not HAN.search(kv) or HAN.search(v):
                    continue          # KO に実体があり JA にハングルが残っていないもののみ
                idx.setdefault((f, kv), v)
    return idx


fn = sys.argv[1]
idx = build_index()
print("翻訳メモリ索引: %d 件" % len(idx))

src = os.path.join(MIS, fn + ".tsv")
rows = [l.rstrip("\n").split("\t") for l in open(src, encoding="utf-8") if l.strip()]

hit, rest = [], []
for r in rows:
    if len(r) < 3:
        rest.append(r)
        continue
    key, field, kv = r[0], r[1], r[2].replace("⏎", "\n")
    ja = idx.get((field, kv))
    if ja:
        hit.append("%s\t%s\t%s" % (key, field, ja.replace("\n", "⏎")))
    else:
        rest.append(r)

with open(os.path.join(MIS, fn + ".ja.auto.tsv"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(hit) + ("\n" if hit else ""))
with open(src, "w", encoding="utf-8", newline="\n") as fh:
    for r in rest:
        fh.write("\t".join(r) + "\n")

print("自動補完 %d 件 / 残り %d 件" % (len(hit), len(rest)))
