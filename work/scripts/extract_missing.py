# jp に存在しないキー(ko/en にはある)を抽出して翻訳用 TSV を作る
#   PYTHONIOENCODING=utf-8 python work/scripts/extract_missing.py mapname
# 出力: work/missing/<file>.tsv   1行 = キー \t フィールド \t KO \t EN
# 改行は ⏎ に置換して1行1エントリを保つ。
import json, os, re, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "work", "missing")
PH = re.compile(r"^[A-Z0-9$]+(_+[A-Z0-9$]+)+(:\[F\].*)?$")
HAN = re.compile(r"[가-힣]")
CN = re.compile(r"[一-鿿]")
SKIP = {"npc", "type", "class", "regionID", "grade", "comment", "commnet", "isTutorial"}


def norm(k):
    p = k.split("-")
    return ((p[0].lstrip("0") or "0"), "-".join(p[1:]))


fn = sys.argv[1]
jp = json.load(open(os.path.join(ROOT, "json_weblate", "jp", fn + ".json"), encoding="utf-8"))
ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", fn + ".json"), encoding="utf-8"))
enp = os.path.join(ROOT, "json_weblate", "en", fn + ".json")
en = json.load(open(enp, encoding="utf-8")) if os.path.exists(enp) else {}

jpn = {norm(k) for k in jp}
os.makedirs(OUT, exist_ok=True)
rows = []
for k, e in ko.items():
    if norm(k) in jpn or not isinstance(e, dict):
        continue
    for f, v in e.items():
        if f in SKIP or f.endswith("Kor") or not isinstance(v, str) or not v.strip():
            continue
        if PH.match(v.strip()) or not (HAN.search(v) or CN.search(v)):
            continue          # 韓国語版にも実体が無いものは訳さない
        ev = en.get(k, {}).get(f) if isinstance(en.get(k), dict) else ""
        rows.append((k, f, v, ev if isinstance(ev, str) else ""))

def flat(s):
    """TSV の1行に収めるため、改行・復帰・タブをすべて記号化する。
    原文に生の \\r が混ざっているデータがあり(koritemdescription 3件・scriptquest 1件)、
    正規化しないと1レコードが複数の物理行に割れて後続処理が壊れる。"""
    return s.replace("\r\n", "⏎").replace("\r", "⏎").replace("\n", "⏎").replace("\t", " ")


p = os.path.join(OUT, fn + ".tsv")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    for k, f, kv, ev in rows:
        fh.write("%s\t%s\t%s\t%s\n" % (k, f, flat(kv), flat(ev)))
print("%s: %d 行 (キー %d 個)" % (p, len(rows), len({r[0] for r in rows})))
