# 2026-11 再同期: 上書き後の jp を正とし、未訳/欠落分を HEAD 訳・TM で埋める計画を立てる(読み取り専用)
#   PYTHONIOENCODING=utf-8 python work/resync/plan.py [--write]
# --write で work/resync/<file>.todo.json (残り) と <file>.fill.json (自動確定分) を出力
import json, os, re, sys, glob, subprocess, collections
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "work", "resync")
PH = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\].*)?$")
HAN = re.compile(r"[가-힣]")
CN = re.compile(r"[一-鿿]")
SKIP = {"npc", "type", "class", "regionID", "grade", "comment", "commnet", "commend", "isTutorial", "feature", "id", "desc_kor"}
REF = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else "HEAD"
def skip(f): return f in SKIP or f.endswith("Kor")
def cur(lang, fn):
    p = os.path.join(ROOT, "json_weblate", lang, fn + ".json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
def head(lang, fn):
    r = subprocess.run(["git", "show", "%s:json_weblate/%s/%s.json" % (REF, lang, fn)], cwd=ROOT, capture_output=True)
    return json.loads(r.stdout.decode("utf-8")) if r.returncode == 0 else {}
def good(v): return isinstance(v, str) and v.strip() and not PH.match(v.strip()) and not HAN.search(v)
def fv(d, k, f):
    e = d.get(k); return e.get(f) if isinstance(e, dict) else None
def untrans(v): return isinstance(v, str) and v.strip() and (PH.match(v.strip()) or HAN.search(v))
def has_src(v): return isinstance(v, str) and v.strip() and not PH.match(v.strip()) and (HAN.search(v) or CN.search(v))

files = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ROOT, "json_weblate", "jp", "*.json")))
data = {}
tm = {}  # (field, ko) -> ja   (HEAD と現行の両方から)
tm_en = {}
idtm = {}  # (file, ID, field, ko) -> ja  キー接尾辞違い(--CN → -- 等)の回収用
for fn in files:
    J, K, E = cur("jp", fn), cur("ko", fn), cur("en", fn)
    HJ, HK = head("jp", fn), head("ko", fn)
    data[fn] = (J, K, E, HJ, HK)
    for (jj, kk, ee) in ((J, K, E), (HJ, HK, None)):
        for k, e in jj.items():
            if not isinstance(e, dict): continue
            for f, v in e.items():
                if skip(f) or not good(v): continue
                kv = fv(kk, k, f)
                if isinstance(kv, str) and (HAN.search(kv) or CN.search(kv)): tm.setdefault((f, kv), v)
                if isinstance(kv, str): idtm.setdefault((fn, k.split("-")[0].lstrip("0"), f, kv), v)
                if ee is not None:
                    ev = fv(ee, k, f)
                    if isinstance(ev, str) and len(ev.strip()) >= 4 and not PH.match(ev.strip()): tm_en.setdefault((f, ev), v)

tot = collections.Counter()
print("%-30s %6s %6s %6s %6s %6s | %6s %6s %6s %6s %6s" % ("file", "U:head", "U:id", "U:tm", "U:new", "U:none", "M:head", "M:id", "M:tm", "M:new", "M:jp"))
for fn in files:
    J, K, E, HJ, HK = data[fn]
    fill, todo = {}, {}
    c = collections.Counter()
    # 既存キーの未訳
    for k, e in J.items():
        if not isinstance(e, dict): continue
        for f, v in e.items():
            if skip(f) or not untrans(v): continue
            kv, ev, hv = fv(K, k, f), fv(E, k, f), fv(HJ, k, f)
            src = kv if has_src(kv) else None
            if good(hv) and (fv(HK, k, f) == kv or not HK):
                fill.setdefault(k, {})[f] = hv; c["U:head"] += 1
            elif src and (fn, k.split("-")[0].lstrip("0"), f, src) in idtm:
                fill.setdefault(k, {})[f] = idtm[(fn, k.split("-")[0].lstrip("0"), f, src)]; c["U:id"] += 1
            elif src and (f, src) in tm and len(src.strip()) >= 2:
                fill.setdefault(k, {})[f] = tm[(f, src)]; c["U:tm"] += 1
            elif src or (isinstance(ev, str) and ev.strip() and not PH.match(ev.strip())):
                todo.setdefault(k, {})[f] = [kv, ev]; c["U:new"] += 1
            else:
                c["U:none"] += 1
    # 欠落キー
    bkp = os.path.join(OUT, fn + ".backup.json")
    orig = json.load(open(bkp, encoding="utf-8")) if os.path.exists(bkp) else J
    for k, e in K.items():
        if k in orig or not isinstance(e, dict): continue
        for f, kv in e.items():
            if skip(f) or not has_src(kv) or f in J.get(k, {}): continue
            ev, hv = fv(E, k, f), fv(HJ, k, f)
            if re.search(r"[ぁ-んァ-ヶ]", kv) and not HAN.search(kv):
                fill.setdefault(k, {})[f] = kv; c["M:jp"] += 1
            elif good(hv) and (fv(HK, k, f) == kv or not HK):
                fill.setdefault(k, {})[f] = hv; c["M:head"] += 1
            elif (fn, k.split("-")[0].lstrip("0"), f, kv) in idtm:
                fill.setdefault(k, {})[f] = idtm[(fn, k.split("-")[0].lstrip("0"), f, kv)]; c["M:id"] += 1
            elif (f, kv) in tm and len(kv.strip()) >= 2:
                fill.setdefault(k, {})[f] = tm[(f, kv)]; c["M:tm"] += 1
            else:
                todo.setdefault(k, {})[f] = [kv, ev]; c["M:new"] += 1
    if sum(c.values()):
        print("%-30s %6d %6d %6d %6d %6d | %6d %6d %6d %6d %6d" % (fn, c["U:head"], c["U:id"], c["U:tm"], c["U:new"], c["U:none"], c["M:head"], c["M:id"], c["M:tm"], c["M:new"], c["M:jp"]))
    tot.update(c)
    if "--write" in sys.argv:
        for name, obj in (("fill", fill), ("todo", todo)):
            p = os.path.join(OUT, "%s.%s.json" % (fn, name))
            if obj:
                json.dump(obj, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
            elif os.path.exists(p): os.remove(p)
print("TOTAL", dict(tot))
