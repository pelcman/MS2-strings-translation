# -*- coding: utf-8 -*-
"""釣り魚名46種(基本+景品=98エントリ)を fish_map.json (KO→JA) で翻訳して適用する。

- 対象: jp/itemname.json の name が「プレースホルダー」または「(景品) プレースホルダー」のエントリ
- KO の name((경품) 接頭辞を除去)をキーに fish_map.json を引く
- 適用前にバックアップとラウンドトリップ一致を検証、フォーマット(LF・indent=2・末尾改行)保全

使い方: python work/itemname/apply_fish.py
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JP = os.path.join(ROOT, "json_weblate", "jp", "itemname.json")
KO = os.path.join(ROOT, "json_weblate", "ko", "itemname.json")
BACKUP = os.path.join(ROOT, "work", "itemname", "itemname.backup.json")
MAP = os.path.join(ROOT, "work", "itemname", "fish_map.json")

PH = re.compile(r"^(\((?P<prefix>[^)]+)\) )?[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\].*)?$")

def dump(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"

def main():
    raw = open(JP, encoding="utf-8", newline="").read()
    jp = json.loads(raw)
    if dump(jp) != raw:
        print("NG: ラウンドトリップ不一致。フォーマットを確認してください。")
        sys.exit(1)
    print("OK: ラウンドトリップ一致")

    shutil.copyfile(JP, BACKUP)
    print(f"バックアップ: {BACKUP}")

    ko = json.load(open(KO, encoding="utf-8"))
    fish = {k: v for k, v in json.load(open(MAP, encoding="utf-8")).items()
            if not k.startswith("_")}

    changed, unmatched = 0, []
    for key, entry in jp.items():
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            continue
        m = PH.match(name)
        if not m:
            continue
        ko_name = ko.get(key, {}).get("name", "")
        ko_base = re.sub(r"^\(경품\) ", "", ko_name)
        if ko_base in fish:
            prize = ko_name != ko_base
            entry["name"] = ("(景品) " if prize else "") + fish[ko_base]
            changed += 1
        elif ko_name and not PH.match(ko_name):
            unmatched.append((key, name, ko_name))

    print(f"適用: {changed} エントリ")
    if unmatched:
        print(f"警告: KO実名ありでマップ未登録 {len(unmatched)} 件:")
        for k, n, kn in unmatched[:10]:
            print(" ", k, n[:40], "|", kn)

    with open(JP, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(jp))
    print(f"書き込み完了: {JP}")

if __name__ == "__main__":
    main()
