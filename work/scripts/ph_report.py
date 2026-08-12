# プレースホルダー未訳のうち「翻訳元が存在するもの」を数える(読み取り専用)
#   PYTHONIOENCODING=utf-8 python work/scripts/ph_report.py          # ファイル別集計
#   PYTHONIOENCODING=utf-8 python work/scripts/ph_report.py mapname  # 明細
# AGENTS.md 方針4「全言語で未翻訳のものは訳さない」に従い、
# ko/en どちらにも実体が無いものは「訳元なし」として除外する。
import json, os, re, sys, glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PH = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\].*)?$")
HAN = re.compile(r"[가-힣]")
CN = re.compile(r"[一-鿿]")
LAT = re.compile(r"[A-Za-z]")
SKIP = {"npc", "type", "class", "regionID", "grade", "comment", "commnet", "isTutorial"}


def has_source(kv, ev):
    if isinstance(kv, str) and kv.strip() and not PH.match(kv.strip()) and (HAN.search(kv) or CN.search(kv)):
        return True
    if isinstance(ev, str) and ev.strip() and not PH.match(ev.strip()) and LAT.search(ev):
        return True
    return False


def scan(fn):
    jp = json.load(open(os.path.join(ROOT, "json_weblate", "jp", fn + ".json"), encoding="utf-8"))
    def side(lang):
        p = os.path.join(ROOT, "json_weblate", lang, fn + ".json")
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    ko, en = side("ko"), side("en")
    ok, ng = [], 0
    for k, e in jp.items():
        if not isinstance(e, dict):
            continue
        for f, v in e.items():
            if f in SKIP or f.endswith("Kor") or not isinstance(v, str):
                continue
            if not PH.match(v.strip()):
                continue
            kv = ko.get(k, {}).get(f) if isinstance(ko.get(k), dict) else None
            ev = en.get(k, {}).get(f) if isinstance(en.get(k), dict) else None
            if has_source(kv, ev):
                ok.append((k, f, kv, ev))
            else:
                ng += 1
    return ok, ng


if len(sys.argv) > 1:
    ok, ng = scan(sys.argv[1])
    for k, f, kv, ev in ok:
        print("%s | %s\n   KO: %s\n   EN: %s" % (k, f, kv, ev))
    print("\n訳せる %d / 訳元なし %d" % (len(ok), ng))
    sys.exit(0)

total = 0
for p in sorted(glob.glob(os.path.join(ROOT, "json_weblate", "jp", "*.json"))):
    fn = os.path.basename(p)[:-5]
    ok, ng = scan(fn)
    if ok:
        print("%-32s 訳せる %5d   訳元なし %5d" % (fn, len(ok), ng))
        total += len(ok)
print("-" * 58)
print("%-32s 訳せる %5d" % ("合計", total))
