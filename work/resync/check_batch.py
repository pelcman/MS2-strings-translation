# 2026-11 再同期: ワーカー出力の検査
#   PYTHONIOENCODING=utf-8 python work/resync/check_batch.py <batch名>     例: scriptnpc_1
# 入力 batches/<batch>.in.json と 出力 batches/<batch>.out*.json ({id: 訳}、分割可) を照合する
import json, os, re, sys, collections
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "batches")
HAN = re.compile(r"[가-힣]")
TAG = re.compile(r"\$(?!pp)[A-Za-z]+(?::[^$]*)?\$|\{\d+\}|%[sd]|<[^>]+>")
name = sys.argv[1]
ins = json.load(open(os.path.join(B, name + ".in.json"), encoding="utf-8"))
import glob
out = {}
for p in sorted(glob.glob(os.path.join(B, name + ".out*.json"))):   # 分割出力 <batch>.out01.json 等もまとめて読む
    out.update(json.load(open(p, encoding="utf-8")))
errs = collections.Counter(); shown = 0
def bad(uid, msg):
    global shown
    errs[msg.split(":")[0]] += 1
    if shown < 60: print(uid, "-", msg); shown += 1
for u in ins:
    uid = u["id"]; src = u["ko"] if u["ko"] and HAN.search(u["ko"]) else (u["en"] or u["ko"] or "")
    ja = out.get(uid)
    if not isinstance(ja, str) or not ja.strip(): bad(uid, "未訳"); continue
    if HAN.search(ja): bad(uid, "ハングル残存")
    if "$pp" in ja: bad(uid, "助詞タグ$pp残存")
    a = collections.Counter(TAG.findall(src)); b = collections.Counter(TAG.findall(ja))
    if a != b:
        diff = (a - b) + (b - a)
        if not all(t.startswith("<font") or t == "</font>" for t in diff) or sum((a-b).values()) != sum((b-a).values()):
            bad(uid, "タグ不一致: 不足=%s 余分=%s" % (dict(a - b), dict(b - a)))
    if src.count("\n") != ja.count("\n"): bad(uid, "改行数不一致: 原文%d 訳%d" % (src.count("\n"), ja.count("\n")))
    if src.count("\n") != ja.count("\n"): bad(uid, "リテラル\n数不一致: 原文%d 訳%d" % (src.count("\n"), ja.count("\n")))
    if re.search(r"[ぁ-んァ-ヶ一-龥][!?]", ja): bad(uid, "半角!?(全角にする)")
    if "～" in ja: bad(uid, "全角チルダ～(〜にする)")
extra = set(out) - {u["id"] for u in ins}
if extra: print("in に無い id:", list(extra)[:5])
print("合計 %d ユニット / 訳あり %d / 問題 %s" % (len(ins), sum(1 for u in ins if out.get(u["id"])), dict(errs) or "なし"))
