# -*- coding: utf-8 -*-
"""釣り魚詳細説明文46種(98エントリ)を fishdesc_map.json で翻訳して適用する。

- 対象: jp/koritemdescription.json の tooltipDescription が
  STRINGFISHDETAILDESC_<ID>_NAME:[F]... 形式のエントリ
- マップキーは <ID>。適用前バックアップ+ラウンドトリップ検証+フォーマット保全。

使い方: python work/itemname/apply_fishdesc.py
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JP = os.path.join(ROOT, "json_weblate", "jp", "koritemdescription.json")
BACKUP = os.path.join(ROOT, "work", "itemname", "koritemdescription.backup.json")
MAP = os.path.join(ROOT, "work", "itemname", "fishdesc_map.json")

PH = re.compile(r"^STRINGFISHDETAILDESC_(\d+)_NAME(:\[F\].*)?$")

def dump(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"

def main():
    raw = open(JP, encoding="utf-8", newline="").read()
    jp = json.loads(raw)
    if dump(jp) != raw:
        print("NG: ラウンドトリップ不一致")
        sys.exit(1)
    print("OK: ラウンドトリップ一致")

    shutil.copyfile(JP, BACKUP)
    print(f"バックアップ: {BACKUP}")

    m = {k: v for k, v in json.load(open(MAP, encoding="utf-8")).items()
         if not k.startswith("_")}
    for v in m.values():
        assert "\\n" in v and "\n" not in v, "改行はリテラル\\nで書くこと"

    changed, missing = 0, []
    for key, entry in jp.items():
        s = entry.get("tooltipDescription")
        if not isinstance(s, str):
            continue
        mo = PH.match(s)
        if not mo:
            continue
        fid = mo.group(1)
        if fid in m:
            entry["tooltipDescription"] = m[fid]
            changed += 1
        else:
            missing.append((key, fid))

    print(f"適用: {changed} エントリ")
    if missing:
        print(f"警告: マップ未登録 {len(missing)} 件: {missing[:5]}")

    with open(JP, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(jp))
    print(f"書き込み完了: {JP}")

if __name__ == "__main__":
    main()
