# 担当500行の作業用コンテキストを吐く: 行番号 / 話者(KO->JA) / クエスト名 / KO / EN
import json, os, re
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", ".."))
PH_RE = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+")

src = json.load(open(os.path.join(BASE, "_sto_src.json"), encoding="utf-8"))
targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
ko2keys = defaultdict(list)
for k, v in targets.items():
    ko2keys[v[0]].append(k)

npc_ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "npcname.json"), encoding="utf-8"))
npc_bk = json.load(open(os.path.join(BASE, "..", "npcname", "npcname.backup.json"), encoding="utf-8"))
npc_jp = json.load(open(os.path.join(ROOT, "json_weblate", "jp", "npcname.json"), encoding="utf-8"))

ko2ja_off = {}   # 公式訳のみ
ko2ja_cur = {}
for k, e in npc_ko.items():
    kv = e.get("name")
    if not isinstance(kv, str) or not kv:
        continue
    bv = npc_bk.get(k, {}).get("name")
    if isinstance(bv, str) and bv and not PH_RE.match(bv):
        ko2ja_off.setdefault(kv, set()).add(bv)
    cv = npc_jp.get(k, {}).get("name")
    if isinstance(cv, str) and cv and not PH_RE.match(cv):
        ko2ja_cur.setdefault(kv, set()).add(cv)

qd_ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "questdescription_final.json"), encoding="utf-8"))
qd_bk = json.load(open(os.path.join(ROOT, "work", "questdesc", "questdescription_final.backup.json"), encoding="utf-8"))
qd_jp = json.load(open(os.path.join(ROOT, "json_weblate", "jp", "questdescription_final.json"), encoding="utf-8"))

out = []
for n in sorted(src, key=int):
    r = src[n]
    npc = r["npc"]
    off = "/".join(sorted(ko2ja_off.get(npc, ()))) or "-"
    cur = "/".join(sorted(ko2ja_cur.get(npc, ()))) or "-"
    qids = sorted({k[:8] for k in ko2keys.get(r["ko"], []) if re.match(r"^\d{8}", k)})
    qinfo = []
    for q in qids:
        for kk in (q + "--",):
            ke = qd_ko.get(kk, {})
            je = qd_jp.get(kk, {})
            be = qd_bk.get(kk, {})
            if ke:
                bn = be.get("name", "")
                jn = je.get("name", "")
                mark = "公式" if bn and not PH_RE.match(bn) and not re.search(r"[가-힣]", bn) else ""
                qinfo.append(f"{q}{mark}: {jn or ke.get('name','')}")
    out.append(f"### {n} 話者KO={npc} 公式JA={off} 現JA={cur}")
    if qinfo:
        out.append("  Q " + " ; ".join(qinfo))
    for t in ("exact", "keynum", "fuzzy"):
        if t in r:
            out.append("  SALVAGE(%s) %s" % (t, json.dumps(r[t], ensure_ascii=False)[:400]))

open(os.path.join(BASE, "_sto_ctx.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("written", len(out))
