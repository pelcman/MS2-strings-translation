# scriptquest 訳語統一スクリプト(適用後に毎回実行)
# ワーカー横断で発生した表記ブレを、原本(JMS2公式)調査で確定した表記に一括統一する。
# 対象: work/scriptquest/sq_map*.json と json_weblate/jp/scriptquest.json
#
# 各ルールの根拠は右コメント。命名系ファイル(itemname/npcname/mapname/npctitle/titlename)を
# 最優先、次に scriptquest 原本の多数派、という優先順位で確定している。
import json, glob, os, re

FIX = [
    ("星明かり遠征隊", "星色遠征隊"),  # 命名系25件 vs questdesc10件
    ("招集令", "召集令"),              # scriptquest原本2件+stringtrigger原本9件
    ("女帝様", "女王様"),              # scriptquest原本の一貫表記
    ("メソ", "メル"),                  # stringcommon原本163件(通貨単位)
    ("総理", "大臣"),                  # npctitle/mapname/itemname/npcname + scriptquest原本9件
    ("ホムプルス", "ハンフルス"),      # 命名系9件 vs questdesc16件
    ("黒星会のドン", "黒星会の顔役"),  # 대부: questdesc原本 10002020 が同一NPCで「顔役」
    ("ドンである", "顔役である"),      # 同上
    ("$MyPCName$様", "$MyPCName$さん"),  # 公式原本は「さん」486件・「様」0件
    ("闇の気配", "闇のオーラ"),          # 어둠의 기운: 公式原本は闇のオーラ54件(気配は0件)
]

# 正規表現による統一。(パターン, 置換)
# NPC 名タグの直後の敬称は「様」。公式原本は 様243件・さん1件。
# ただし $MyPCName$(プレイヤー)は「さん」なので、npc/npcName タグのみを対象にする。
REGEX_FIX = [
    (re.compile(r"(\$npc(?:Name)?:[^$]*\$)さん"), r"\1様"),
]

# 本プロジェクトが訳した行にだけ適用する正規表現。
# 公式原本は感嘆符・疑問符の約9割が全角(！5620/! 663、？4801/? 226)。
# 欠落キー補完のバッチが半角に偏っていたため、英数字の直後以外を全角に揃える。
OURS_ONLY_REGEX = [
    (re.compile(r"(?<![A-Za-z0-9])!"), "！"),
    (re.compile(r"(?<![A-Za-z0-9])\?"), "？"),
]

# 話者ごとの一人称。公式原本の用例に合わせる。
# (話者名, 誤, 正) — その話者の name のみを置換する
SPEAKER_FIX = [
    ("메이슨", "私", "僕"),   # 公式原本メイソン: 僕117 / 私3
]

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", ".."))
targets = sorted(glob.glob(os.path.join(BASE, "sq_*.json")))   # sq_map* と sq_kri* の両方
targets.append(os.path.join(ROOT, "json_weblate", "jp", "scriptquest.json"))

# 話者別ルールを適用する KO 原文の集合を作る(sq_* のキーは KO 原文なので照合できる)
ko_all = json.load(open(os.path.join(ROOT, "json_weblate", "ko", "scriptquest.json"), encoding="utf-8"))
jp_orig = json.load(open(os.path.join(BASE, "scriptquest.backup.json"), encoding="utf-8"))
PH_RE = re.compile(r"^[A-Z0-9$]+(_[A-Z0-9$]+)+")
speaker_ko = {}      # 話者名 -> その話者の KO 原文集合(公式訳が無い行のみ)
speaker_key = {}     # 話者名 -> その話者のキー集合(同上)
is_official = {}     # キー -> JMS2 公式訳が存在するか
for _k, _e in jp_orig.items():
    _bv = _e.get("name")
    is_official[_k] = isinstance(_bv, str) and bool(_bv) and not PH_RE.match(_bv)
for _k, _e in ko_all.items():
    _npc = _e.get("npc")
    if not _npc:
        continue
    _bv = jp_orig.get(_k, {}).get("name")
    if isinstance(_bv, str) and _bv and not PH_RE.match(_bv):
        continue     # 公式訳がある行は触らない
    _v = _e.get("name")
    if isinstance(_v, str):
        speaker_ko.setdefault(_npc, set()).add(_v)
        speaker_key.setdefault(_npc, set()).add(_k)

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
        for rx, rep in REGEX_FIX:
            nv = rx.sub(rep, nv)
        # 公式訳が存在しない行(=本PJ訳)のみ
        if not isjp or not is_official.get(k):
            for rx, rep in OURS_ONLY_REGEX:
                nv = rx.sub(rep, nv)
        for spk, wrong, right in SPEAKER_FIX:
            hit = k in speaker_key.get(spk, ()) if isjp else k in speaker_ko.get(spk, ())
            if hit:
                nv = nv.replace(wrong, right)
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
