# -*- coding: utf-8 -*-
"""koritemdescription の頻度3以上の定型文76種(1,287文字列)を適用する。

- freq3plus.txt の ###n ↔ KO原文 の対応を読み、freq3plus_ja.json の n → JA を引く
- jp 側がプレースホルダーのフィールドのみ、ko 側が KO原文と完全一致する場合に置換
- バックアップ+ラウンドトリップ検証+フォーマット保全

使い方: python work/koritemdescription/apply_freq3.py
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JP = os.path.join(ROOT, "json_weblate", "jp", "koritemdescription.json")
KO = os.path.join(ROOT, "json_weblate", "ko", "koritemdescription.json")
WORK = os.path.join(ROOT, "work", "koritemdescription")
BACKUP = os.path.join(WORK, "koritemdescription.backup.json")

PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")

def dump(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"

def load_sources():
    """freq3plus.txt から ###n → KO原文 を復元する(⏎は実改行に戻す)"""
    srcs = {}
    n = None
    for line in open(os.path.join(WORK, "freq3plus.txt"), encoding="utf-8"):
        if line.startswith("###"):
            n = line.split()[0][3:]
        elif line.startswith("KO|") and n is not None:
            srcs[n] = line[3:].rstrip("\n").replace("⏎", "\n")
    return srcs

def main():
    raw = open(JP, encoding="utf-8", newline="").read()
    jp = json.loads(raw)
    if dump(jp) != raw:
        print("NG: ラウンドトリップ不一致")
        sys.exit(1)
    print("OK: ラウンドトリップ一致")
    shutil.copyfile(JP, BACKUP)

    ko = json.load(open(KO, encoding="utf-8"))
    ja_map = {k: v for k, v in json.load(
        open(os.path.join(WORK, "freq3plus_ja.json"), encoding="utf-8")).items()
        if not k.startswith("_")}
    srcs = load_sources()
    assert set(srcs) == set(ja_map), f"番号の不一致: {set(srcs) ^ set(ja_map)}"
    src2ja = {srcs[n]: ja_map[n] for n in srcs}

    changed = 0
    for key, entry in jp.items():
        kv = ko.get(key, {})
        for f in ("tooltipDescription", "guideDescription"):
            s = entry.get(f)
            if not isinstance(s, str) or not s or not PH.search(s):
                continue
            src = kv.get(f, "")
            if src in src2ja:
                entry[f] = src2ja[src]
                changed += 1

    print(f"適用: {changed} 文字列 (期待1287)")
    with open(JP, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(jp))
    print(f"書き込み完了: {JP}")

if __name__ == "__main__":
    main()
