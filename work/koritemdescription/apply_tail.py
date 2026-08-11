# -*- coding: utf-8 -*-
"""koritemdescription の一点物(tail.txt の438種)を tail_ja.json で適用する。

使い方: python work/koritemdescription/apply_tail.py
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JP = os.path.join(ROOT, "json_weblate", "jp", "koritemdescription.json")
KO = os.path.join(ROOT, "json_weblate", "ko", "koritemdescription.json")
EN = os.path.join(ROOT, "json_weblate", "en", "koritemdescription.json")
WORK = os.path.join(ROOT, "work", "koritemdescription")
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")

def dump(d): return json.dumps(d, ensure_ascii=False, indent=2) + "\n"

def main():
    raw = open(JP, encoding="utf-8", newline="").read()
    jp = json.loads(raw)
    assert dump(jp) == raw, "ラウンドトリップ不一致"
    shutil.copyfile(JP, os.path.join(WORK, "koritemdescription.backup.json"))
    ko = json.load(open(KO, encoding="utf-8"))
    en = json.load(open(EN, encoding="utf-8"))

    srcs = {}
    n = None
    for line in open(os.path.join(WORK, "tail.txt"), encoding="utf-8"):
        if line.startswith("###"):
            n = line.split()[0][3:]
        elif line.startswith("KO|") and n:
            srcs[n] = line[3:].rstrip("\n").replace("⏎", "\n")
    ja = {k: v for k, v in json.load(
        open(os.path.join(WORK, "tail_ja.json"), encoding="utf-8")).items() if not k.startswith("_")}
    missing = set(srcs) - set(ja)
    assert not missing, f"tail_ja.json に欠番: {sorted(missing, key=int)[:10]}"
    src2ja = {}
    for num, src in srcs.items():
        src2ja[src] = ja[num]

    changed = 0
    leftover = []
    for key, entry in jp.items():
        kv = ko.get(key, {}); ev = en.get(key, {})
        for f in ("tooltipDescription", "guideDescription"):
            s = entry.get(f)
            if not isinstance(s, str) or not s or not PH.search(s): continue
            src = kv.get(f, "")
            k_ok = isinstance(src, str) and bool(src) and not PH.search(src)
            e = ev.get(f, "")
            e_ok = isinstance(e, str) and bool(e) and not PH.search(e)
            lookup = src if k_ok else ("EN::" + e if e_ok else None)
            if lookup is None: continue
            if lookup in src2ja:
                entry[f] = src2ja[lookup]; changed += 1
            else:
                leftover.append((key, f, (src or e)[:50]))

    print(f"適用: {changed} 文字列 (期待528)")
    if leftover:
        print("未適用の翻訳可能文字列:", len(leftover))
        for l in leftover[:10]: print("  ", l)
    with open(JP, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dump(jp))
    print("書き込み完了")

if __name__ == "__main__":
    main()
