# -*- coding: utf-8 -*-
"""数値テンプレート方式の汎用適用: python work/uifiles/apply_rules.py <データ名> <ルールJSON>

KO原文の数値(\\d+)を#に正規化してルールを引き、JAテンプレートの{}に数値を順に代入。
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")
HG = re.compile(r"[가-힯]")
NUM = re.compile(r"\d+")

def main():
    fn, rules_path = sys.argv[1], sys.argv[2]
    rules = {k: v for k, v in json.load(open(rules_path, encoding="utf-8")).items() if not k.startswith("_")}
    jp_path = os.path.join(ROOT, "json_weblate", "jp", fn + ".json")
    raw = open(jp_path, encoding="utf-8", newline="").read()
    tail = "\n" if raw.endswith("\n") else ""
    jp = json.loads(raw)
    assert json.dumps(jp, ensure_ascii=False, indent=2) + tail == raw, "RT不一致"
    shutil.copyfile(jp_path, os.path.join(ROOT, "work", "uifiles", fn + ".backup.json"))
    ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", fn + ".json"), encoding="utf-8"))
    en = json.load(open(os.path.join(ROOT, "json_weblate", "en", fn + ".json"), encoding="utf-8"))
    n = miss = bad = 0
    misses = []
    for k, v in jp.items():
        for f, s in list(v.items()):
            if not isinstance(s, str) or not s: continue
            if not (PH.search(s) or HG.search(s)): continue
            kn = ko.get(k, {}).get(f, "")
            if not isinstance(kn, str) or not kn or PH.search(kn):
                # KO が使えない場合は EN 原文で「EN::正規化キー」を引く
                e = en.get(k, {}).get(f, "")
                if not isinstance(e, str) or not e or PH.search(e): continue
                kn = e
                norm = "EN::" + NUM.sub("#", e)
            else:
                norm = NUM.sub("#", kn)
            tpl = rules.get(norm)
            if tpl is None:
                miss += 1; misses.append((k, f, norm[:60])); continue
            nums = NUM.findall(kn)
            if tpl.count("{}") != len(nums):
                bad += 1; misses.append(("SLOT!", k, norm[:50])); continue
            v[f] = tpl.format(*nums); n += 1
    print(f"{fn}: 適用 {n} / 未マッチ {miss} / スロット不一致 {bad}")
    for m in misses[:10]: print("  ", m)
    with open(jp_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(jp, ensure_ascii=False, indent=2) + tail)

if __name__ == "__main__":
    main()
