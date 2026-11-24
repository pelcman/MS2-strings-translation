# 2026-11 再同期: ワーカー出力(ユニット訳)を キー単位の訳マップに展開する
#   PYTHONIOENCODING=utf-8 python work/resync/expand.py
# 出力: work/resync/<データ名>.ja.json  ({キー: {フィールド: 訳}})。数値違いの同型文は数値を差し替えて生成
import json, os, re, glob, collections
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "work", "resync"); B = os.path.join(OUT, "batches")
NUM = re.compile(r"(?<![#$:A-Za-z0-9_.])[0-9]+(?:\.[0-9]+)?")   # 日本語・ハングル直後の数字も拾う(色コード・タグ内は除外)
units = json.load(open(os.path.join(B, "units.json"), encoding="utf-8"))
tr = {}
for p in sorted(glob.glob(os.path.join(B, "*.out*.json"))):
    tr.update(json.load(open(p, encoding="utf-8")))

def adapt(src_old, ja_old, src_new):
    a, b = NUM.findall(src_old), NUM.findall(src_new)
    if a == b: return ja_old
    jn = NUM.findall(ja_old)
    if len(a) != len(b): return None
    if len(set(a)) == len(a) and all(jn.count(v) == 1 for v in a):
        # 値が一意 → 値で対応付け(訳文側だけにある数値「1秒ごと」等はそのまま)
        m = dict(zip(a, b)); return NUM.sub(lambda x: m.get(x.group(0), x.group(0)), ja_old)
    if sorted(jn) != sorted(a): return None
    if jn == a:
        it = iter(b); return NUM.sub(lambda x: next(it), ja_old)
    return None

res = collections.defaultdict(dict); miss = []; fail = []
for uid, mem in units.items():
    ja = tr.get(uid)
    if not ja: miss.append(uid); continue
    _, _, _, ko0, en0 = mem[0]
    s0 = ko0 if ko0 and re.search(r"[가-힣]", ko0) else (en0 or ko0 or "")
    for fn, k, f, kv, ev in mem:
        s = kv if kv and re.search(r"[가-힣]", kv) else (ev or kv or "")
        j = adapt(s0, ja, s)
        if j is None: fail.append((uid, k, s)); continue
        res[fn].setdefault(k, {})[f] = j
for fn, d in res.items():
    json.dump(d, open(os.path.join(OUT, fn + ".ja.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(fn, sum(len(e) for e in d.values()), "文字列")
print("未訳ユニット", len(miss), miss[:10])
print("数値差し替え失敗", len(fail))
json.dump(fail, open(os.path.join(B, "expand_fail.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
