# -*- coding: utf-8 -*-
"""翻訳進捗テーブル(Markdown)を出力する。README.md の表の再生成用。

  python work/scripts/status.py

- 残り   = 未翻訳(プレースホルダー/ハングル残存)のうち KO/EN いずれかに実文があるもの
- 残置   = 全言語プレースホルダーのみ(翻訳元が存在しない。方針により残す)
- 対象外フィールド: comment/commend/commnet/isTutorial、addressname の *Kor、
  stringcommon の desc、maidmanufacturemessage の npc(JMS2 でも韓国語のままの内部ラベル)
"""
import json, re, sys, io, glob, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")
HG = re.compile(r"[가-힯]")
EXCL_FIELDS = {"comment", "commend", "commnet", "isTutorial"}

def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, "json_weblate", "jp", "*.json"))):
        fn = os.path.basename(path)[:-5]
        jp = json.load(open(path, encoding="utf-8"))
        def load(lang):
            p = os.path.join(ROOT, "json_weblate", lang, fn + ".json")
            return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        ko, en = load("ko"), load("en")
        total = rest = nosrc = 0
        for k, v in jp.items():
            if not isinstance(v, dict):
                continue
            for f, s in v.items():
                if not isinstance(s, str) or not s or f in EXCL_FIELDS:
                    continue
                if fn == "addressname" and f.endswith("Kor"):
                    continue
                if fn == "stringcommon" and f == "desc":
                    continue
                if fn == "maidmanufacturemessage" and f == "npc":
                    continue
                total += 1
                if not (PH.search(s) or HG.search(s)):
                    continue
                kn = ko.get(k, {}).get(f, "")
                e = en.get(k, {}).get(f, "")
                if (isinstance(kn, str) and kn and not PH.search(kn)) or \
                   (isinstance(e, str) and e and not PH.search(e)):
                    rest += 1
                else:
                    nosrc += 1
        rows.append((fn, total, rest, nosrc))
    print("| ファイル | 対象フィールド | 残り | 残置(源無し) | 状態 |")
    print("|---|---:|---:|---:|---|")
    for fn, total, rest, nosrc in rows:
        st = "✅ 完了" if rest == 0 else f"🔄 残り{rest:,}"
        print(f"| {fn} | {total:,} | {rest:,} | {nosrc} | {st} |")
    print()
    print(f"合計 残り: {sum(r[2] for r in rows):,} / 残置: {sum(r[3] for r in rows):,}")

if __name__ == "__main__":
    main()
