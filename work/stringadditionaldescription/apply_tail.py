# -*- coding: utf-8 -*-
"""stringadditionaldescription の残り(608種/686文字列)を tail_rules.json で適用する。

- KO原文の数値(\\d+(?:\\.\\d+)?)を # に正規化してルールを引き、JAテンプレートの {} に
  数値を順番に代入する(FONTカラーコードの数字部分も同じ仕組みで復元)
- name / tooltipDescription 両フィールド対象

使い方: python work/stringadditionaldescription/apply_tail.py
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JP = os.path.join(ROOT, "json_weblate", "jp", "stringadditionaldescription.json")
KO = os.path.join(ROOT, "json_weblate", "ko", "stringadditionaldescription.json")
EN = os.path.join(ROOT, "json_weblate", "en", "stringadditionaldescription.json")
WORK = os.path.join(ROOT, "work", "stringadditionaldescription")
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")
NUM = re.compile(r"\d+(?:\.\d+)?")

def main():
    raw = open(JP, encoding="utf-8", newline="").read()
    tail_nl = "\n" if raw.endswith("\n") else ""
    dump = lambda d: json.dumps(d, ensure_ascii=False, indent=2) + tail_nl
    jp = json.loads(raw)
    assert dump(jp) == raw, "ラウンドトリップ不一致"
    shutil.copyfile(JP, os.path.join(WORK, "stringadditionaldescription.backup.json"))
    ko = json.load(open(KO, encoding="utf-8"))
    en = json.load(open(EN, encoding="utf-8"))
    rules = {k: v for k, v in json.load(
        open(os.path.join(WORK, "tail_rules.json"), encoding="utf-8")).items() if not k.startswith("_")}

    changed, unmatched, badfmt = 0, [], []
    for key, entry in jp.items():
        kv = ko.get(key, {}); ev = en.get(key, {})
        for f in ("name", "tooltipDescription"):
            s = entry.get(f)
            if not isinstance(s, str) or not s or not PH.search(s): continue
            src = kv.get(f, "")
            k_ok = isinstance(src, str) and bool(src) and not PH.search(src)
            if not k_ok:
                e = ev.get(f, "")
                if isinstance(e, str) and e and not PH.search(e):
                    unmatched.append((key, f, "EN-only: " + e[:40]))
                continue
            norm = NUM.sub("#", src)
            tpl = rules.get(norm)
            if tpl is None:
                unmatched.append((key, f, src[:50]))
                continue
            nums = NUM.findall(src)
            if tpl.count("{}") != len(nums):
                badfmt.append((key, f, norm[:40], tpl.count("{}"), len(nums)))
                continue
            entry[f] = tpl.format(*nums)
            changed += 1

    print(f"適用: {changed} 文字列 (期待686前後)")
    if badfmt:
        print("！スロット数不一致:", len(badfmt))
        for b in badfmt[:8]: print("  ", b)
    if unmatched:
        print("未マッチ:", len(unmatched))
        for u in unmatched[:10]: print("  ", u)
    with open(JP, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dump(jp))
    print("書き込み完了")

if __name__ == "__main__":
    main()
