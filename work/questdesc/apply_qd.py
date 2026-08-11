# -*- coding: utf-8 -*-
"""questdescription_final 適用スクリプト。

翻訳ソースは KO。$pp...$(助詞プレースホルダー、JA では脱落)を除去した形で
  1) ファイル内既訳 TM(完全一致)
  2) 既訳ペアから自動学習した数値テンプレート(数値列が KO/JA で一致するもののみ)
  3) 手動ルール work/questdesc/qd_rules.json(数値正規化キー、"{}"に数値を順代入)
  4) 手動完全一致 work/questdesc/qd_map.json
を順に引く。手動ファイルは無ければスキップ。
"""
import json, os, re, shutil, sys, io, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")
HG = re.compile(r"[가-힯]")
NUM = re.compile(r"\d+")
PP = re.compile(r"\$pp[^$]*\$")

def load_optional(name):
    import glob as _glob
    out = {}
    pat = os.path.join(ROOT, "work", "questdesc", name.replace(".json", "*.json"))
    for p in sorted(_glob.glob(pat)):
        for k, v in json.load(open(p, encoding="utf-8")).items():
            if not k.startswith("_"):
                out[k] = v
    return out

def main():
    fn = "questdescription_final"
    jp_path = os.path.join(ROOT, "json_weblate", "jp", fn + ".json")
    raw = open(jp_path, encoding="utf-8", newline="").read()
    tail = "\n" if raw.endswith("\n") else ""
    jp = json.loads(raw)
    assert json.dumps(jp, ensure_ascii=False, indent=2) + tail == raw, "RT不一致"
    shutil.copyfile(jp_path, os.path.join(ROOT, "work", "questdesc", fn + ".backup.json"))
    ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", fn + ".json"), encoding="utf-8"))

    # 既訳ペア → TM(pp除去キー) & テンプレート学習(pp除去+数値列一致)
    tm = {}
    learn = collections.defaultdict(set)
    for k, v in jp.items():
        for f, s in v.items():
            if not isinstance(s, str) or not s or PH.search(s) or HG.search(s):
                continue
            kn = ko.get(k, {}).get(f, "")
            if not isinstance(kn, str) or not kn:
                continue
            kn2 = PP.sub("", kn)
            tm.setdefault(kn2, s)
            knums = NUM.findall(kn2)
            if knums and knums == NUM.findall(s):
                learn[NUM.sub("#", kn2)].add(NUM.sub("{}", s))
    templates = {p: t.pop() for p, t in learn.items() if len(t) == 1}
    rules = load_optional("qd_rules.json")
    emap = load_optional("qd_map.json")

    n_tm = n_tpl = n_rule = n_map = bad = 0
    rest = collections.Counter()
    rest_ex = {}
    for k, v in jp.items():
        for f, s in list(v.items()):
            if not isinstance(s, str) or not s or not (PH.search(s) or HG.search(s)):
                continue
            kn = ko.get(k, {}).get(f, "")
            if not isinstance(kn, str) or not kn or PH.search(kn):
                continue
            kn2 = PP.sub("", kn)
            if kn2 in tm:
                v[f] = tm[kn2]; n_tm += 1; continue
            if kn2 in emap:
                v[f] = emap[kn2]; n_map += 1; continue
            norm = NUM.sub("#", kn2)
            nums = NUM.findall(kn2)
            tpl = templates.get(norm)
            which = "tpl"
            if tpl is None and norm in rules:
                tpl = rules[norm]; which = "rule"
            if tpl is not None:
                if tpl.count("{}") != len(nums):
                    bad += 1; continue
                v[f] = tpl.format(*nums)
                if which == "tpl": n_tpl += 1
                else: n_rule += 1
                continue
            rest[norm] += 1
            rest_ex.setdefault(norm, kn)
    total = n_tm + n_tpl + n_rule + n_map
    print(f"適用 {total} (TM {n_tm} / 自動tpl {n_tpl} / 手動rule {n_rule} / 手動map {n_map}) "
          f"/ スロット不一致 {bad} / 残り {sum(rest.values())} (ユニーク {len(rest)})")
    with open(os.path.join(ROOT, "work", "questdesc", "rest_patterns.txt"), "w", encoding="utf-8") as fh:
        for p, c in rest.most_common():
            fh.write(f"x{c}\t{p}\n\tEX: {rest_ex[p]}\n")
    with open(jp_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(jp, ensure_ascii=False, indent=2) + tail)

if __name__ == "__main__":
    main()
