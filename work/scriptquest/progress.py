# scriptquest 翻訳の進捗表示(読み取り専用・いつ実行しても安全)
#   PYTHONIOENCODING=utf-8 python work/scriptquest/progress.py
# ファイルは一切変更しない。稼働中のワーカーと衝突しない。
import json, glob, os, re, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", ".."))
JP = os.path.join(ROOT, "json_weblate", "jp", "scriptquest.json")
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")

targets = json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))["targets"]
jp = json.load(open(JP, encoding="utf-8"))

done = remain = 0
remain_ko = set()
for k, (kov, env) in targets.items():
    cur = jp.get(k, {}).get("name")
    if isinstance(cur, str) and PH.search(cur):
        remain += 1
        remain_ko.add(kov)
    else:
        done += 1

total = done + remain
pct = done * 100.0 / total if total else 0
bar = "#" * int(pct / 2.5) + "-" * (40 - int(pct / 2.5))

print(f"scriptquest 翻訳進捗   [{bar}] {pct:.1f}%")
print(f"  適用済み : {done:,} / {total:,}")
print(f"  残り     : {remain:,} (ユニーク {len(remain_ko):,})")

maps = sorted(glob.glob(os.path.join(BASE, "sq_map*.json")))
print(f"\n作成済みバッチ: {len(maps)} 個 (最新 {os.path.basename(maps[-1]) if maps else 'なし'})")
for p in maps[-3:]:
    m = json.load(open(p, encoding="utf-8"))
    c = m.pop("_comment", "")
    ts = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%m/%d %H:%M")
    print(f"  {os.path.basename(p)}  {len(m):3d}件  {ts}  {c[:60]}")

# 稼働中ワーカーの目安: todo.txt の何行目まで着手済みか
todo = os.path.join(BASE, "todo.txt")
if os.path.exists(todo):
    n = sum(1 for _ in open(todo, encoding="utf-8"))
    print(f"\ntodo.txt 全 {n:,} 行 / 次の未着手はおよそ {len(maps)*100+1:,} 行目から")
