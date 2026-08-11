# -*- coding: utf-8 -*-
"""qd_rules_idx.json(most_common順のインデックス) → qd_rules.json(正規化キー)を生成・検証。"""
import json, os, re, sys, io, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")
HG = re.compile(r"[가-힯]")
NUM = re.compile(r"\d+")
PP = re.compile(r"\$pp[^$]*\$")
# 和文文字の直後の半角コロンを全角に(プレースホルダー $map:...$ 等の : は латин字の後なので対象外)
COLON = re.compile(r"(?<=[぀-ヿ一-鿿ー])\:")

fn = "questdescription_final"
jp = json.load(open(os.path.join(ROOT, f"json_weblate/jp/{fn}.json"), encoding="utf-8"))
ko = json.load(open(os.path.join(ROOT, f"json_weblate/ko/{fn}.json"), encoding="utf-8"))

# 既訳の ?/？ 使用比率
half = full = 0
for k, v in jp.items():
    for f, s in v.items():
        if isinstance(s, str) and s and not PH.search(s) and not HG.search(s):
            half += s.count("?") ; full += s.count("？")
print(f"既訳の ? : {half} / ？ : {full}")

# TM・自動テンプレートを再現して残パターンを再列挙(apply_qd.py と同一ロジック)
tm = {}
learn = collections.defaultdict(set)
for k, v in jp.items():
    for f, s in v.items():
        if not isinstance(s, str) or not s or PH.search(s) or HG.search(s): continue
        kn = ko.get(k, {}).get(f, "")
        if not isinstance(kn, str) or not kn: continue
        kn2 = PP.sub("", kn)
        tm.setdefault(kn2, s)
        knums = NUM.findall(kn2)
        if knums and knums == NUM.findall(s):
            learn[NUM.sub("#", kn2)].add(NUM.sub("{}", s))
templates = {p for p, t in learn.items() if len(t) == 1}
rest = collections.Counter()
for k, v in jp.items():
    for f, s in v.items():
        if not isinstance(s, str) or not s or not (PH.search(s) or HG.search(s)): continue
        kn = ko.get(k, {}).get(f, "")
        if not isinstance(kn, str) or not kn or PH.search(kn): continue
        kn2 = PP.sub("", kn)
        if kn2 in tm: continue
        norm = NUM.sub("#", kn2)
        if norm in templates: continue
        rest[norm] += 1

idx = {k: v for k, v in json.load(open(os.path.join(ROOT, "work/questdesc/qd_rules_idx.json"), encoding="utf-8")).items() if not k.startswith("_")}
ordered = [p for p, c in rest.most_common() if c >= 3]
print(f"count>=3 パターン: {len(ordered)} / idx エントリ: {len(idx)}")
out = {}
errors = 0
use_full = full >= half
for i, norm in enumerate(ordered, 1):
    ja = idx.get(str(i))
    if ja is None:
        print(f"  [{i}] JA なし: {norm[:60]!r}"); errors += 1; continue
    ja = COLON.sub("：", ja)
    if use_full:
        ja = ja.replace("!", "！").replace("?", "？")
    if ja.count("{}") != norm.count("#"):
        print(f"  [{i}] スロット不一致 {ja.count('{}')} vs {norm.count('#')}: {norm[:60]!r}"); errors += 1; continue
    if ja.count("\n") != norm.count("\n"):
        print(f"  [{i}] 行数不一致 {ja.count(chr(10))} vs {norm.count(chr(10))}: {norm[:60]!r}"); errors += 1; continue
    out[norm] = ja
print(f"生成 {len(out)} / エラー {errors}")
with open(os.path.join(ROOT, "work/questdesc/qd_rules.json"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
