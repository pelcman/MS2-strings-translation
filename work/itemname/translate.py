# -*- coding: utf-8 -*-
"""Rule-based EN->JA translation for MapleStory2 item names, following existing JMS2 conventions."""
import json, re

SC = r"C:\Users\chro\AppData\Local\Temp\claude\c--Users-chro-Desktop-item\716449ef-c413-4587-8ba3-40dde686df10\scratchpad"

CLASS = {
    "Knight": "ナイト", "Berserker": "バーサーカー", "Wizard": "ウィザード",
    "Priest": "プリースト", "Archer": "レンジャー", "Heavy Gunner": "ヘビーガンナー",
    "Thief": "シーフ", "Assassin": "アサシン", "Runeblade": "ルーンブレイダー",
    "Striker": "ストライカー", "Soul Binder": "ソウルバインダー",
}

SERIES = {
    "Antique Arigon": "アンティークアリゴン",
    "Antique Infernuke": "アンティークインフェルヌーク",
    "Tairen Combat": "タイレンコンバット",
    "Tairen Officer": "タイレンオフィサー",
    "Tairen Royal": "タイレンロイヤル",
    "Tairen Rensha": "タイレンレンシャ",
    "Fire Prism": "ファイアプリズム",
    "Humanitas Field": "ヒューマニタスフィールド",
}

# gear piece nouns (KR-informed: Bracers/Gauntlets=글러브, Tassets/Greaves=팬츠, Star=스파이크, Greatsword=라지소드)
PIECE = {
    "Armor": "アーマー", "Blade": "ブレイド", "Boots": "ブーツ", "Bow": "ボウ",
    "Bracers": "グローブ", "Cannon": "キャノン", "Circlet": "サークレット",
    "Greatsword": "ラージソード", "Knife": "ナイフ", "Knuckles": "ナックル",
    "Longsword": "ロングソード", "Pants": "パンツ", "Scepter": "セプター",
    "Shield": "シールド", "Staff": "スタッフ", "Star": "スパイク",
    "Soul": "ソウル", "Tablet": "タブレット", "Claws": "クローハンド",
    "Coat": "コート", "Greaves": "パンツ", "Helmet": "ヘルメット",
    "Axe": "アックス", "History": "ヒストリー", "Spirit": "スピリット",
    "Manual": "マニュアル", "Codex": "法典", "Gauntlets": "グローブ",
    "Tassets": "パンツ", "Vest": "ベスト",
    "Belt": "ベルト", "Cape": "マント", "Earrings": "イヤリング",
    "Necklace": "ネックレス", "Ring": "指輪",
    "Hat": "帽子", "Gloves": "グローブ", "Shoes": "靴",
    "Top": "服(上)", "Bottoms": "服(下)",
}

# box/suffix forms attached to a series
SERIES_SUFFIX = {
    "Weapon Box": "武器ボックス",
    "Weapon Box Fragment": "武器ボックスの欠片",
    "Weapon Random Box": "武器ランダムボックス",
    "Headgear Box": "帽子ボックス",
    "Headgear Box Fragment": "帽子ボックスの欠片",
    "Shoes Box": "靴ボックス",
    "Shoes Box Fragment": "靴ボックスの欠片",
    "Gauntlets Box": "グローブボックス",
    "Gauntlets Box Fragment": "グローブボックスの欠片",
    "Gloves Box": "グローブボックス",
    "Gloves Box Fragment": "グローブボックスの欠片",
    "Bracers Box": "グローブボックス",
    "Bracers Box Fragment": "グローブボックスの欠片",
    "Top/Bottoms Random Box": "服ランダムボックス(上下)",
    "Top/Bottoms Selection Box": "服選択ボックス(上下)",
    "Top/Bottoms Selection Box Fragment": "服選択ボックス(上下)の欠片",
    "Headgear/Gloves/Shoes Selection Box": "帽子/グローブ/靴選択ボックス",
    "Headgear/Gloves/Shoes Selection Box Fragment": "帽子/グローブ/靴選択ボックスの欠片",
    "Accessory Random Box": "アクセサリーランダムボックス",
    "Accessory Random Box Fragment": "アクセサリーランダムボックスの欠片",
    "Accessory Fragment Box": "アクセサリーの欠片ボックス",
    "Accessory Fragment Box Scroll": "アクセサリーの欠片ボックス呪文書",
    "All-in-One Box": "オールインワンボックス",
}

ELITE_PIECE = {
    "Battle Gloves": "バトルグローブ", "Battle Helmet": "バトルヘルメット",
    "Magic Hat": "マジックハット", "Magic Sleeve": "マジックスリーブ",
    "Marshall Circlet": "マーシャルサークレット", "Marshall Gloves": "マーシャルグローブ",
    "Scout Gloves": "スカウトグローブ", "Scout Hat": "スカウトハット",
    "Stealth Bangle": "スニーキングブレスレット", "Stealth Mask": "スニーキングオブジェクト",
}

SKIN_SLOT = {
    "Top": "服(上)", "Bottoms": "服(下)", "Bottom": "服(下)", "Pants": "服(下)",
    "Skirt": "服(下)", "Drop Bottoms": "服(下)",
    "Hat": "帽子", "Earrings": "イヤリング",
    "Face Decoration": "顔飾り", "Face Ornament": "顔飾り",
    "Entrance": "入場式", "Entry": "入場式", "Fame": "入場式", "Intro Entrance": "入場式",
    "Eye Decoration": "目の飾り",
    "Gloves": "グローブ", "Shoes": "靴",
}
SKIN_PREFIX = {
    "Skin": "スキン",
    "Street Rapper": "ストリートラッパー",
    "Save SF Dress": "セーブSFドレス",
    "Vocaloid Concept": "ボーカロイドコンセプト",
}
GENDER = {"F": "(女)", "M": "(男)", "Female": "(女)", "Male": "(男)"}

DUNGEON = {
    "Ancient Aetherine Mine": "古代エネル鉱山",
    "Hall of Conspiracy": "陰謀の殿堂",
    "Hidden Hangar": "隠された格納庫",
    "Illusory Blue Shadow Cave": "幻影の青い影洞窟",
    "Illusory Horus's Nest": "幻影のホルスの巣",
    "Renegade Timaion": "裏切り者ティマイオン",
    "Ruckus Black Bean Playground": "ドタバタブラックビーン遊び場",
    "Showdown with Infernog": "インフェルノック最後の決戦",
}

BRIDE_ADJ = {
    "Affectionate": "優しい", "Blessed": "祝福された", "Considerate": "思いやりのある",
    "Fresh": "初々しい", "Gentle Moonlight": "ほのかな月明かりの", "Radiant": "輝く",
    "Serious": "真剣な", "Splendid": "華麗な", "Strong": "頼もしい",
    "Sunshine-Filled": "陽射しあふれる", "Trusted": "信頼される", "Warm": "温かい",
}
COUPLE_ADJ = {
    "Blessed": "祝福された", "Considerate": "思いやりのある", "Fresh": "初々しい",
    "Loving": "優しい", "Serious": "真剣な", "Shining": "輝く",
    "Soft Moonlight": "ほのかな月明かりの", "Splendid": "華麗な", "Strong": "頼もしい",
    "Sunlit": "陽射しあふれる", "Trusting": "信頼される", "Warm": "温かい",
}

RARITY = {"Epic": "エクセレント", "Legendary": "レジェンダリー", "Ascendant": "エピック"}
RR_SLOT = {"Main Hand": "片手", "Two-handed": "両手", "Accessory": "アクセサリー", "Armor": "防具"}

series_alt = "|".join(sorted(SERIES, key=len, reverse=True))
class_alt = "|".join(sorted(CLASS, key=len, reverse=True))
piece_alt = "|".join(sorted(PIECE, key=len, reverse=True))
suffix_alt = "|".join(sorted(SERIES_SUFFIX, key=len, reverse=True))
elite_alt = "|".join(sorted(ELITE_PIECE, key=len, reverse=True))
slot_alt = "|".join(sorted(SKIN_SLOT, key=len, reverse=True))
dungeon_alt = "|".join(re.escape(d) for d in sorted(DUNGEON, key=len, reverse=True))


def translate(en):
    # ---- class'd series gear: "Knight's Tairen Combat Boots [Scroll]"
    m = re.fullmatch(rf"({class_alt})'s ({series_alt}) ({piece_alt})( Scroll)?", en)
    if m:
        cl, se, pc, sc = m.groups()
        return SERIES[se] + PIECE[pc] + f"({CLASS[cl]})" + ("呪文書" if sc else "")

    # ---- series gear w/ class parens: "Fire Prism Boots (Archer)"
    m = re.fullmatch(rf"({series_alt}) ({piece_alt}) \(({class_alt})\)", en)
    if m:
        se, pc, cl = m.groups()
        return SERIES[se] + PIECE[pc] + f"({CLASS[cl]})"

    # ---- series box/suffix forms
    m = re.fullmatch(rf"({series_alt}) ({suffix_alt})", en)
    if m:
        se, sf = m.groups()
        return SERIES[se] + SERIES_SUFFIX[sf]

    # ---- plain series gear: "Tairen Combat Boots [Scroll]" / "X Fragment"
    m = re.fullmatch(rf"({series_alt}) ({piece_alt})( Scroll| Fragment)?", en)
    if m:
        se, pc, sf = m.groups()
        tail = {"" : "", " Scroll": "呪文書", " Fragment": "の欠片"}[sf or ""]
        return SERIES[se] + PIECE[pc] + tail

    # ---- PC Cafe elite adventurer
    m = re.fullmatch(rf"\(PC Cafe\) Elite Adventurer ({elite_alt}) \(({class_alt})\)", en)
    if m:
        pc, cl = m.groups()
        return f"(ネットカフェ) エリートアドベンチャー{ELITE_PIECE[pc]}({CLASS[cl]})"
    m = re.fullmatch(rf"\(PC Cafe\) ({class_alt})'s Exceptional Adventuring Leggings", en)
    if m:
        return f"(ネットカフェ) エリートアドベンチャーバトルサイド({CLASS[m.group(1)]})"
    m = re.fullmatch(rf"\(PC Cafe\) ({class_alt})'s Exceptional Adventuring Pants", en)
    if m:
        return f"(ネットカフェ) エリートアドベンチャーマーシャルパンツ({CLASS[m.group(1)]})"
    m = re.fullmatch(rf"\(PC Cafe\) 엘리트 어드벤쳐 마샬 셔츠 \(({class_alt})\)", en)
    if m:
        return f"(ネットカフェ) エリートアドベンチャーマーシャルシャツ({CLASS[m.group(1)]})"
    m = re.fullmatch(rf"\(PC Cafe\) 엘리트 어드벤쳐 배틀 코트 \(({class_alt})\)", en)
    if m:
        return f"(ネットカフェ) エリートアドベンチャーバトルコート({CLASS[m.group(1)]})"

    # ---- skins: "02/15 Skin Top (F)", "Street Rapper Fame (M)", etc.
    m = re.fullmatch(rf"(\d\d/\d\d) Skin (?:({slot_alt})) \((F|M|Female|Male)\)", en)
    if m:
        d, sl, g = m.groups()
        return f"{d} スキン{SKIN_SLOT[sl]}{GENDER[g]}"
    m = re.fullmatch(rf"(Street Rapper|Save SF Dress|Vocaloid Concept(?: Intro| Drop)?) (?:({slot_alt})) \((F|M|Female|Male)\)", en)
    if m:
        p, sl, g = m.groups()
        p = p.replace(" Intro", "").replace(" Drop", "")
        return f"{SKIN_PREFIX[p]}{SKIN_SLOT[sl]}{GENDER[g]}"
    m = re.fullmatch(rf"Sample (?:({slot_alt})) \(Capsule Gacha Skin\)", en)
    if m:
        return f"サンプル{SKIN_SLOT[m.group(1)]}(カプセルガチャスキン)"

    # ---- rank reward boxes
    m = re.fullmatch(rf"({dungeon_alt}) (S\+|S|A|B|C)[- ]?[Rr]ank Reward Box", en)
    if m:
        return f"{DUNGEON[m.group(1)]}{m.group(2)}ランク報酬ボックス"
    m = re.fullmatch(r"Queen Bean Rumble Round (\d+) Reward Box", en)
    if m:
        return f"クイーンビーンランブル{m.group(1)}ラウンド報酬ボックス"

    # ---- titles
    m = re.fullmatch(r"Title: (.+) (Bride|Groom)", en)
    if m and m.group(1) in BRIDE_ADJ:
        return "称号：" + BRIDE_ADJ[m.group(1)] + ("花嫁" if m.group(2) == "Bride" else "花婿")
    m = re.fullmatch(r"(.+) Couple Title Selection Box", en)
    if m and m.group(1) in COUPLE_ADJ:
        return COUPLE_ADJ[m.group(1)] + "夫婦の称号選択ボックス"

    # ---- re-roller / socket family
    m = re.fullmatch(r"(Epic|Legendary|Ascendant) Bonus( Value)? Re-roller \(Lv\. 70/(Main Hand|Two-handed|Accessory|Armor)\)", en)
    if m:
        r, val, sl = m.groups()
        word = "オプション数値変更券" if val else "オプション変更券"
        return f"{RARITY[r]}{word}(LV70/{RR_SLOT[sl]})"
    m = re.fullmatch(r"(Epic|Legendary|Ascendant) (Belt|Cape|Earrings|Necklace|Ring) Bonus Value Re-roller \(Lv\. 70\)", en)
    if m:
        r, pc = m.groups()
        return f"{RARITY[r]}{PIECE[pc]}オプション数値変更券(LV70)"
    m = re.fullmatch(r"(Epic|Legendary|Ascendant) (\d)-Socket Conversion Scroll \(Lv\. 70\)", en)
    if m:
        r, n = m.groups()
        return f"{RARITY[r]}{n}ソケット変換呪文書(LV70)"
    m = re.fullmatch(r"Legendary (Gloves|Headgear|Shoes) Fragment Selection Box", en)
    if m:
        sl = {"Gloves": "グローブ", "Headgear": "帽子", "Shoes": "靴"}[m.group(1)]
        return f"レジェンダリー{sl}の欠片選択ボックス"
    if en == "Legendary Top/Bottoms Fragment Selection Box":
        return "レジェンダリー服(上下)の欠片選択ボックス"

    return None


def main():
    targets = json.load(open(SC + r"\targets.json", encoding="utf-8"))
    uniq = sorted({v["en"] for v in targets.values()})
    ko_by_en = {}
    for v in targets.values():
        ko_by_en.setdefault(v["en"], v["ko"])

    auto = {}
    unresolved = []
    for name in uniq:
        t = translate(name)
        if t:
            auto[name] = t
        else:
            unresolved.append(name)

    print(f"unique: {len(uniq)}, auto: {len(auto)}, unresolved: {len(unresolved)}")
    with open(SC + r"\auto_map.json", "w", encoding="utf-8") as f:
        json.dump(auto, f, ensure_ascii=False, indent=1)
    with open(SC + r"\unresolved.txt", "w", encoding="utf-8") as f:
        for n in unresolved:
            f.write(f"{n}  //KO// {ko_by_en.get(n,'')}\n")

if __name__ == "__main__":
    main()
