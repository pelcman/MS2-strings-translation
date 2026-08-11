# -*- coding: utf-8 -*-
"""npcname / npcnameplural の未訳(プレースホルダー+ハングル残存)を適用する。

- npcname: KO名 → npc_map.json / tm_hits.json / LVnバランステスト正規表現 で解決
- npcnameplural: 同IDの npcname 訳 + ":s"(KO側の形式に追従。:s 無しならそのまま)

使い方: python work/npcname/apply_npcname.py
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, "work", "npcname")
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")
HG = re.compile(r"[가-힯]")
LVTEST = re.compile(r"^LV(\d+) 밸런스 (보스|엘리트|일반) 테스트$")
RANK = {"보스": "ボス", "엘리트": "エリート", "일반": "一般"}

def load(path):
    raw = open(path, encoding="utf-8", newline="").read()
    tail = "\n" if raw.endswith("\n") else ""
    d = json.loads(raw)
    assert json.dumps(d, ensure_ascii=False, indent=2) + tail == raw, f"RT不一致: {path}"
    return d, tail

def save(path, d, tail):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2) + tail)

def untranslated(s):
    return isinstance(s, str) and bool(s) and (PH.search(s) or HG.search(s))

def main():
    m = {k: v for k, v in json.load(open(os.path.join(WORK, "npc_map.json"), encoding="utf-8")).items()
         if not k.startswith("_")}
    m.update(json.load(open(os.path.join(WORK, "tm_hits.json"), encoding="utf-8")))
    m.update({k: v for k, v in json.load(open(os.path.join(WORK, "plural_map.json"), encoding="utf-8")).items()
              if not k.startswith("_")})

    def resolve(ko_name):
        ko_name = ko_name.strip()
        if ko_name in m: return m[ko_name]
        lt = LVTEST.match(ko_name)
        if lt: return f"LV{lt.group(1)}バランス{RANK[lt.group(2)]}テスト"
        return None

    # --- npcname ---
    jp_path = os.path.join(ROOT, "json_weblate", "jp", "npcname.json")
    jn, tail_n = load(jp_path)
    shutil.copyfile(jp_path, os.path.join(WORK, "npcname.backup.json"))
    kn = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "npcname.json"), encoding="utf-8"))
    changed = 0
    unresolved = []
    for k, v in jn.items():
        s = v.get("name")
        if not untranslated(s): continue
        src = kn.get(k, {}).get("name", "")
        if not isinstance(src, str) or not src or PH.search(src): continue
        ja = resolve(src)
        if ja is None:
            unresolved.append((k, src[:40]))
        else:
            v["name"] = ja
            changed += 1
    print(f"npcname 適用: {changed} / 未解決: {len(unresolved)}")
    for u in unresolved[:10]: print("  ", u)
    save(jp_path, jn, tail_n)

    # --- npcnameplural ---
    jpp_path = os.path.join(ROOT, "json_weblate", "jp", "npcnameplural.json")
    jpp, tail_p = load(jpp_path)
    shutil.copyfile(jpp_path, os.path.join(WORK, "npcnameplural.backup.json"))
    kop = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "npcnameplural.json"), encoding="utf-8"))
    changed_p = 0
    unresolved_p = []
    for k, v in jpp.items():
        s = v.get("name")
        if not untranslated(s): continue
        ko_p = kop.get(k, {}).get("name", "")
        base = jn.get(k, {}).get("name", "")
        if isinstance(base, str) and base and not untranslated(base):
            suffix = ":s" if isinstance(ko_p, str) and ko_p.endswith(":s") else ""
            v["name"] = base + suffix
            changed_p += 1
            continue
        # npcname 側に無い/未訳の場合: KO複数形から :s を外してマップ解決
        if isinstance(ko_p, str) and ko_p and not PH.search(ko_p):
            core = ko_p[:-2] if ko_p.endswith(":s") else ko_p
            ja = resolve(core)
            if ja is not None:
                v["name"] = ja + (":s" if ko_p.endswith(":s") else "")
                changed_p += 1
                continue
        unresolved_p.append((k, (ko_p or "")[:40]))
    print(f"npcnameplural 適用: {changed_p} / 未解決: {len(unresolved_p)}")
    for u in unresolved_p[:10]: print("  ", u)
    save(jpp_path, jpp, tail_p)

if __name__ == "__main__":
    main()
