# -*- coding: utf-8 -*-
"""stringadditionaldescription の頻度3以上175種(約2,499文字列)を適用する。

- freq3plus.txt の ###n(field付き) ↔ KO原文 と freq3plus_ja.json の n → JA を突合
- jp側がプレースホルダーのフィールドのみ、ko側(無ければen)完全一致で置換

使い方: python work/stringadditionaldescription/apply_freq3.py
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JP = os.path.join(ROOT, "json_weblate", "jp", "stringadditionaldescription.json")
KO = os.path.join(ROOT, "json_weblate", "ko", "stringadditionaldescription.json")
EN = os.path.join(ROOT, "json_weblate", "en", "stringadditionaldescription.json")
WORK = os.path.join(ROOT, "work", "stringadditionaldescription")
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")

def main():
    raw = open(JP, encoding="utf-8", newline="").read()
    tail_nl = "\n" if raw.endswith("\n") else ""
    dump = lambda d: json.dumps(d, ensure_ascii=False, indent=2) + tail_nl
    jp = json.loads(raw)
    assert dump(jp) == raw, "ラウンドトリップ不一致"
    shutil.copyfile(JP, os.path.join(WORK, "stringadditionaldescription.backup.json"))
    ko = json.load(open(KO, encoding="utf-8"))
    en = json.load(open(EN, encoding="utf-8"))

    srcs = {}
    n = field = None
    for line in open(os.path.join(WORK, "freq3plus.txt"), encoding="utf-8"):
        if line.startswith("###"):
            n = line.split()[0][3:]
            m = re.search(r"field=(\S+)", line)
            field = m.group(1)
        elif line.startswith("KO|") and n:
            srcs[n] = (field, line[3:].rstrip("\n").replace("⏎", "\n"))
    ja = {k: v for k, v in json.load(
        open(os.path.join(WORK, "freq3plus_ja.json"), encoding="utf-8")).items() if not k.startswith("_")}
    assert set(srcs) == set(ja), f"番号不一致: {set(srcs) ^ set(ja)}"
    src2ja = {srcs[k]: ja[k] for k in srcs}

    changed = 0
    for key, entry in jp.items():
        kv = ko.get(key, {})
        for f in ("name", "tooltipDescription"):
            s = entry.get(f)
            if not isinstance(s, str) or not s or not PH.search(s): continue
            src = kv.get(f, "")
            if not isinstance(src, str) or not src or PH.search(src): continue
            if (f, src) in src2ja:
                entry[f] = src2ja[(f, src)]
                changed += 1

    print(f"適用: {changed} 文字列 (期待~2,499)")
    with open(JP, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dump(jp))
    print("書き込み完了")

if __name__ == "__main__":
    main()
