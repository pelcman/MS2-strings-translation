# 未翻訳エントリの包括監査(読み取り専用)
#   PYTHONIOENCODING=utf-8 python work/scripts/audit.py            # 全ファイルのサマリ
#   PYTHONIOENCODING=utf-8 python work/scripts/audit.py mapname    # 明細を表示
#
# 従来 status.py は「プレースホルダー形式」と「ハングル残存」の2種類しか見ておらず、
# 「未定」のような日本語のダミー値や、jp ファイルにキー自体が無いケースを見逃していた。
# ここでは 6 種類すべてを検出する。
import json, os, re, sys, glob, collections

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
JPD = os.path.join(ROOT, "json_weblate", "jp")

PH = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\].*)?$")
HAN = re.compile(r"[가-힣]")
JPC = re.compile(r"[ぁ-んァ-ヶ一-龥]")
CN = re.compile(r"[一-鿿]")
FILLER = {"未定", "未定義", "TBD", "(未翻訳)", "?", "-", "N/A"}
# KO 自体がダミー語の場合、JP の「未定」は正しい訳なので検出しない
KO_FILLER = {"미정", "테스트", "없음", "미정의"}

# 翻訳対象外のフィールド(AGENTS.md 準拠)
SKIP_FIELDS = {"npc", "type", "class", "regionID", "grade", "comment", "commnet",
               "isTutorial", "feature", "id"}

def skip(field):
    return field in SKIP_FIELDS or field.endswith("Kor")

def load(lang, fn):
    p = os.path.join(ROOT, "json_weblate", lang, fn + ".json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

REASONS = ["プレースホルダー", "ハングル残存", "ダミー値", "KO丸写し", "EN丸写し", "キー欠落"]

def audit(fn):
    jp, ko, en = load("jp", fn), load("ko", fn), load("en", fn)
    found = collections.defaultdict(list)

    for k, e in jp.items():
        if not isinstance(e, dict):
            continue
        for f, v in e.items():
            if skip(f) or not isinstance(v, str) or not v.strip():
                continue
            kv = ko.get(k, {}).get(f) if isinstance(ko.get(k), dict) else None
            ev = en.get(k, {}).get(f) if isinstance(en.get(k), dict) else None
            # KO に実体がある(ハングルを含み、かつダミー語そのものではない)
            src_ok = isinstance(kv, str) and bool(HAN.search(kv)) and kv.strip() not in KO_FILLER
            s = v.strip()
            if PH.match(s):
                found["プレースホルダー"].append((k, f, v, kv, ev))
            elif HAN.search(v):
                found["ハングル残存"].append((k, f, v, kv, ev))
            elif s in FILLER and src_ok:
                found["ダミー値"].append((k, f, v, kv, ev))
            elif src_ok and v == kv:
                found["KO丸写し"].append((k, f, v, kv, ev))
            elif src_ok and isinstance(ev, str) and v == ev and not JPC.search(v):
                found["EN丸写し"].append((k, f, v, kv, ev))

    # jp にキーが無く ko に実体があるもの
    for k, e in ko.items():
        if k in jp or not isinstance(e, dict):
            continue
        for f, v in e.items():
            if skip(f) or not isinstance(v, str) or not v.strip():
                continue
            if HAN.search(v) or CN.search(v):
                ev = en.get(k, {}).get(f) if isinstance(en.get(k), dict) else None
                found["キー欠落"].append((k, f, None, v, ev))
    return found

files = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(JPD, "*.json")))
detail = sys.argv[1] if len(sys.argv) > 1 else None

if detail:
    found = audit(detail)
    for r in REASONS:
        for k, f, v, kv, ev in found.get(r, []):
            print("[%s] %s | %s\n   JP: %s\n   KO: %s\n   EN: %s" %
                  (r, k, f, v, kv, ev))
    print("\n合計:", {r: len(found[r]) for r in REASONS if found[r]})
    sys.exit(0)

total = collections.Counter()
print("%-32s %8s %8s %7s %8s %8s %8s" %
      ("ファイル", "PH", "ハングル", "ダミー", "KO写し", "EN写し", "キー欠落"))
print("-" * 88)
for fn in files:
    found = audit(fn)
    n = [len(found[r]) for r in REASONS]
    if sum(n):
        print("%-32s %8d %8d %7d %8d %8d %8d" % (fn, *n))
        for r, c in zip(REASONS, n):
            total[r] += c
print("-" * 88)
print("%-32s %8d %8d %7d %8d %8d %8d" % ("合計", *[total[r] for r in REASONS]))
print("\n明細: python work/scripts/audit.py <ファイル名>")
