# sq_map*.json 検査ツール(翻訳ワーカー・レビュワー共用)
# 使い方: python work/scriptquest/check_map.py work/scriptquest/sq_map024.json ...
# ハードエラー(exit 1): キーが targets.json に無い / 値にハングル残存 / 値に $pp タグ残存
# 警告(exit 0): キーと値でタグの集合が不一致(意訳による削減の可能性あり、目視判断)
import json, re, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
kos = {v[0] for v in targets.values()}
HANGUL = re.compile(r"[가-힣]")
PP = re.compile(r"\$pp[2r]?:[^$]*\$")
TAG = re.compile(r"\$[A-Za-z]+(?::[^$]*)?\$|</?font[^>]*>")

hard = 0
for p in sys.argv[1:]:
    m = json.load(open(p, encoding="utf-8"))
    m.pop("_comment", None)
    errs, warns = [], []
    for k, v in m.items():
        if k not in kos:
            errs.append(("KEY_NOT_IN_TARGETS", k))
        if HANGUL.search(v):
            errs.append(("HANGUL_IN_VALUE", k))
        if PP.search(v):
            errs.append(("PP_TAG_IN_VALUE", k))
        if sorted(TAG.findall(PP.sub("", k))) != sorted(TAG.findall(v)):
            warns.append(("TAG_MISMATCH", k))
    print(f"{os.path.basename(p)}: {len(m)}件, エラー {len(errs)}, 警告 {len(warns)}")
    for t, k in (errs + warns)[:30]:
        print("  ", t, repr(k)[:110])
    hard += len(errs)

sys.exit(1 if hard else 0)
