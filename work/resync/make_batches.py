# 2026-11 再同期: todo.json を翻訳ワーカー用バッチに分割する
#   PYTHONIOENCODING=utf-8 python work/resync/make_batches.py
# 数値だけが異なる原文は1ユニットにまとめる(代表を訳し、残りは expand.py が数値を差し替えて生成)
# 出力: work/resync/batches/<batch>.in.json  [{id, field, ko, en, npc?, npc_ja?, n}]
#       work/resync/batches/units.json       ユニット → [(データ名, キー, フィールド, KO, EN)]
import json, os, re, glob, collections
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "work", "resync")
B = os.path.join(OUT, "batches")
NUM = re.compile(r"(?<![#$:\w])\d+(?:\.\d+)?")

# 話者名 KO -> JA(npcname の既訳)
npc_ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "npcname.json"), encoding="utf-8"))
npc_jp = json.load(open(os.path.join(ROOT, "json_weblate", "jp", "npcname.json"), encoding="utf-8"))
spk = {}
for k, e in npc_ko.items():
    j = npc_jp.get(k, {}).get("name")
    if isinstance(e, dict) and e.get("name") and j and not re.search(r"[가-힣]", j):
        spk.setdefault(e["name"], j)
sko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "scriptnpc.json"), encoding="utf-8"))

PLAN = {  # データ名 -> バッチ数
    "scriptnpc": 4, "questdescription_final": 2, "stringskilldescription": 1,
    "setitemname": "misc", "stringadditionaldescription": "misc", "koritemdescription": "misc", "achievedescription": "misc",
}
units = {}
batches = collections.defaultdict(list)
for fn, nb in PLAN.items():
    todo = json.load(open(os.path.join(OUT, fn + ".todo.json"), encoding="utf-8"))
    groups = collections.OrderedDict()
    for k, e in todo.items():
        for f, (kv, ev) in e.items():
            t = (f, NUM.sub("#", kv or ""), NUM.sub("#", ev or ""))
            groups.setdefault(t, []).append((fn, k, f, kv, ev))
    items = []
    for i, (t, mem) in enumerate(groups.items(), 1):
        fn_, k, f, kv, ev = mem[0]
        uid = "%s#%04d" % (fn, i)
        units[uid] = mem
        u = {"id": uid, "field": f, "ko": kv, "en": ev}
        if fn == "scriptnpc":
            s = sko.get(k, {}).get("npc")
            u["npc"] = s
            if s in spk: u["npc_ja"] = spk[s]
        if len(mem) > 1: u["n"] = len(mem)
        items.append(u)
    if nb == "misc":
        batches["misc"].extend(items)
    else:
        total = sum(len(u["ko"] or u["en"] or "") for u in items)
        per = total / nb; acc = 0; bi = 1
        for u in items:
            if acc >= per * bi and bi < nb: bi += 1
            batches["%s_%d" % (fn, bi)].append(u)
            acc += len(u["ko"] or u["en"] or "")
for name, items in batches.items():
    json.dump(items, open(os.path.join(B, name + ".in.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(name, len(items), "units", sum(len(u["ko"] or "") for u in items), "KO chars")
json.dump(units, open(os.path.join(B, "units.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
