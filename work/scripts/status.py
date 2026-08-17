# -*- coding: utf-8 -*-
"""翻訳進捗テーブル(Markdown)を出力する。README.md の表の再生成用。

  python work/scripts/status.py

- 残り   = 未翻訳(プレースホルダー/ハングル残存)のうち KO/EN いずれかに実文があるもの
- 欠落   = ko に実文があるのに jp にキーが無いもの
           (Weblate 上に翻訳枠が存在しないため、キーを追加しないと翻訳できない。
            2026-08 のセッションで全件補完した)
- 残置   = 全言語プレースホルダーのみ(翻訳元が存在しない。方針により残す)
- 対象外フィールド: comment/commend/commnet/isTutorial、addressname の *Kor、
  stringcommon の desc、maidmanufacturemessage の npc(JMS2 でも韓国語のままの内部ラベル)、
  stringtrigger/scriptquest の npc・type(話者IDとトリガー関数名。JP・EN とも原文のまま)

注意: 以前は「jp に存在するキー」だけを数えていたため、jp にキーが無いものが
集計から丸ごと漏れ、実際には未カバーのファイルが「完了」と表示されていた。
"""
import json, re, sys, io, glob, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")
HG = re.compile(r"[가-힯]")
EXCL_FIELDS = {"comment", "commend", "commnet", "isTutorial"}
# 文字集めイベントのアイテム(1文字ずつ集めて文章にするもの)は翻訳せず原文を維持する
LETTER_TILES = {"30001309-ItemKR-", "30001310-ItemKR-", "30001311-ItemKR-", "30001312-ItemKR-",
                "30001314-ItemKR-", "30001315-ItemKR-", "30001316-ItemKR-", "30001317-ItemKR-",
                "30001318-ItemKR-", "30001319-ItemKR-", "30001320-ItemKR-"}

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
                if fn in ("stringtrigger", "scriptquest") and f in ("npc", "type"):
                    continue
                if fn == "itemname" and k in LETTER_TILES:
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
        # ko にあって jp にキーが無いもの(翻訳枠そのものが存在しない)
        miss = 0
        for k, v in ko.items():
            if k in jp or not isinstance(v, dict):
                continue
            for f, s in v.items():
                if not isinstance(s, str) or not s.strip() or f in EXCL_FIELDS:
                    continue
                if fn == "addressname" and f.endswith("Kor"):
                    continue
                if fn == "stringcommon" and f == "desc":
                    continue
                if fn == "maidmanufacturemessage" and f == "npc":
                    continue
                if fn in ("stringtrigger", "scriptquest") and f in ("npc", "type"):
                    continue
                if HG.search(s) or re.search(r"[一-鿿]", s):
                    miss += 1
        rows.append((fn, total, rest, nosrc, miss))
    print("| ファイル | 対象フィールド | 残り | 欠落キー | 残置(源無し) | 状態 |")
    print("|---|---:|---:|---:|---:|---|")
    for fn, total, rest, nosrc, miss in rows:
        st = "✅ 完了" if rest == 0 and miss == 0 else f"🔄 残り{rest + miss:,}"
        print(f"| {fn} | {total:,} | {rest:,} | {miss:,} | {nosrc} | {st} |")
    print()
    print(f"合計 残り: {sum(r[2] for r in rows):,} / 欠落キー: {sum(r[4] for r in rows):,} "
          f"/ 残置: {sum(r[3] for r in rows):,}")

if __name__ == "__main__":
    main()
