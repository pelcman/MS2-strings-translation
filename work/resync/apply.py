# 2026-11 再同期: 訳マップを jp に適用する
#   PYTHONIOENCODING=utf-8 python work/resync/apply.py <map.json> [<map.json> ...]
# マップの形式: { "<データ名>": { "<キー>": { "<フィールド>": "訳" } } }  または
#               ファイル名が <データ名>.fill.json / <データ名>.ja.json の場合は { "<キー>": {...} }
# - 既存キー: 未訳(プレースホルダー or ハングル)のフィールドだけを置換。翻訳済みは触らない
# - 欠落キー: ko の並び順でファイル末尾に追加(フィールドも ko の並び順、訳のあるフィールドのみ)
# - 初回適用前に work/resync/<データ名>.backup.json を作成
import json, os, re, shutil, sys, collections
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "work", "resync")
PH = re.compile(r"^[A-Z0-9$]+(_+[A-Z0-9$]+)+(:\[F\].*)?$")
HAN = re.compile(r"[가-힣]")

def untrans(v): return isinstance(v, str) and v.strip() and (PH.match(v.strip()) or HAN.search(v))

maps = collections.defaultdict(dict)
for p in sys.argv[1:]:
    b = os.path.basename(p)
    d = json.load(open(p, encoding="utf-8"))
    m = re.match(r"^(.+?)\.(fill|ja|ja\.[^.]+)\.json$", b)
    if m:
        d = {m.group(1): d}
    for fn, entries in d.items():
        for k, e in entries.items():
            for f, v in e.items():
                maps[fn].setdefault(k, {})[f] = v

for fn, tr in maps.items():
    JP = os.path.join(ROOT, "json_weblate", "jp", fn + ".json")
    raw = open(JP, "rb").read()
    tail = b"\n" if raw.endswith(b"\n") else b""
    jp = json.loads(raw.decode("utf-8"))
    assert json.dumps(jp, ensure_ascii=False, indent=2).encode("utf-8") + tail == raw, fn + ": roundtrip mismatch"
    ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", fn + ".json"), encoding="utf-8"))
    bk = os.path.join(OUT, fn + ".backup.json")
    if not os.path.exists(bk):
        shutil.copyfile(JP, bk)
    before = list(jp)
    orig = json.load(open(bk, encoding="utf-8"))   # 取り込み時点の jp(元からあるキーは構造を変えない)
    upd = add = skipped = 0
    for k, e in tr.items():
        for f, v in e.items():
            assert not HAN.search(v), "%s %s %s: ハングル残存 %r" % (fn, k, f, v)
            assert not PH.match(v.strip()), "%s %s: プレースホルダー" % (fn, k)
        if k in jp:
            for f, v in e.items():
                if f in jp[k] and untrans(jp[k][f]):
                    jp[k][f] = v; upd += 1
                elif f not in jp[k] and k not in orig and isinstance(ko.get(k), dict) and f in ko[k]:
                    # 本作業で追加したキーへのフィールド追加(ko の並び順を保つ)
                    order = list(ko[k])
                    merged = dict(jp[k]); merged[f] = v
                    jp[k] = {x: merged[x] for x in sorted(merged, key=lambda x: order.index(x) if x in order else 999)}
                    add += 1
                else:
                    skipped += 1
    for k in ko:
        if k in jp or k not in tr:
            continue
        order = list(ko[k]) if isinstance(ko[k], dict) else []
        fields = sorted(tr[k], key=lambda f: order.index(f) if f in order else 999)
        jp[k] = {f: tr[k][f] for f in fields}
        add += sum(1 for _ in fields)
    notin = [k for k in tr if k not in jp]
    # 追加キー(取り込み時に無かったキー)は複数回の適用をまたいでも ko の並び順に揃える
    added_keys = [k for k in ko if k in jp and k not in orig]
    jp = {**{k: jp[k] for k in orig}, **{k: jp[k] for k in added_keys}}
    assert list(jp)[:len(orig)] == list(orig)
    open(JP, "wb").write(json.dumps(jp, ensure_ascii=False, indent=2).encode("utf-8") + tail)
    print("%-30s 更新 %5d / 追加 %5d 文字列 (キー %d -> %d)%s%s" % (fn, upd, add, len(before), len(jp),
          " / 対象外 %d" % skipped if skipped else "", " / ko に無いキー %d" % len(notin) if notin else ""))
