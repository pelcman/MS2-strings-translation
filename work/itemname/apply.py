# -*- coding: utf-8 -*-
"""Apply EN/KO -> JA translations to the untranslated (ITEMNAME_*) entries of the ja file."""
import json, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SC = r"C:\Users\chro\AppData\Local\Temp\claude\c--Users-chro-Desktop-item\716449ef-c413-4587-8ba3-40dde686df10\scratchpad"
BASE = r"c:\Users\chro\Desktop\item"
JA_PATH = BASE + r"\maplestory2-xml-itemname-ja.json"

with open(JA_PATH, encoding="utf-8") as f:
    ja_text = f.read()
ja = json.loads(ja_text)
en = json.load(open(BASE + r"\maplestory2-xml-itemname-en.json", encoding="utf-8"))
ko = json.load(open(BASE + r"\maplestory2-xml-itemname-ko.json", encoding="utf-8"))

auto_map = json.load(open(SC + r"\auto_map.json", encoding="utf-8"))
manual_en = json.load(open(SC + r"\manual_en.json", encoding="utf-8"))
manual_ko = json.load(open(SC + r"\manual_ko.json", encoding="utf-8"))

# --- format check: can we reproduce the file byte-identically from json round-trip?
roundtrip = json.dumps(ja, ensure_ascii=False, indent=2)
if ja_text.rstrip("\n") == roundtrip:
    print("format round-trip: OK (indent=2)")
else:
    # find first diff for diagnosis
    a, b = ja_text.rstrip("\n"), roundtrip
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            print("format round-trip: MISMATCH at char", i)
            print("orig:", repr(a[max(0,i-60):i+60]))
            print("new :", repr(b[max(0,i-60):i+60]))
            sys.exit(1)
    print("format round-trip: length mismatch", len(a), len(b))
    sys.exit(1)

GENDER_EN = {"F": "(女)", "M": "(男)", "Female": "(女)", "Male": "(男)"}
GENDER_KO = {"여": "(女)", "남": "(男)"}


def lookup_en(name):
    if name in auto_map:
        return auto_map[name]
    if name in manual_en["exact"]:
        return manual_en["exact"][name]
    m = re.fullmatch(r"(.+?) \((F|M|Female|Male)\)", name)
    if m and m.group(1) in manual_en["gendered"]:
        return manual_en["gendered"][m.group(1)] + GENDER_EN[m.group(2)]
    return None


def lookup_ko(name):
    if name in manual_ko["exact"]:
        return manual_ko["exact"][name]
    m = re.fullmatch(r"(.+?) \((여|남)\)", name)
    if m:
        base, g = m.group(1), GENDER_KO[m.group(2)]
        if base in manual_ko["gendered"]:
            return manual_ko["gendered"][base] + g
        m2 = re.fullmatch(r"(\d\d/\d\d) 스킨 (.+)", base)
        if m2 and m2.group(2) in manual_ko["skin_slot"]:
            return f"{m2.group(1)} スキン{manual_ko['skin_slot'][m2.group(2)]}{g}"
    return None


n_en = n_ko = n_left = 0
miss_en, miss_ko = set(), set()
for key, entry in ja.items():
    name = entry.get("name", "")
    if not name.startswith("ITEMNAME_"):
        continue
    en_name = en.get(key, {}).get("name", "")
    ko_name = ko.get(key, {}).get("name", "")
    new = None
    if en_name and not en_name.startswith("ITEMNAME_"):
        new = lookup_en(en_name)
        if new is None:
            miss_en.add(en_name)
    elif ko_name and not ko_name.startswith("ITEMNAME_"):
        new = lookup_ko(ko_name)
        if new is None:
            miss_ko.add(ko_name)
    if new:
        entry["name"] = new
        if en_name and not en_name.startswith("ITEMNAME_"):
            n_en += 1
        else:
            n_ko += 1
    else:
        n_left += 1

print(f"translated from EN: {n_en}")
print(f"translated from KO: {n_ko}")
print(f"left untranslated:  {n_left}")
if miss_en:
    print("\nMISSING EN mappings:")
    for x in sorted(miss_en):
        print(" ", x)
if miss_ko:
    print("\nMISSING KO mappings:")
    for x in sorted(miss_ko):
        print(" ", x)

if miss_en or miss_ko:
    print("\nNOT writing file (missing mappings).")
    sys.exit(2)

out = json.dumps(ja, ensure_ascii=False, indent=2)
if ja_text.endswith("\n"):
    out += "\n"
with open(JA_PATH, "w", encoding="utf-8", newline="") as f:
    f.write(out)
print("\nfile written:", JA_PATH)
