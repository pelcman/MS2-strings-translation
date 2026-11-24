# 2026-11 再同期: 数値テンプレートTM。KO原文の数値だけが異なる既訳があれば、数値を差し替えて流用する
#   PYTHONIOENCODING=utf-8 python work/resync/numtm.py <データ名> [...]
# 出力: work/resync/<データ名>.numtm.json(適用可能な訳)、todo.json からは除去
import json, os, re, sys, glob, collections
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "work", "resync")
HAN = re.compile(r"[가-힣]")
PH = re.compile(r"^[A-Z0-9$]+(_+[A-Z0-9$]+)+(:\[F\].*)?$")
NUM = re.compile(r"(?<![#$:\w])\d+(?:\.\d+)?")   # 色コード(#00aaef)・$item:123$ 内の数字は除く
def tmpl(s): return NUM.sub("\x00", s), NUM.findall(s)

idx = {}
for p in glob.glob(os.path.join(ROOT, "json_weblate", "jp", "*.json")):
    fn = os.path.basename(p)[:-5]
    kp = os.path.join(ROOT, "json_weblate", "ko", fn + ".json")
    if not os.path.exists(kp): continue
    jp = json.load(open(p, encoding="utf-8")); ko = json.load(open(kp, encoding="utf-8"))
    for k, e in jp.items():
        if not isinstance(e, dict) or not isinstance(ko.get(k), dict): continue
        for f, v in e.items():
            kv = ko[k].get(f)
            if not isinstance(v, str) or not isinstance(kv, str) or not HAN.search(kv) or HAN.search(v) or PH.match(v.strip()): continue
            t, nums = tmpl(kv)
            if not nums: continue
            idx.setdefault((f, t), []).append((nums, v))

def adapt(nums_old, ja_old, nums_new):
    jn = NUM.findall(ja_old)
    if sorted(jn) != sorted(nums_old): return None
    if len(set(nums_old)) == len(nums_old):          # 値が一意 → 値で対応付け
        m = dict(zip(nums_old, nums_new))
        return NUM.sub(lambda x: m[x.group(0)], ja_old)
    if jn == nums_old:                                 # 出現順が同じ → 順に置換
        it = iter(nums_new)
        return NUM.sub(lambda x: next(it), ja_old)
    return None

for fn in sys.argv[1:]:
    tp = os.path.join(OUT, fn + ".todo.json")
    todo = json.load(open(tp, encoding="utf-8"))
    hit, rest = {}, {}
    for k, e in todo.items():
        for f, (kv, ev) in e.items():
            ja = None
            if isinstance(kv, str) and HAN.search(kv):
                t, nums = tmpl(kv)
                for nums_old, ja_old in idx.get((f, t), []):
                    ja = adapt(nums_old, ja_old, nums)
                    if ja: break
            if ja: hit.setdefault(k, {})[f] = ja
            else: rest.setdefault(k, {})[f] = [kv, ev]
    json.dump(hit, open(os.path.join(OUT, fn + ".numtm.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    json.dump(rest, open(tp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(fn, "数値TM一致", sum(len(e) for e in hit.values()), "残り", sum(len(e) for e in rest.values()))
