# _kri_ja00N.json (###番号 -> JA) と todo_kritias.txt から sq_kri00N.json を組み立てる
#   PYTHONIOENCODING=utf-8 python work/scriptquest/_kri_build.py 1
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
COMMENTS = {
    1: "クリティアス バッチ001 (###1-100 ブリーチェ/メイソンの初期任務・ベンシ・ビロル・マルレーネ接見)",
    2: "クリティアス バッチ002 (###101-200 クラウディア救出・ワールド安全保障会議・キデル調査)",
    3: "クリティアス バッチ003 (###201-300 マルレーネとの対話・バンゲンハイムの娘・資源融合炉)",
    4: "クリティアス バッチ004 (###301-400 艦砲射撃とクラウディア覚醒・ゲオルク同盟・定期評価)",
}

n = int(sys.argv[1])
lo, hi = (n - 1) * 100 + 1, n * 100

rows = {}
for ln in open(os.path.join(BASE, "todo_kritias.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    rows[int(num[3:])] = ko.replace("⏎", "\n")

ja = json.load(open(os.path.join(BASE, "_kri_ja%03d.json" % n), encoding="utf-8"))

# 同一 KO を持つ番号どうしで訳を共有する
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

# 他バッチと KO が重複する行はこちらにも入れておく(値は同一)
extra = json.load(open(os.path.join(BASE, "_kri_ja%03d.json" % n), encoding="utf-8"))
for k, v in extra.items():
    i = int(k)
    if not (lo <= i <= hi):
        out[rows[i]] = v

if missing:
    print("!! 訳が無い番号:", missing)
    sys.exit(1)

p = os.path.join(BASE, "sq_kri%03d.json" % n)
with open(p, "wb") as fh:
    fh.write(json.dumps(out, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
print(os.path.basename(p), len(out) - 1, "件 (対象行", hi - lo + 1, ")")
