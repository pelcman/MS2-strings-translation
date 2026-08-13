# 担当範囲(###1-500)の KO 原文を抽出し、公式既訳をサルベージする
import json, os, glob, re, difflib
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", ".."))
LO, HI = 1, 500

rows = {}
for ln in open(os.path.join(BASE, "todo_story.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    n = int(num[3:])
    if LO <= n <= HI:
        rows[n] = (npc, ko.replace("⏎", "\n"), en)

targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
kos = {v[0] for v in targets.values()}
ko2keys = defaultdict(list)
for k, v in targets.items():
    ko2keys[v[0]].append(k)

missing = [n for n, (a, k, e) in rows.items() if k not in kos]
print("rows:", len(rows), "not-in-targets:", missing)

# 既存 sq_*.json の訳
exist = {}
for p in sorted(glob.glob(os.path.join(BASE, "sq_*.json"))):
    d = json.load(open(p, encoding="utf-8"))
    d.pop("_comment", None)
    for k, v in d.items():
        exist.setdefault(k, (os.path.basename(p), v))
dup = {n: exist[k] for n, (a, k, e) in rows.items() if k in exist}
print("already-translated-in-sq:", len(dup))
for n in sorted(dup):
    print("  DUP", n, dup[n][0], repr(rows[n][1])[:60], "=>", repr(dup[n][1])[:80])

# KO 内の重複
seen = defaultdict(list)
for n, (a, k, e) in rows.items():
    seen[k].append(n)
print("internal-dup groups:", [v for v in seen.values() if len(v) > 1])

# ===== 公式既訳サルベージ =====
PH_RE = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+")
sq_jp = json.load(open(os.path.join(BASE, "scriptquest.backup.json"), encoding="utf-8"))
sq_ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "scriptquest.json"), encoding="utf-8"))
qd_jp = json.load(open(os.path.join(ROOT, "work", "questdesc", "questdescription_final.backup.json"), encoding="utf-8"))
qd_ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "questdescription_final.json"), encoding="utf-8"))


def norm(s):
    s = re.sub(r"\$pp[2r]?:[^$]*\$", "", s)
    s = re.sub(r"</?font[^>]*>", "", s)
    s = re.sub(r"\s+", "", s)
    return s


# 公式訳 (KO正規化 -> JA) のプール
pool = {}          # normko -> [(src, key, ja, rawko)]
def add_pool(ko_d, jp_d, tag, fields):
    for k, e in jp_d.items():
        ke = ko_d.get(k)
        if not isinstance(ke, dict) or not isinstance(e, dict):
            continue
        for f in fields:
            jv, kv = e.get(f), ke.get(f)
            if not isinstance(jv, str) or not isinstance(kv, str) or not jv or not kv:
                continue
            if PH_RE.match(jv) or re.search(r"[가-힣]", jv):
                continue
            pool.setdefault(norm(kv), []).append((tag, k, jv, kv))

add_pool(sq_ko, sq_jp, "sq", ["name"])
add_pool(qd_ko, qd_jp, "qd", ["desc", "complete", "manual", "manualDesc", "manualComplete"])
print("official pool:", len(pool))

# クエストID(キー先頭8桁)ベースの索引
sq_bykeynum = defaultdict(list)
for k, e in sq_jp.items():
    jv = e.get("name")
    if not isinstance(jv, str) or not jv or PH_RE.match(jv) or re.search(r"[가-힣]", jv):
        continue
    m = re.match(r"^(\d{8})", k)
    if m:
        sq_bykeynum[m.group(1)].append((k, jv, sq_ko.get(k, {}).get("name", "")))
for k, e in qd_jp.items():
    m = re.match(r"^(\d{8})", k)
    if not m or not isinstance(e, dict):
        continue
    ke = qd_ko.get(k, {})
    for f in ["desc", "complete", "manual", "manualDesc", "manualComplete", "name"]:
        jv, kv = e.get(f), ke.get(f) if isinstance(ke, dict) else None
        if not isinstance(jv, str) or not isinstance(kv, str) or not jv or not kv:
            continue
        if PH_RE.match(jv) or re.search(r"[가-힣]", jv):
            continue
        sq_bykeynum[m.group(1)].append(("qd:" + k + ":" + f, jv, kv))

pool_keys = list(pool.keys())

out = {}
stat = defaultdict(int)
for n in sorted(rows):
    npc, ko, en = rows[n]
    nk = norm(ko)
    rec = {"npc": npc, "ko": ko, "en": en}
    if nk in pool:
        rec["exact"] = pool[nk][0][:3]
        stat["exact"] += 1
    else:
        # キー番号一致
        cand = []
        for key in ko2keys.get(ko, []):
            m = re.match(r"^(\d{8})", key)
            if m:
                for kk, jv, kv in sq_bykeynum.get(m.group(1), []):
                    r = difflib.SequenceMatcher(None, nk, norm(kv)).ratio()
                    cand.append((r, kk, jv, kv))
        cand.sort(reverse=True)
        if cand and cand[0][0] >= 0.72:
            rec["keynum"] = cand[0][:4]
            stat["keynum"] += 1
        else:
            best = difflib.get_close_matches(nk, pool_keys, n=1, cutoff=0.72)
            if best:
                r = difflib.SequenceMatcher(None, nk, best[0]).ratio()
                rec["fuzzy"] = [round(r, 3)] + list(pool[best[0]][0][:4])
                stat["fuzzy"] += 1
            elif cand:
                rec["keynum_low"] = [round(cand[0][0], 3)] + list(cand[0][1:])
    out[str(n)] = rec

print("salvage:", dict(stat))
json.dump(out, open(os.path.join(BASE, "_sto_src.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
