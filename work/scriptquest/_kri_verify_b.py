# 担当範囲(###1-400 / 再生成後 todo_kritias.txt)のカバレッジ・書式・訳語統一の自己検証
import json, os, re, glob

BASE = os.path.dirname(os.path.abspath(__file__))
rows = {}
for ln in open(os.path.join(BASE, "todo_kritias.txt"), encoding="utf-8").read().split("\n"):
    if not ln.startswith("###"):
        continue
    num, npc, ko, en = ln.split("|", 3)
    rows[int(num[3:])] = (npc, ko.replace("⏎", "\n"))

merged = {}
for i in (5, 6, 7, 8):
    p = os.path.join(BASE, "sq_kri%03d.json" % i)
    raw = open(p, "rb").read()
    assert b"\r" not in raw, ("CRLF", p)
    assert raw.endswith(b"\n"), ("末尾改行なし", p)
    d = json.loads(raw.decode("utf-8"))
    assert (json.dumps(d, ensure_ascii=False, indent=2) + "\n").encode("utf-8") == raw, ("書式不一致", p)
    d.pop("_comment", None)
    for k, v in d.items():
        if k in merged and merged[k] != v:
            print("!! 値の衝突:", repr(k)[:60])
        merged[k] = v

uncovered = [n for n in range(1, 401) if rows[n][1] not in merged]
print("未カバー:", uncovered)
mine = {rows[n][1] for n in range(1, 401)}
print("担当外キー:", len([k for k in merged if k not in mine]))
print("ユニークキー総数:", len(merged), "/ 対象行 400")

# 既存 sq_* との重複チェック(他ワーカーの訳と衝突しないか)
for p in sorted(glob.glob(os.path.join(BASE, "sq_*.json"))):
    if os.path.basename(p) in ("sq_kri005.json", "sq_kri006.json", "sq_kri007.json", "sq_kri008.json"):
        continue
    d = json.load(open(p, encoding="utf-8"))
    d.pop("_comment", None)
    for k, v in d.items():
        if k in merged and merged[k] != v:
            print("!! 他ファイルと訳が異なる:", os.path.basename(p), repr(k)[:50])

NG = ["星明かり遠征隊", "招集令", "女帝様", "メソ", "総理", "ホムプルス", "黒星会のドン", "ドンである"]
FW = re.compile(r"[Ａ-Ｚａ-ｚ０-９]")
PP = re.compile(r"\$pp[2r]?:")
for k, v in merged.items():
    for w in NG:
        if w in v:
            print("!! 表記ゆれ", w, repr(v)[:60])
    if FW.search(v):
        print("!! 全角英数", repr(v)[:60])
    if PP.search(v):
        print("!! ppタグ", repr(v)[:60])
    if v.count("<font") != v.count("</font"):
        print("!! fontタグ不整合", repr(v)[:70])
    if k.count("\n") != v.count("\n"):
        print("!! 改行数差", k.count("\n"), v.count("\n"), repr(k)[:50])
    # 各行の前後空白が原文と一致するか
    for i, (a, b) in enumerate(zip(k.split("\n"), v.split("\n"))):
        if (len(a) - len(a.rstrip())) != (len(b) - len(b.rstrip())):
            print("!! 行末空白不一致", i, repr(a)[-30:], "=>", repr(b)[-30:])
        if (len(a) - len(a.lstrip())) != (len(b) - len(b.lstrip())):
            print("!! 行頭空白不一致", i, repr(a)[:30], "=>", repr(b)[:30])
print("検証終了")
