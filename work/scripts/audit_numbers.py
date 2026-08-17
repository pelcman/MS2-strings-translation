# 補完したエントリで KO と JA の数値が食い違うものを検出する(読み取り専用)
#   PYTHONIOENCODING=utf-8 python work/scripts/audit_numbers.py
#
# ワーカーが「数字を # に正規化したテンプレート照合」で既訳を流用した結果、
# 別の回数・分数がそのまま入ってしまう事故があった(例: KO 10분 → JA 30分間)。
# タグ内の ID は比較対象から除外し、本文中の数値だけを比較する。
import json, os, re, glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MIS = os.path.join(ROOT, "work", "missing")
TAG = re.compile(r"\$[A-Za-z]+:[^$]*\$|\$MyPCName\$|<[^>]*>|\[\[?[a-z]+:[^\]]*\]\]?")
NUM = re.compile(r"\d+")
SKIP = {"npc", "type", "class", "regionID", "grade", "comment", "commnet", "isTutorial"}


def nums(s):
    return NUM.findall(TAG.sub(" ", s))


hits = []
for p in sorted(glob.glob(os.path.join(ROOT, "json_weblate", "jp", "*.json"))):
    fn = os.path.basename(p)[:-5]
    kp = os.path.join(ROOT, "json_weblate", "ko", fn + ".json")
    if not os.path.exists(kp):
        continue
    jp = json.load(open(p, encoding="utf-8"))
    ko = json.load(open(kp, encoding="utf-8"))
    bk = os.path.join(MIS, fn + ".backup.json")
    base = json.load(open(bk, encoding="utf-8")) if os.path.exists(bk) else {}
    for k, e in jp.items():
        ke = ko.get(k)
        if not isinstance(e, dict) or not isinstance(ke, dict):
            continue
        for f, v in e.items():
            kv = ke.get(f)
            if f in SKIP or f.endswith("Kor"):
                continue
            if not isinstance(v, str) or not isinstance(kv, str):
                continue
            if not kv.strip() or not v.strip():
                continue
            a, b = nums(kv), nums(v)
            # 個数が同じなのに値が違う = 別の数値に差し替わった可能性が高い。
            # 個数自体が違うのは言い回しの差(「3回」→「3度」など)が多いので除く。
            if len(a) != len(b) or a == b:
                continue
            new = bool(base) and k not in base
            if not new:
                continue          # 補完で追加したキーのみ対象
            hits.append((fn, k, f, kv, v, new))

print("KO と JA で数値が異なるエントリ: %d 件" % len(hits))
print("(うち今回の補完で追加したキー: %d 件)" % sum(1 for h in hits if h[5]))
for fn, k, f, kv, v, new in hits[:40]:
    mark = "★補完" if new else "既存"
    print("  %-6s %-22s %-26s KO:%-34s JA:%s" %
          (mark, fn[:22], k[:26], kv.replace("\n", " ")[:34], v.replace("\n", " ")[:34]))
