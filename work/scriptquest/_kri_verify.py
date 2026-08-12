# 担当範囲(###1-400)のカバレッジ・書式・訳語統一の自己検証
import json, os, re, glob

BASE = os.path.dirname(os.path.abspath(__file__))
rows = {}
for ln in open(os.path.join(BASE, "todo_kritias.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    rows[int(num[3:])] = (npc, ko.replace("⏎", "\n"))

merged, per = {}, {}
for i in (1, 2, 3, 4):
    p = os.path.join(BASE, "sq_kri%03d.json" % i)
    raw = open(p, "rb").read()
    assert b"\r" not in raw, ("CRLF", p)
    assert raw.endswith(b"\n"), ("末尾改行なし", p)
    d = json.loads(raw.decode("utf-8"))
    assert (json.dumps(d, ensure_ascii=False, indent=2) + "\n").encode("utf-8") == raw, ("書式不一致", p)
    d.pop("_comment", None)
    per[i] = d
    for k, v in d.items():
        if k in merged and merged[k] != v:
            print("!! 値の衝突:", repr(k)[:60])
        merged[k] = v

# カバレッジ
uncovered = [n for n in range(1, 401) if rows[n][1] not in merged]
print("未カバー:", uncovered)
extra = [k for k in merged if k not in {rows[n][1] for n in range(1, 401)}]
print("担当外キー:", len(extra))
print("ユニークキー総数:", len(merged), "/ 対象行 400")

# unify.py の FIX に抵触していないか
NG = ["星明かり遠征隊", "招集令", "女帝様", "メソ", "総理", "ホムプルス", "黒星会のドン", "ドンである"]
for k, v in merged.items():
    for w in NG:
        if w in v:
            print("!! 表記ゆれ", w, repr(v)[:60])

# 全角英数字・タグ健全性
FW = re.compile(r"[Ａ-Ｚａ-ｚ０-９]")
PP = re.compile(r"\$pp[2r]?:")
for k, v in merged.items():
    if FW.search(v):
        print("!! 全角英数", repr(v)[:60])
    if PP.search(v):
        print("!! ppタグ", repr(v)[:60])
    if v.count("<font") != v.count("</font"):
        print("!! fontタグ不整合", repr(v)[:70])
    # 先頭/末尾の空白・改行が原文と一致するか
    ko = k
    for f in (lambda s: s[:1], lambda s: s[-1:]):
        pass
    if (ko[:1].isspace()) != (v[:1].isspace()) or (ko[-1:].isspace()) != (v[-1:].isspace()):
        print("!! 前後空白不一致", repr(ko)[-40:], "=>", repr(v)[-40:])
    if ko.count("\n") != v.count("\n"):
        print("!! 改行数差", ko.count("\n"), v.count("\n"), repr(ko)[:50])
print("検証終了")
