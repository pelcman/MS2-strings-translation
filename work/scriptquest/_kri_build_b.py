# _krib_ja00N.json (###番号 -> JA) と todo_kritias.txt から sq_kri00N.json を組み立てる
#   PYTHONIOENCODING=utf-8 python work/scriptquest/_kri_build_b.py 5
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
COMMENTS = {
    5: "クリティアス バッチ005 (###1-100 定期評価とブリーチェの探査任務・資源確保・ネコ探し)",
    6: "クリティアス バッチ006 (###101-200 探査地域拡大・ケルベス討伐・融合炉作戦)",
    7: "クリティアス バッチ007 (###201-300 クリティアス本土へ・ロボット工場・ルミナイツ定期評価)",
    8: "クリティアス バッチ008 (###301-400 ルミナイツのエネル研究・探査資料回収・闇の軍団撃退)",
}

n = int(sys.argv[1])
lo, hi = (n - 5) * 100 + 1, (n - 4) * 100

rows = {}
for ln in open(os.path.join(BASE, "todo_kritias.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    rows[int(num[3:])] = ko.replace("⏎", "\n")

ja = json.load(open(os.path.join(BASE, "_krib_ja%03d.json" % n), encoding="utf-8"))

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
for k, v in ja.items():
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
