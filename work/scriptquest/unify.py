# scriptquest 訳語統一スクリプト(適用後に毎回実行)
# ワーカー横断で発生した表記ブレを、原本(JMS2公式)調査で確定した表記に一括統一する。
# 対象: work/scriptquest/sq_map*.json と json_weblate/jp/scriptquest.json
#
# 各ルールの根拠は右コメント。命名系ファイル(itemname/npcname/mapname/npctitle/titlename)を
# 最優先、次に scriptquest 原本の多数派、という優先順位で確定している。
import json, glob, os

FIX = [
    ("星明かり遠征隊", "星色遠征隊"),  # 命名系25件 vs questdesc10件
    ("招集令", "召集令"),              # scriptquest原本2件+stringtrigger原本9件
    ("女帝様", "女王様"),              # scriptquest原本の一貫表記
    ("メソ", "メル"),                  # stringcommon原本163件(通貨単位)
    ("総理", "大臣"),                  # npctitle/mapname/itemname/npcname + scriptquest原本9件
    ("ホムプルス", "ハンフルス"),      # 命名系9件 vs questdesc16件
    ("黒星会のドン", "黒星会の顔役"),  # 대부: questdesc原本 10002020 が同一NPCで「顔役」
    ("ドンである", "顔役である"),      # 同上
]

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", ".."))
targets = sorted(glob.glob(os.path.join(BASE, "sq_map*.json")))
targets.append(os.path.join(ROOT, "json_weblate", "jp", "scriptquest.json"))

total = 0
for p in targets:
    raw = open(p, "rb").read()
    tail = b"\n" if raw.endswith(b"\n") else b""
    d = json.loads(raw.decode("utf-8"))
    assert (json.dumps(d, ensure_ascii=False, indent=2) + tail.decode()).encode("utf-8") == raw, p
    isjp = p.replace("\\", "/").endswith("jp/scriptquest.json")
    n = 0
    for k, e in d.items():
        v = e.get("name") if isjp else e
        if not isinstance(v, str):
            continue
        nv = v
        for a, b in FIX:
            nv = nv.replace(a, b)
        if nv != v:
            if isjp:
                e["name"] = nv
            else:
                d[k] = nv
            n += 1
    if n:
        open(p, "wb").write(json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8") + tail)
        print(os.path.basename(p), "統一", n)
        total += n
print("統一合計", total)
