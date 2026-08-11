# -*- coding: utf-8 -*-
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"c:\Users\chro\Desktop\item"
new = json.load(open(BASE + r"\maplestory2-xml-itemname-ja.json", encoding="utf-8"))
old = json.load(open(BASE + r"\maplestory2-xml-itemname-ja.backup.json", encoding="utf-8"))
en = json.load(open(BASE + r"\maplestory2-xml-itemname-en.json", encoding="utf-8"))

assert list(new.keys()) == list(old.keys()), "key order changed!"
changed = 0
bad = []
for k in old:
    o, n = old[k], new[k]
    if o.get("class") != n.get("class"):
        bad.append(("class changed", k))
    if o.get("name", "") != n.get("name", ""):
        changed += 1
        if not o.get("name", "").startswith("ITEMNAME_"):
            bad.append(("non-placeholder changed", k, o.get("name", ""), n.get("name", "")))
        if n.get("name", "").startswith("ITEMNAME_"):
            bad.append(("still placeholder after change", k))

left = sum(1 for v in new.values() if v.get("name", "").startswith("ITEMNAME_"))
print(f"keys: {len(new)}, changed: {changed}, remaining ITEMNAME_: {left}")
print("problems:", bad if bad else "none")

# JA text sanity: no Hangul or Latin-only leftovers in changed names
import re
hangul = [ (k, new[k].get("name", "")) for k in old if old[k].get("name", "") != new[k].get("name", "") and re.search(r"[\uac00-\ud7af]", new[k].get("name", "")) ]
print("hangul leftovers:", hangul if hangul else "none")

print("\n--- samples ---")
SAMPLES = [
    ("Wizard's Antique Infernuke Claws Scroll", None),
    ("Archer's Tairen Combat Circlet", None),
    ("Tairen Officer All-in-One Box", None),
    ("Tairen Rensha Belt Fragment", None),
    ("Fire Prism Boots (Striker)", None),
    ("Fire Prism Top/Bottoms Selection Box Fragment", None),
    ("(PC Cafe) Elite Adventurer Stealth Mask (Thief)", None),
    ("08/01 Skin Entry (Female)", None),
    ("05/01 Skin Fame (M)", None),
    ("Showdown with Infernog S+ Rank Reward Box", None),
    ("Queen Bean Rumble Round 13 Reward Box", None),
    ("Title: Gentle Moonlight Groom", None),
    ("Sunlit Couple Title Selection Box", None),
    ("Epic Bonus Re-roller (Lv. 70/Two-handed)", None),
    ("Legendary Top/Bottoms Fragment Selection Box", None),
    ("Ascendant 2-Socket Conversion Scroll (Lv. 70)", None),
    ("Wedding Candy of Terror", None),
    ("Alberto Bean Car", None),
    ("Sexy Starfish Bikini (M)", None),
]
shown = set()
for want, _ in SAMPLES:
    for k, e in en.items():
        if e.get("name") == want and k in new and k not in shown:
            shown.add(k)
            print(f"  {want}\n    -> {new[k]['name']}")
            break

# KO-derived samples
ko = json.load(open(BASE + r"\maplestory2-xml-itemname-ko.json", encoding="utf-8"))
KO_SAMPLES = ["12/15 스킨 장갑 (남)", "샘플 무기 스킨 (홀) (캡슐 가챠 스킨)", "트라이아 궁중 셰프 전신 (여)",
              "(PC방) 엘리트 어드벤쳐 홀", "幽翼绯影腰带、披风箱", "便携式灭火器（女）"]
for want in KO_SAMPLES:
    for k, e in ko.items():
        if e.get("name") == want and k in new:
            print(f"  [KO] {want}\n    -> {new[k]['name']}")
            break

# what classes are in the 602 leftovers
import collections
cls = collections.Counter(v.get("class", "") for v in new.values() if v.get("name", "").startswith("ITEMNAME_"))
print("\nleftover classes:", dict(cls))
