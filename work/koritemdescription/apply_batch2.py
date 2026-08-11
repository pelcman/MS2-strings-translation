# -*- coding: utf-8 -*-
"""koritemdescription バッチ2: TM完全一致 → ルール生成 → 手作りマップ の3段で適用する。

対象クラスタ:
- TM: 全ファイル横断の KO→JA 完全一致(既訳流用)
- 合成魔法呪文書 (470)
- CNペットカプセル枠 (~143)
- エンチャントルーン +9/+11 (32)
- オプション数値変更券 70LV (12)
- クイーンビーンランブル報酬ボックス (13)
- 武器発動効果 [古代の力]/[エネルトリガー]/[砲撃支援]/[きらめく青い光] (ルール生成)
- crafted2_ja.json (SCROLL/QBR-1..4/PROC-1,27/PETKO)

使い方: python work/koritemdescription/apply_batch2.py
"""
import json, os, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JP = os.path.join(ROOT, "json_weblate", "jp", "koritemdescription.json")
KO = os.path.join(ROOT, "json_weblate", "ko", "koritemdescription.json")
WORK = os.path.join(ROOT, "work", "koritemdescription")
PH = re.compile(r"(^|\s)[A-Z0-9$]+(_[A-Z0-9$]+)+(:\[F\]\S*)?($|\s)")
HG = re.compile(r"[가-힯]")

def dump(d): return json.dumps(d, ensure_ascii=False, indent=2) + "\n"

# --- ルール生成 ---
SYNTH = re.compile(r"^신비한 합성 마법이 담긴 주문서로 재료를 모아 \$item:(\d+)\$\$pp:를,을\$( 2개)? 만들 수 있다\.$")
# CNペット枠は前方/後方一致で判定(区切り記号は全角カンマ U+FF0C・中黒 U+00B7)
PETCN_PRE = ("<font color='#9FC93C'>便利功能\\n · 自动复活墓碑\\n · 自动药水恢复"
             "\\n · 自动拾取道具\\n<font size='3'> </font>\\n</font>存储")
PETCN_SUF = "召唤信息的道具。平时以物品形态待在其他次元空间，受到角色召唤便会出现。"

class _PetMatcher:
    def match(self, s):
        # 「存储X召唤信息」のほか「存储有X召唤信息」変種もある。名前部分は使わず
        # jp itemname から取るため、枠の前半と末尾だけ確認する
        return (s.startswith(PETCN_PRE[:-2]) and s.endswith(PETCN_SUF)
                and "召唤信息的道具" in s)

PETCN = _PetMatcher()
RUNE = re.compile(r"^더블클릭으로 룬스톤을 사용해 장비를 인챈트 할 수 있다\.\\n인챈트 가능한 노멀, 레어, 엘리트, 엑설런트, 레전더리, 에픽 등급 (한손 무기|쌍수 무기|양손 무기|모자|상의|하의|장갑|신발) 장비에만 사용할 수 있으며, 사용 시 100% 확률로 해당 아이템이 \+(\d+) 인챈트 아이템이 된다\.$")
OPT = re.compile(r"^더블클릭으로 옵션 변경권을 사용할 수 있다\.\\n\\n<font color=\"#FFFFFF\">70레벨 (레전더리|에픽|엑설런트) 등급의 (귀고리|망토|목걸이|반지|벨트|모자, 상의, 하의, 한벌, 장갑, 신발)에만 사용할 수 있으며, 사용 시 추가 옵션 수치만 변경된다\.</font>\\n\\n<font color=\"#FF5F5F\">옵션 변경권을 통하여 옵션 변경을 할 경우에는 추가 옵션 변경 횟수가 증가되지 않습니다\.\\n추가 옵션이 없거나 추가 옵션 변경 횟수가 표시되지 않는 아이템은 사용할 수 없습니다\.\\n옵션 변경권을 통하여 옵션을 변경할 경우에는 동일한 수치가 나올 수 있습니다\.</font>$")
QBRN = re.compile(r"^퀸크빌 럼블 (\d+)라운드를 클리어하면 획득할 수 있는 상자이다\. 단, 주 1회만 획득할 수 있으며 라운드 클리어 시가 아닌 던전 결과 단계에서 획득할 수 있다\.$")
PROCA = re.compile(r"^<font color='#ff8ae5' size='14'>\[(고대의 힘|에네르 트리거)\]\\n물리/마법 대미지가 8% 증가하고 (.+?) 타격 시 (\d+)초 동안 전투력이 1000 증가한다\. 전투력 증가 효과는 10초 내 재발동하지 않는다\. (?:이 효과는 (.+?) )?전장 및 투기장에서 발동하지 않는다\.</font>$")
PROCB = re.compile(r"^<font color='#ff8ae5' size='14'>\[포격 지원\]\\n타격 시 5초 마다 게오르크 군이 주변 적에게 685% 대미지의 포격을 입힌다\. (?:(.+?) )?전장 및 투기장에서는 효과가 적용되지 않는다\.$")
PROCC = re.compile(r"^<font color='#ff8ae5' size='14'>\[영롱한 푸른빛\]\\n블루라펜타의 힘이 점점 쌓여 10초마다 한번씩 전투력이 (\d+) 만큼 증가한 대미지를 입힙니다\.$")

SLOT = {"한손 무기": "片手武器", "쌍수 무기": "双手武器", "양손 무기": "両手武器",
        "모자": "帽子", "상의": "服(上)", "하의": "服(下)", "장갑": "グローブ", "신발": "靴"}
GRADE = {"레전더리": "レジェンダリー", "에픽": "エピック", "엑설런트": "エクセレント"}
PART = {"귀고리": "イヤリング", "망토": "マント", "목걸이": "ネックレス", "반지": "指輪",
        "벨트": "ベルト", "모자, 상의, 하의, 한벌, 장갑, 신발": "帽子、服(上)、服(下)、全身服、グローブ、靴"}
SKILL = {"서먼 소드": "サモンソード", "절단": "切断", "허리케인 경보": "ハリケーン警報",
         "홀리 익스텐션": "ホーリーエクステンション", "피닉스 스트라이크 샷": "フェニックスストライクショット",
         "부비 트랩 MK2": "ブービートラップMK2", "포이즌 플랜": "ポイズンプラン",
         "비기 : 파괴": "秘技：破壊", "루나틱 플래쉬": "ルナティックフラッシュ",
         "얼티밋 러쉬": "アルティメットラッシュ", "힘의 해방": "力の解放",
         "공격 태세 돌파": "攻撃態勢突破", "더스크 폴": "ダスクフォール",
         "와일드 파이어": "ワイルドファイア", "신성한 힘": "神聖な力",
         "이글 스쿼드": "イーグルスクワッド", "메슬라 코일": "メスラコイル",
         "임기응변": "臨機応変", "비술 : 붕괴": "秘術：崩壊",
         "게이트 오브 블레이드": "ゲートオブブレイド",
         "얼티밋 디스트로이 킥": "アルティメットデストロイキック", "완벽한 선율": "完璧な旋律",
         "사나운 불길": "荒れ狂う炎", "가스 중독": "ガス中毒"}
GEAR = {"안티크 인페누크 쉴드": "アンティークインフェルヌークシールド",
        "안티크 인페누크 히스토릭": "アンティークインフェルヌークヒストリー",
        "타이렌 커맨더 컴뱃 쉴드": "タイレンオフィサーシールド",
        "타이렌 커맨더 컴뱃 메뉴얼": "タイレンオフィサーマニュアル",
        "타이렌 로열 나이프": "タイレンロイヤルナイフ", "타이렌 로열 스파이크": "タイレンロイヤルスパイク",
        "타이렌 로열 법전": "タイレンロイヤル法典", "타이렌 로열 소드": "タイレンロイヤルロングソード",
        "타이렌 로열 쉴드": "タイレンロイヤルシールド", "타이렌 로열 홀": "タイレンロイヤルセプター"}
HEAD = {"고대의 힘": "古代の力", "에네르 트리거": "エネルトリガー"}

def cond_ja(c):
    m = re.match(r"^(.+?) 상태의 적을$", c)
    if m and m.group(1) in SKILL: return SKILL[m.group(1)] + "状態の敵を"
    m = re.match(r"^(.+?)[을를] 습득한 상태에서$", c)
    if m and m.group(1) in SKILL: return SKILL[m.group(1)] + "を習得した状態で"
    m = re.match(r"^(.+?) 습득 상태에서$", c)
    if m and m.group(1) in SKILL: return SKILL[m.group(1)] + "を習得した状態で"
    m = re.match(r"^(.+?) 상태에서$", c)
    if m and m.group(1) in SKILL: return SKILL[m.group(1)] + "状態で"
    m = re.match(r"^(.+?)[로으]로?$", c)  # 〜로 / 〜으로
    if m:
        base = re.sub(r"[로으]로?$", "", c).rstrip()
        base = re.sub(r"(으로|로)$", "", c).strip()
    for k in sorted(SKILL, key=len, reverse=True):
        if c == k + "로" or c == k + "으로": return SKILL[k] + "で"
    return None

def extra_ja(e):
    if e is None: return "この効果は戦場および闘技場では発動しない。"
    if e == "양손에 동일한 장비를 착용해야 활성화 되며":
        return "この効果は両手に同一の装備を着用した場合のみ活性化され、戦場および闘技場では発動しない。"
    m = re.match(r"^(.+?)[을를] 함께 사용해야 활성화 되며$", e)
    if m and m.group(1) in GEAR:
        return "この効果は" + GEAR[m.group(1)] + "と一緒に使用した場合のみ活性化され、戦場および闘技場では発動しない。"
    return None

def extra_b_ja(e):
    if e is None: return ""
    m = re.match(r"^양손에 (.+?)[을를] 장착해야 활성화 된다\.$", e)
    if m and m.group(1) in GEAR:
        return "両手に" + GEAR[m.group(1)] + "を装着した場合のみ活性化される。"
    m = re.match(r"^이 효과는 (.+?)[과와] 함께 [사새]용해야 활성화 된다\.$", e)
    if m and m.group(1) in GEAR:
        return "この効果は" + GEAR[m.group(1)] + "と一緒に使用した場合のみ活性化される。"
    return None

def rule_ja(src, key, itemjp):
    m = SYNTH.match(src)
    if m:
        n = "を2個" if m.group(2) else "を"
        return f"神秘的な合成魔法が宿る呪文書。材料を集めると$item:{m.group(1)}${n}作ることができる。"
    if PETCN.match(src):
        name = itemjp.get(key, {}).get("name", "")
        if not name or PH.search(name) or HG.search(name): return None
        return ("<font color='#9FC93C'>便利機能\\n・碑石自動復活\\n・自動ポーション回復\\n・自動アイテム拾得"
                "\\n<font size='3'> </font>\\n</font>" + name +
                "の召喚情報を保存しているアイテム。普段はアイテムの形で異次元にいるが、キャラクターが召喚すると現れる。")
    # CNペット枠の変種: ペットスキル(地上ライディング)付き / ペットカバン行付き
    if src.startswith("<font color='#9FC93C'>便利功能") and "召唤信息的道具" in src:
        name = itemjp.get(key, {}).get("name", "")
        if not name or PH.search(name) or HG.search(name): return None
        tail = (name + "の召喚情報を保存しているアイテム。普段はアイテムの形で異次元にいるが、"
                "キャラクターが召喚すると現れる。")
        if "宠物技能" in src and "陆地坐骑移动速度将提高5%" in src:
            return ("<font color='#9FC93C'>便利機能\\n・碑石自動復活\\n・自動ポーション回復\\n・自動アイテム拾得"
                    "\\n\\nペットスキル\\n・ペットを召喚した状態で、地上ライディングの移動速度が5%増加する。"
                    "\\n<font size='3'> </font>\\n</font>" + tail)
        m2 = re.search(r"宠物背包(\d+)格", src)
        if m2:
            return ("<font color='#9FC93C'>便利機能\\n・碑石自動復活\\n・自動ポーション回復\\n・自動アイテム拾得"
                    f"\\nペットカバン{m2.group(1)}マス<font size='3'> </font>\\n</font>" + tail)
        return None
    m = RUNE.match(src)
    if m:
        return ("ダブルクリックでルーンストーンを使用して装備をエンチャントできる。\\nエンチャント可能なノーマル、レア、エリート、"
                f"エクセレント、レジェンダリー、エピック等級の{SLOT[m.group(1)]}装備にのみ使用でき、"
                f"使用すると100%の確率で該当アイテムが+{m.group(2)}エンチャントアイテムになる。")
    m = OPT.match(src)
    if m:
        return ("ダブルクリックでオプション変更券を使用できる。\\n\\n<font color=\"#FFFFFF\">"
                f"70レベルの{GRADE[m.group(1)]}等級の{PART[m.group(2)]}にのみ使用できる。"
                "使用すると追加オプションの数値のみ変更される。</font>\\n\\n<font color=\"#FF5F5F\">"
                "オプション変更券でオプションを変更する場合、追加オプション変更回数は増加しません。\\n"
                "追加オプションがないアイテムや、追加オプション変更回数が表示されないアイテムには使用できません。\\n"
                "オプション変更券でオプションを変更する場合、同じ数値が出る可能性があります。</font>")
    m = QBRN.match(src)
    if m:
        return (f"クイーンビーンランブル{m.group(1)}ラウンドをクリアすると獲得できるボックス。"
                "ただし、週1回のみ獲得でき、ラウンドクリア時ではなくダンジョン結果の段階で獲得できる。")
    m = PROCA.match(src)
    if m:
        c = cond_ja(m.group(2)); e = extra_ja(m.group(4))
        if c is None or e is None: return None
        return (f"<font color='#ff8ae5' size='14'>[{HEAD[m.group(1)]}]\\n物理/魔法ダメージが8%増加し、"
                f"{c}打撃時、{m.group(3)}秒間戦闘力が1000増加する。戦闘力増加効果は10秒以内には再発動しない。{e}</font>")
    m = PROCB.match(src)
    if m:
        e = extra_b_ja(m.group(1))
        if e is None: return None
        return ("<font color='#ff8ae5' size='14'>[砲撃支援]\\n打撃時、5秒ごとにゲオルク軍が周囲の敵に"
                f"685%ダメージの砲撃を加える。{e}戦場および闘技場では効果が適用されない。")
    m = PROCC.match(src)
    if m:
        return ("<font color='#ff8ae5' size='14'>[きらめく青い光]\\nブルーラペンタの力が少しずつ積み重なり、"
                f"10秒ごとに1回、戦闘力が{m.group(1)}増加したダメージを与える。")
    return None

def main():
    raw = open(JP, encoding="utf-8", newline="").read()
    jp = json.loads(raw)
    assert dump(jp) == raw, "ラウンドトリップ不一致"
    shutil.copyfile(JP, os.path.join(WORK, "koritemdescription.backup.json"))
    ko = json.load(open(KO, encoding="utf-8"))
    itemjp = json.load(open(os.path.join(ROOT, "json_weblate", "jp", "itemname.json"), encoding="utf-8"))

    # TM(全ファイル横断・完全一致)
    tm = {}
    for fn in os.listdir(os.path.join(ROOT, "json_weblate", "jp")):
        try:
            j2 = json.load(open(os.path.join(ROOT, "json_weblate", "jp", fn), encoding="utf-8"))
            k2 = json.load(open(os.path.join(ROOT, "json_weblate", "ko", fn), encoding="utf-8"))
        except FileNotFoundError:
            continue
        for k, v in j2.items():
            kv = k2.get(k, {})
            for f, s in v.items():
                if not isinstance(s, str) or not s or PH.search(s) or HG.search(s): continue
                src = kv.get(f, "")
                if isinstance(src, str) and src and not PH.search(src):
                    tm.setdefault(src, s)

    # 手作りマップ: clusters2.txt のタグ→KO と crafted2_ja.json のタグ→JA
    srcs = {}
    tag = None
    for line in open(os.path.join(WORK, "clusters2.txt"), encoding="utf-8"):
        if line.startswith("@@"):
            tag = line.split()[0][2:]
        elif line.startswith("KO|") and tag:
            srcs[tag] = line[3:].rstrip("\n").replace("⏎", "\n")
    crafted = {k: v for k, v in json.load(
        open(os.path.join(WORK, "crafted2_ja.json"), encoding="utf-8")).items() if not k.startswith("_")}
    crafted_src = {}
    for t, ja in crafted.items():
        assert t in srcs, f"clusters2.txt にタグ {t} が無い"
        crafted_src[srcs[t]] = ja

    stats = {"tm": 0, "rule": 0, "crafted": 0}
    unresolved = []
    for key, entry in jp.items():
        kv = ko.get(key, {})
        for f in ("tooltipDescription", "guideDescription"):
            s = entry.get(f)
            if not isinstance(s, str) or not s or not PH.search(s): continue
            src = kv.get(f, "")
            if not isinstance(src, str) or not src or PH.search(src): continue
            if src in tm:
                entry[f] = tm[src]; stats["tm"] += 1
            elif src in crafted_src:
                entry[f] = crafted_src[src]; stats["crafted"] += 1
            else:
                ja = rule_ja(src, key, itemjp)
                if ja is not None:
                    entry[f] = ja; stats["rule"] += 1
                elif SYNTH.match(src) or PETCN.match(src) or PROCA.match(src) or PROCB.match(src):
                    unresolved.append((key, f, src[:60]))

    print("適用:", stats, "計", sum(stats.values()))
    if unresolved:
        print("！ルール該当だが未解決:", len(unresolved))
        for u in unresolved[:10]: print("  ", u)
    with open(JP, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dump(jp))
    print("書き込み完了")

if __name__ == "__main__":
    main()
