# -*- coding: utf-8 -*-
import json, collections

BASE = r"c:\Users\chro\Desktop\item"

with open(BASE + r"\maplestory2-xml-itemname-ja.json", encoding="utf-8") as f:
    ja = json.load(f)
with open(BASE + r"\maplestory2-xml-itemname-en.json", encoding="utf-8") as f:
    en = json.load(f)
with open(BASE + r"\maplestory2-xml-itemname-ko.json", encoding="utf-8") as f:
    ko = json.load(f)

def is_untranslated(name):
    return name.startswith("ITEMNAME_")

targets = {}  # key -> {class, en, ko}
no_en = []    # en also untranslated
for key, entry in ja.items():
    if not is_untranslated(entry.get("name", "")):
        continue
    en_name = en.get(key, {}).get("name", "")
    ko_name = ko.get(key, {}).get("name", "")
    if en_name and not is_untranslated(en_name):
        targets[key] = {"class": entry.get("class", ""), "en": en_name, "ko": ko_name}
    else:
        no_en.append({"key": key, "class": entry.get("class", ""), "en": en_name, "ko": ko_name})

print("ja untranslated total:", sum(1 for e in ja.values() if is_untranslated(e.get("name",""))))
print("with EN name:", len(targets))
print("without EN name:", len(no_en))

# unique EN names
uniq = collections.Counter(v["en"] for v in targets.values())
print("unique EN names:", len(uniq))
print("top duplicated:")
for name, c in uniq.most_common(15):
    print(f"  {c:4d}  {name}")

out = r"C:\Users\chro\AppData\Local\Temp\claude\c--Users-chro-Desktop-item\716449ef-c413-4587-8ba3-40dde686df10\scratchpad"
with open(out + r"\targets.json", "w", encoding="utf-8") as f:
    json.dump(targets, f, ensure_ascii=False, indent=1)
with open(out + r"\no_en.json", "w", encoding="utf-8") as f:
    json.dump(no_en, f, ensure_ascii=False, indent=1)
with open(out + r"\unique_en.json", "w", encoding="utf-8") as f:
    json.dump(sorted(uniq.keys()), f, ensure_ascii=False, indent=1)
