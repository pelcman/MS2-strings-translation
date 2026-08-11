# stringtrigger 適用スクリプト
# targets.json の未翻訳エントリ(name欄プレースホルダー)に対し、
# TM (tm_self/tm_cross) → st_map*.json (KO原文→JA) の順で訳を適用する。
# 実行前バックアップ・フォーマット保存(LF・末尾改行)・適用/残り件数レポート付き。
import json, glob, os, shutil, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", ".."))
JP = os.path.join(ROOT, "json_weblate", "jp", "stringtrigger.json")

def load(p):
    return json.load(open(p, encoding="utf-8"))

targets = load(os.path.join(BASE, "targets.json"))["targets"]
tm = {}
for name in ["tm_cross.json", "tm_self.json"]:  # self を後勝ちで優先
    p = os.path.join(BASE, name)
    if os.path.exists(p):
        tm.update(load(p))
maps = {}
for p in sorted(glob.glob(os.path.join(BASE, "st_map*.json"))):
    m = load(p)
    m.pop("_comment", None)
    maps.update(m)

raw = open(JP, "rb").read()
tail = b"\n" if raw.endswith(b"\n") else b""
jp = json.loads(raw.decode("utf-8"))

# ラウンドトリップ検証
rt = (json.dumps(jp, ensure_ascii=False, indent=2) + tail.decode()).encode("utf-8")
assert rt == raw, "roundtrip mismatch — フォーマット不一致"

shutil.copyfile(JP, os.path.join(BASE, "stringtrigger.backup.json"))

PH = re.compile(r"^[A-Z0-9$_]+(:\[F\]\S*)?$")
applied = 0
remain = []
for k, (kov, env) in targets.items():
    cur = jp[k].get("name")
    if not (isinstance(cur, str) and PH.match(cur) and "_" in cur):
        continue  # 適用済み
    ja = maps.get(kov) or tm.get(kov)
    if ja:
        jp[k]["name"] = ja
        applied += 1
    else:
        remain.append(k)

with open(JP, "wb") as fh:
    fh.write((json.dumps(jp, ensure_ascii=False, indent=2)).encode("utf-8") + tail)

print(f"適用: {applied} / 残り: {len(remain)}")
uniq = {}
for k in remain:
    uniq.setdefault(targets[k][0], []).append(k)
print(f"残りユニークKO: {len(uniq)}")
json.dump(
    {ko: {"en": targets[keys[0]][1], "keys": keys} for ko, keys in uniq.items()},
    open(os.path.join(BASE, "remaining.json"), "w", encoding="utf-8"),
    ensure_ascii=False, indent=1,
)
