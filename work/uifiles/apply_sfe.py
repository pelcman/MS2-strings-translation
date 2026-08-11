# -*- coding: utf-8 -*-
"""stringfieldenterance 専用適用スクリプト。

KO 原文を実改行で行分割し、各行を
  1) 既訳 TM(同ファイル内の既訳エントリから構築、行単位)
  2) sfe_map.json(手訳の完全一致)
  3) 装備ガイド行・ラウンド見出し行・報酬統合行のルール生成
で翻訳する。先頭のリテラル \\n 接頭辞は剥がして照合し、再付与する。
1 行でも訳せないフィールドは変更しない(レポートのみ)。
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")
HG = re.compile(r"[가-힯]")
PREFIX = re.compile(r"^(?:\\n)+")  # リテラル \n(バックスラッシュ+n)の連続

SLOT = {"무기": "武器", "모자": "帽子", "상의": "服(上)", "하의": "服(下)",
        "장갑": "グローブ", "신발": "靴", "귀고리": "イヤリング", "망토": "マント",
        "목걸이": "ネックレス", "반지": "指輪", "벨트": "ベルト"}
GRADE = {"엑설런트": "エクセレント", "레전더리": "レジェンダリー", "에픽": "エピック",
         "에픽 파이어 프리즘": "エピックファイアプリズム"}

GEAR = re.compile(
    r"^<font color='#00aaef'>(?P<slots>[^<]+)</font> : (?P<lv>\d+)레벨 "
    r"<font color='(?P<c>[^']+)'>(?P<grade>[^<]+)</font> (?P<rest>(등급|장비).*)$")
ROUND = re.compile(r"^<font color='#FFD400'>\* (?P<r>[\d~]+)라운드 아이템 점수 : (?P<sc>\d+)</font>$")
REWARD = re.compile(r"^<font color='#00aaef'>보상 획득 횟수는 \$dungeonTitle:(?P<id>\d+)\$ 던전과 통합됩니다\.</font>$")

TAILS = [
    (re.compile(r"^ 엘리트 어드벤쳐 장비 인챈트 (\d+)단계$"), "エリートアドベンチャー装備エンチャント{}段階"),
    (re.compile(r"^ 엘리트 어드벤쳐 무기 인챈트 (\d+)단계$"), "エリートアドベンチャー武器エンチャント{}段階"),
    (re.compile(r"^ 인챈트 (\d+)단계$"), "エンチャント{}段階"),
    (re.compile(r"^ 앱솔루트 액세서리$"), "アブソリュートアクセサリー"),
    (re.compile(r"^ 떠돌이 모험가의 유산 액세서리$"), "さすらい冒険者の遺産アクセサリー"),
    (re.compile(r"^ 타이렌 렌샤 액세서리$"), "タイレンレンシャアクセサリー"),
    (re.compile(r"^$"), ""),
]

def slots_ja(s):
    parts = [p.strip() for p in s.split(",")]
    if any(p not in SLOT for p in parts):
        return None
    out, i = [], 0
    while i < len(parts):
        if parts[i] == "상의" and i + 1 < len(parts) and parts[i + 1] == "하의":
            out.append("服(上下)"); i += 2
        else:
            out.append(SLOT[parts[i]]); i += 1
    return "、".join(out)

def gear_ja(m):
    sl = slots_ja(m.group("slots"))
    gr = GRADE.get(m.group("grade"))
    if sl is None or gr is None:
        return None
    rest = m.group("rest")
    head = "等級" if rest.startswith("등급") else "装備"
    tail = rest[2:]
    for pat, tpl in TAILS:
        mm = pat.match(tail)
        if mm:
            tail_ja = tpl.format(*mm.groups()) if mm.groups() else tpl
            return (f"<font color='#00aaef'>{sl}</font>：{m.group('lv')}レベル"
                    f"<font color='{m.group('c')}'>{gr}</font>{head}{tail_ja}")
    # 装비 인챈트 / 장비 한계돌파 (에픽 파이어 프리즘用)
    mm = re.match(r"^장비 인챈트 (\d+)단계$", rest)
    if mm:
        return (f"<font color='#00aaef'>{sl}</font>：{m.group('lv')}レベル"
                f"<font color='{m.group('c')}'>{gr}</font>装備エンチャント{mm.group(1)}段階")
    mm = re.match(r"^장비 한계돌파 (\d+)단계$", rest)
    if mm:
        return (f"<font color='#00aaef'>{sl}</font>：{m.group('lv')}レベル"
                f"<font color='{m.group('c')}'>{gr}</font>装備限界突破{mm.group(1)}段階")
    return None

def main():
    fn = "stringfieldenterance"
    emap = {k: v for k, v in json.load(open(
        os.path.join(ROOT, "work", "uifiles", "sfe_map.json"), encoding="utf-8")).items()
        if not k.startswith("_")}
    jp_path = os.path.join(ROOT, "json_weblate", "jp", fn + ".json")
    raw = open(jp_path, encoding="utf-8", newline="").read()
    tail_nl = "\n" if raw.endswith("\n") else ""
    jp = json.loads(raw)
    assert json.dumps(jp, ensure_ascii=False, indent=2) + tail_nl == raw, "RT不一致"
    shutil.copyfile(jp_path, os.path.join(ROOT, "work", "uifiles", fn + ".backup.json"))
    ko = json.load(open(os.path.join(ROOT, "json_weblate", "ko", fn + ".json"), encoding="utf-8"))

    # 行単位 TM(既訳エントリ、接頭辞剥離で両様相登録)
    ptm = {}
    for k, v in jp.items():
        for f, s in v.items():
            if not isinstance(s, str) or not s or PH.search(s) or HG.search(s):
                continue
            kn = ko.get(k, {}).get(f, "")
            if not isinstance(kn, str) or not kn:
                continue
            kl, jl = kn.split("\n"), s.split("\n")
            if len(kl) != len(jl):
                continue
            for a, b in zip(kl, jl):
                pa = PREFIX.match(a); pb = PREFIX.match(b)
                a2 = a[pa.end():] if pa else a
                b2 = b[pb.end():] if pb else b
                if a2.strip():
                    ptm.setdefault(a2, b2)

    def tr_line(line):
        if not line.strip():
            return line
        p = PREFIX.match(line)
        pre = line[:p.end()] if p else ""
        body = line[p.end():] if p else line
        if not body.strip():
            return line
        ja = ptm.get(body) or emap.get(body)
        if ja is None:
            m = GEAR.match(body)
            if m: ja = gear_ja(m)
        if ja is None:
            m = ROUND.match(body)
            if m: ja = f"<font color='#FFD400'>* {m.group('r')}ラウンドアイテムスコア：{m.group('sc')}</font>"
        if ja is None:
            m = REWARD.match(body)
            if m: ja = f"<font color='#00aaef'>報酬獲得回数は$dungeonTitle:{m.group('id')}$ダンジョンと統合されます。</font>"
        return pre + ja if ja is not None else None

    n = fail = skip = 0
    fails = []
    for k, v in jp.items():
        for f, s in list(v.items()):
            if not isinstance(s, str) or not s or not (PH.search(s) or HG.search(s)):
                continue
            kn = ko.get(k, {}).get(f, "")
            if not isinstance(kn, str) or not kn or PH.search(kn):
                skip += 1; continue
            out = []
            ok = True
            for line in kn.split("\n"):
                t = tr_line(line)
                if t is None:
                    ok = False; fails.append((k, f, line[:70])); break
                out.append(t)
            if ok:
                v[f] = "\n".join(out); n += 1
            else:
                fail += 1
    print(f"{fn}: 適用 {n} / 失敗 {fail} / ソース無しスキップ {skip}")
    for x in fails[:15]:
        print("  MISS:", x)
    with open(jp_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(jp, ensure_ascii=False, indent=2) + tail_nl)

if __name__ == "__main__":
    main()
