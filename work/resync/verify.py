# 2026-11 再同期: 適用結果の検証(AGENTS.md「検証(必須)」)
#   PYTHONIOENCODING=utf-8 python work/resync/verify.py
import json, os, re, glob, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "work", "resync")
PH = re.compile(r"^[A-Z0-9$]+(_+[A-Z0-9$]+)+(:\[F\].*)?$")
HAN = re.compile(r"[가-힣]")
SC = re.compile(r"[们这说们关于让过还从]")   # 簡体字に特有の字(日本語に出ない)
SKIP = {"npc", "type", "class", "regionID", "grade", "comment", "commnet", "commend", "desc", "isTutorial"}
def untrans(v): return isinstance(v, str) and v.strip() and (PH.match(v.strip()) or HAN.search(v))
ng = 0
for bk in sorted(glob.glob(os.path.join(OUT, "*.backup.json"))):
    fn = os.path.basename(bk)[:-12]
    JP = os.path.join(ROOT, "json_weblate", "jp", fn + ".json")
    raw = open(JP, "rb").read()
    braw = open(bk, "rb").read()
    errs = []
    if b"\r" in raw: errs.append("CR")
    if raw.endswith(b"\n") != braw.endswith(b"\n"): errs.append("末尾改行が変化")
    jp = json.loads(raw.decode("utf-8")); old = json.loads(braw.decode("utf-8"))
    ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", fn + ".json"), encoding="utf-8"))
    if list(jp)[:len(old)] != list(old): errs.append("既存キー順が変化")
    ch = 0
    for k, e in old.items():
        if not isinstance(e, dict): continue
        if list(jp[k]) != list(e): errs.append("フィールド構成変化 " + k)
        for f, v in e.items():
            if jp[k][f] != v:
                if not untrans(v): errs.append("翻訳済み/非対象を変更 %s %s" % (k, f))
                ch += 1
    new = [k for k in jp if k not in old]
    if [k for k in ko if k in new] != new: errs.append("追加キーが ko 順でない/ko に無い")
    han = ph = sc = 0
    for k, e in jp.items():
        if not isinstance(e, dict): continue
        for f, v in e.items():
            if not isinstance(v, str) or f in SKIP or f.endswith("Kor"):
                if f == "desc" and fn != "stringcommon" and isinstance(v, str) and HAN.search(v): han += 1
                continue
            if HAN.search(v): han += 1
            if PH.match(v.strip()): ph += 1
            if SC.search(v): sc += 1
    oph = sum(1 for e in old.values() if isinstance(e, dict) for f, v in e.items() if isinstance(v, str) and PH.match(v.strip()))
    print("%-30s 変更 %5d 追加キー %5d | ハングル %4d PH %4d(取込時 %4d) 簡体字疑い %d %s" % (fn, ch, len(new), han, ph, oph, sc, "NG " + "; ".join(errs[:3]) if errs else "OK"))
    ng += bool(errs)
sys.exit(1 if ng else 0)
