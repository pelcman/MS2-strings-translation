# 翻訳メモリによる自動補完
#   PYTHONIOENCODING=utf-8 python work/scripts/tm_prefill.py scriptquest
#
# 同じ韓国語原文が別のキーで既に翻訳されていることが多いため、
# 全ファイルの ko→jp 対訳から索引を作り、欠落キーの KO 原文と完全一致するものを
# 自動で埋める。残りだけを翻訳ワーカーに回せば効率が大きく上がる。
#
# 出力:
#   work/missing/<file>.ja.auto.tsv  — 自動補完できた分(そのまま apply 可能)
#   work/missing/<file>.tsv          — 残り(未一致)だけに絞り込んで上書き
import json, os, re, sys, glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MIS = os.path.join(ROOT, "work", "missing")
PH = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\].*)?$")
HAN = re.compile(r"[가-힣]")
SKIP = {"npc", "type", "class", "regionID", "grade", "comment", "commnet", "isTutorial"}


def build_index():
    """全ファイルの (フィールド名, KO原文) -> JA訳 索引と、(フィールド名, EN原文) -> JA訳 索引。
    同じアイテム・台詞が別キー(他リージョン版など)で翻訳済みのことが多く、
    KO が一致しなくても EN が一致すれば同一物と判定できるケースが多い。"""
    idx = {}
    en_idx = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "json_weblate", "jp", "*.json"))):
        fn = os.path.basename(p)[:-5]
        kp = os.path.join(ROOT, "json_weblate", "ko", fn + ".json")
        if not os.path.exists(kp):
            continue
        ep = os.path.join(ROOT, "json_weblate", "en", fn + ".json")
        jp = json.load(open(p, encoding="utf-8"))
        ko = json.load(open(kp, encoding="utf-8"))
        en = json.load(open(ep, encoding="utf-8")) if os.path.exists(ep) else {}
        for k, e in jp.items():
            ke, ee = ko.get(k), en.get(k)
            if not isinstance(e, dict):
                continue
            for f, v in e.items():
                if f in SKIP or f.endswith("Kor"):
                    continue
                if not isinstance(v, str) or not v.strip() or PH.match(v.strip()):
                    continue
                if HAN.search(v):
                    continue          # JA にハングルが残っているものは採用しない
                kv = ke.get(f) if isinstance(ke, dict) else None
                if isinstance(kv, str) and kv.strip() and HAN.search(kv):
                    idx.setdefault((f, kv), v)
                ev = ee.get(f) if isinstance(ee, dict) else None
                if isinstance(ev, str) and ev.strip() and not PH.match(ev.strip()) and len(ev) > 2:
                    en_idx.setdefault((f, ev), v)
    return idx, en_idx


fn = sys.argv[1]
idx, en_idx = build_index()
print("翻訳メモリ索引: KO %d 件 / EN %d 件" % (len(idx), len(en_idx)))

src = os.path.join(MIS, fn + ".tsv")
rows = [l.rstrip("\n").split("\t") for l in open(src, encoding="utf-8") if l.strip()]

KANA = re.compile(r"[ぁ-んァ-ヶ]")

hit, rest = [], []
n_ko = n_en = n_jp = 0
for r in rows:
    if len(r) < 3:
        rest.append(r)
        continue
    key, field, kv = r[0], r[1], r[2].replace("⏎", "\n")
    ev = r[3].replace("⏎", "\n") if len(r) > 3 else ""
    # -Event-JP などのキーは ko ファイルの値がそのまま日本語(JMS2公式テキスト)。
    # かなを含むならハングルではないので、翻訳せずそのまま採用する。
    if KANA.search(kv) and not HAN.search(kv):
        hit.append("%s\t%s\t%s" % (key, field, kv.replace("\n", "⏎")))
        n_jp += 1
        continue
    ja = idx.get((field, kv))
    if ja:
        n_ko += 1
    # EN 一致は KO・EN とも十分な長さがある場合のみ採用する。
    # 短い語(1〜2文字の KO / 3文字以下の EN)は別アイテムでも偶然一致しやすく、
    # 文字集めイベントの「쌀→Rice」のような無関係な訳が入る事故があった。
    elif ev and len(kv.strip()) >= 3 and len(ev.strip()) >= 4:
        ja = en_idx.get((field, ev))
        if ja:
            n_en += 1
    if ja:
        hit.append("%s\t%s\t%s" % (key, field, ja.replace("\n", "⏎")))
    else:
        rest.append(r)
print("  内訳: KO一致 %d / EN一致 %d / 元から日本語 %d" % (n_ko, n_en, n_jp))

with open(os.path.join(MIS, fn + ".ja.auto.tsv"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(hit) + ("\n" if hit else ""))
with open(src, "w", encoding="utf-8", newline="\n") as fh:
    for r in rest:
        fh.write("\t".join(r) + "\n")

print("自動補完 %d 件 / 残り %d 件" % (len(hit), len(rest)))
