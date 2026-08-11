# -*- coding: utf-8 -*-
"""skillname.json のプレースホルダー144件を skillname_ja.json (キー→JA) で適用する。

使い方: python work/skillname/apply_skillname.py
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JP = os.path.join(ROOT, "json_weblate", "jp", "skillname.json")
WORK = os.path.join(ROOT, "work", "skillname")
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")

def main():
    raw = open(JP, encoding="utf-8", newline="").read()
    # skillname.json は末尾改行なし。元ファイルのフォーマットに追従する
    tail_nl = "\n" if raw.endswith("\n") else ""
    dump = lambda d: json.dumps(d, ensure_ascii=False, indent=2) + tail_nl
    jp = json.loads(raw)
    assert dump(jp) == raw, "ラウンドトリップ不一致"
    shutil.copyfile(JP, os.path.join(WORK, "skillname.backup.json"))
    ja = {k: v for k, v in json.load(
        open(os.path.join(WORK, "skillname_ja.json"), encoding="utf-8")).items() if not k.startswith("_")}

    changed = 0
    for key, val in ja.items():
        assert key in jp, f"キーが存在しない: {key}"
        s = jp[key].get("name", "")
        assert isinstance(s, str) and PH.search(s), f"プレースホルダーでない: {key} = {s[:40]}"
        jp[key]["name"] = val
        changed += 1
    left = sum(1 for v in jp.values() if isinstance(v.get("name"), str) and v["name"] and PH.search(v["name"]))
    print(f"適用: {changed} 件 / 残プレースホルダー: {left} (期待14)")
    with open(JP, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dump(jp))
    print("書き込み完了")

if __name__ == "__main__":
    main()
