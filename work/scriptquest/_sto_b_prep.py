# -*- coding: utf-8 -*-
import json, os, sys, collections

BASE = os.path.dirname(os.path.abspath(__file__))
LO, HI = 1, 500

targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
kos = {v[0] for v in targets.values()}

rows = []
with open(os.path.join(BASE, "todo_story.txt"), encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line.startswith("###"):
            continue
        num, rest = line[3:].split("|", 1)
        num = int(num)
        if num < LO or num > HI:
            continue
        spk, rest2 = rest.split("|", 1)
        ko, en = rest2.split("|", 1)
        ko = ko.replace("⏎", "\n")
        rows.append((num, spk, ko, en))

print("rows:", len(rows))
missing = [n for n, s, k, e in rows if k not in kos]
print("not in targets:", len(missing), missing[:10])

# dedupe map: ko -> first num
seen = {}
for n, s, k, e in rows:
    seen.setdefault(k, n)
print("unique ko:", len(seen))

out = {}
for n, s, k, e in rows:
    out[str(n)] = {"spk": s, "ko": k, "en": e, "dup_of": seen[k] if seen[k] != n else None}
json.dump(out, open(os.path.join(BASE, "_sto_b_src.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# speaker stats
c = collections.Counter(s for n, s, k, e in rows)
print(c.most_common())

# per-batch unique counts
for i in range(5):
    a, b = LO + i * 100, LO + i * 100 + 99
    sub = [(n, k) for n, s, k, e in rows if a <= n <= b]
    uniq = {k for n, k in sub}
    print(f"batch{i+1} ###{a}-{b}: rows={len(sub)} uniq={len(uniq)}")
