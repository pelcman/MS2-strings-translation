# _sto_ja00N.json (###番号 -> JA) と todo_story.txt から sq_sto00N.json を組み立てる
#   PYTHONIOENCODING=utf-8 python work/scriptquest/_sto_build.py 1
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
COMMENTS = {
    1: "ストーリー バッチ001 (###1-100 倉庫の人々救出・ラフォイの革収集・ビトの不思議な帽子・ロックフェラータワー・ジュコの飴作り・バルグルの遺跡保存・ダンパの武器庫・バエルの庭)",
    2: "ストーリー バッチ002 (###101-200 バエルの庭再汚染・ゴメイの補給品・デールンの監視塔・チェロキの野生イノシシ・アリヤールのモンスター図鑑と投擲オブジェクト)",
    3: "ストーリー バッチ003 (###201-300 アリヤールの投擲オブジェクト検証・アヤフヤ商団の来訪・モンスター図鑑の種族別調査・ゴダールの島の風習)",
    4: "ストーリー バッチ004 (###301-400 ゴダールの島の風習・マイキーの怪しい来訪者・アリヤールの商品価値検証シリーズ)",
    5: "ストーリー バッチ005 (###401-500 アリヤールの商品価値検証シリーズ後半・マヨールの異文化体験)",
}

n = int(sys.argv[1])
lo, hi = (n - 1) * 100 + 1, n * 100

rows = {}
for ln in open(os.path.join(BASE, "todo_story.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    rows[int(num[3:])] = ko.replace("⏎", "\n")

ja = json.load(open(os.path.join(BASE, "_sto_ja%03d.json" % n), encoding="utf-8"))

by_ko = {}
for i in range(lo, hi + 1):
    by_ko.setdefault(rows[i], []).append(i)

out = {"_comment": COMMENTS[n]}
missing = []
for ko, nums in by_ko.items():
    vals = {ja[str(i)] for i in nums if str(i) in ja}
    if not vals:
        missing.append(nums)
        continue
    assert len(vals) == 1, (nums, vals)
    out[ko] = vals.pop()

# 担当外番号の訳も入っていればそのキーで追加(バッチ跨ぎの重複対策)
for k, v in ja.items():
    i = int(k)
    if not (lo <= i <= hi):
        out[rows[i]] = v

if missing:
    print("!! 訳が無い番号:", missing)
    sys.exit(1)

p = os.path.join(BASE, "sq_sto%03d.json" % n)
with open(p, "wb") as fh:
    fh.write(json.dumps(out, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
print(os.path.basename(p), len(out) - 1, "件 (対象行", hi - lo + 1, ")")
