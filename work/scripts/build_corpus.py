# -*- coding: utf-8 -*-
"""dict/corpus/itemname-pairs.tsv を再生成する。
データファイル(json_weblate/{jp,en,ko}/itemname.json)を更新したら実行すること。

使い方: python work/scripts/build_corpus.py
"""
import json, os, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 例: ITEMNAME_10000041_NAME:[F]Fishing02 / ITEMNAME_20001133_NAME (接尾辞なし)
PLACEHOLDER = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\].*)?$")

def load(lang):
    with open(os.path.join(ROOT, "json_weblate", lang, "itemname.json"), encoding="utf-8") as f:
        return json.load(f)

def main():
    ja, en, ko = load("jp"), load("en"), load("ko")
    rows, seen = [], set()
    for key, j in ja.items():
        ja_name = j.get("name", "")
        if not ja_name or PLACEHOLDER.match(ja_name):
            continue
        en_name = en.get(key, {}).get("name", "")
        ko_name = ko.get(key, {}).get("name", "")
        if PLACEHOLDER.match(en_name):
            en_name = ""
        if PLACEHOLDER.match(ko_name):
            ko_name = ""
        r = (en_name, ko_name, ja_name, j.get("class", ""), key)
        if r[:3] not in seen:
            seen.add(r[:3])
            rows.append(r)

    out = os.path.join(ROOT, "dict", "corpus", "itemname-pairs.tsv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write("en\tko\tja\tclass\tkey\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(f"written: {out} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
