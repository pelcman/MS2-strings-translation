# 欠落キーの訳を jp JSON へ追加する
#   PYTHONIOENCODING=utf-8 python work/scripts/apply_missing.py mapname
# 入力: work/missing/<file>.ja.tsv   1行 = キー \t フィールド \t 日本語訳
# 既存キーの内容と順序は一切変更せず、新規キーを ko の順序でファイル末尾に追加する。
# 追加前に work/missing/<file>.backup.json を作成する。
import json, os, re, shutil, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MIS = os.path.join(ROOT, "work", "missing")
HAN = re.compile(r"[가-힣]")

fn = sys.argv[1]
JP = os.path.join(ROOT, "json_weblate", "jp", fn + ".json")
raw = open(JP, "rb").read()
tail = b"\n" if raw.endswith(b"\n") else b""
jp = json.loads(raw.decode("utf-8"))
assert (json.dumps(jp, ensure_ascii=False, indent=2) + tail.decode()).encode("utf-8") == raw, \
    "roundtrip mismatch — フォーマット不一致"

ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", fn + ".json"), encoding="utf-8"))
before = list(jp)

bk = os.path.join(MIS, fn + ".backup.json")
if not os.path.exists(bk):
    shutil.copyfile(JP, bk)

trans = {}
for line in open(os.path.join(MIS, fn + ".ja.tsv"), encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip():
        continue
    k, f, ja = line.split("\t", 2)
    ja = ja.replace("⏎", "\n")
    assert not HAN.search(ja), "ハングル残存: " + k
    trans.setdefault(k, {})[f] = ja

added = 0
for k in ko:                      # ko の並び順で追加
    if k in jp or k not in trans:
        continue
    jp[k] = dict(trans[k])
    added += 1

assert list(jp)[:len(before)] == before, "既存キーの順序が変わった"
open(JP, "wb").write(json.dumps(jp, ensure_ascii=False, indent=2).encode("utf-8") + tail)
print("%s: %d キー追加 (%d -> %d)" % (fn, added, len(before), len(jp)))
missing = [k for k in trans if k not in jp]
if missing:
    print("  ※ ko に無く追加できなかったキー:", missing[:5])
