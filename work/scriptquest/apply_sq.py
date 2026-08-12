# scriptquest 適用スクリプト
# targets.json の未翻訳エントリ(name欄プレースホルダー)に対し、
# TM (tm_self/tm_cross) → sq_map*.json (KO原文→JA) の順で訳を適用する。
# 実行前バックアップ・フォーマット保存(LF・末尾改行)・適用/残り件数レポート付き。
import json, glob, os, shutil, re

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", ".."))
JP = os.path.join(ROOT, "json_weblate", "jp", "scriptquest.json")
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")

def load(p):
    return json.load(open(p, encoding="utf-8"))

targets = load(os.path.join(BASE, "targets.json"))["targets"]
tm = {}
for name in ["tm_cross.json", "tm_self.json"]:  # self を後勝ちで優先
    p = os.path.join(BASE, name)
    if os.path.exists(p):
        tm.update(load(p))
maps = {}
for p in sorted(glob.glob(os.path.join(BASE, "sq_*.json"))):   # sq_map* と sq_kri* の両方
    m = load(p)
    m.pop("_comment", None)
    maps.update(m)

raw = open(JP, "rb").read()
tail = b"\n" if raw.endswith(b"\n") else b""
jp = json.loads(raw.decode("utf-8"))

rt = (json.dumps(jp, ensure_ascii=False, indent=2) + tail.decode()).encode("utf-8")
assert rt == raw, "roundtrip mismatch — フォーマット不一致"

bk = os.path.join(BASE, "scriptquest.backup.json")
if not os.path.exists(bk):          # 初回のみ原本を保存
    shutil.copyfile(JP, bk)
shutil.copyfile(JP, os.path.join(BASE, "scriptquest.prev.json"))

applied = 0
remain = []
for k, (kov, env) in targets.items():
    cur = jp[k].get("name")
    if not (isinstance(cur, str) and PH.search(cur)):
        continue                     # 適用済み
    ja = maps.get(kov) or tm.get(kov)
    if ja:
        jp[k]["name"] = ja
        applied += 1
    else:
        remain.append(k)

with open(JP, "wb") as fh:
    fh.write(json.dumps(jp, ensure_ascii=False, indent=2).encode("utf-8") + tail)

uniq = {}
for k in remain:
    uniq.setdefault(targets[k][0], []).append(k)
print(f"適用: {applied} / 残り: {len(remain)} (ユニーク {len(uniq)})")
