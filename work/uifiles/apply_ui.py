# -*- coding: utf-8 -*-
"""UI系ファイル汎用適用: python work/uifiles/apply_ui.py <データ名> <マップJSON>

jp側がプレースホルダー/ハングル残存のフィールドについて、
KO原文(なければEN)がマップに完全一致すれば置換する。
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")
HG = re.compile(r"[가-힯]")

def main():
    fn, map_path = sys.argv[1], sys.argv[2]
    M = {k: v for k, v in json.load(open(map_path, encoding="utf-8")).items() if not k.startswith("_")}
    jp_path = os.path.join(ROOT, "json_weblate", "jp", fn + ".json")
    raw = open(jp_path, encoding="utf-8", newline="").read()
    tail = "\n" if raw.endswith("\n") else ""
    jp = json.loads(raw)
    assert json.dumps(jp, ensure_ascii=False, indent=2) + tail == raw, "RT不一致"
    shutil.copyfile(jp_path, os.path.join(ROOT, "work", "uifiles", fn + ".backup.json"))
    ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", fn + ".json"), encoding="utf-8"))
    en = json.load(open(os.path.join(ROOT, "json_weblate", "en", fn + ".json"), encoding="utf-8"))
    n = miss = 0
    misses = []
    for k, v in jp.items():
        for f, s in list(v.items()):
            if not isinstance(s, str) or not s: continue
            if not (PH.search(s) or HG.search(s)): continue
            kn = ko.get(k, {}).get(f, ""); e = en.get(k, {}).get(f, "")
            src = None
            if isinstance(kn, str) and kn and not PH.search(kn) and kn != s: src = kn
            elif isinstance(e, str) and e and not PH.search(e) and e != s: src = "EN::" + e
            if src is None: continue
            if src in M:
                v[f] = M[src]; n += 1
            else:
                miss += 1; misses.append((k, f, src[:60]))
    print(f"{fn}: 適用 {n} / 未マッチ {miss}")
    for m in misses[:8]: print("  ", m)
    with open(jp_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(jp, ensure_ascii=False, indent=2) + tail)

if __name__ == "__main__":
    main()
