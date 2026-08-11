# MapleStory 2 日本語ローカライズ — 翻訳データ

MapleStory 2 (MS2) クライアント文字列データの日本語化プロジェクト。
日本版 (JMS2, 2019-2020) で未翻訳のまま残ったデータを、英語版・韓国語版を元に補完する。

- 翻訳方針・ワークフロー: [AGENTS.md](AGENTS.md)(CLAUDE.md と共通)
- 辞書・用語集: [dict/](dict/)(terms.json / proper-nouns.json / style-guide.md)
- 作業ファイル・スクリプト: [work/](work/)([work/README.md](work/README.md) 参照)
- 翻訳データ本体: `json_weblate/{jp,en,ko}/`(Weblate と同期)

## 進捗サマリー(2026-08-11 時点)

| 区分 | ファイル数 | 未翻訳の残り |
|---|---:|---:|
| ✅ 完了(本プロジェクトで翻訳) | 31 | 0 |
| ✅ 完了(JMS2 既訳のみで作業不要) | 30 | 0 |
| 🔄 作業中・未着手 | 3 | 59,262 |

- 「残り」= 未翻訳(プレースホルダー形式またはハングル残存)のうち、KO/EN のいずれかに実文があるもの。
- 「残置(源無し)」= 全言語でプレースホルダーのみ(翻訳元が存在しない)。方針によりそのまま残す。
- 開発者向けメモ等の正当な韓国語フィールドは集計対象外
  (stringcommon の comment/desc 系、maidmanufacturemessage の npc、chapterdescription の isTutorial、addressname の *Kor)。
- 表の再生成: `python work/scripts/status.py`

## 🔄 作業中・未着手

| ファイル | 対象フィールド | 残り | 残置(源無し) | 状況 |
|---|---:|---:|---:|---|
| scriptquest | 70,453 | 45,068 | 46 | 未着手(ストーリー会話。最大のデータ) |
| stringtrigger | 22,710 | 9,576 | 0 | 未着手(トリガーメッセージ) |
| questdescription_final | 26,264 | 4,618 | 62 | 作業中。TM+自動学習+頻出パターン369種で3,919件翻訳済み。残りは一点物 |

## ✅ 完了(本プロジェクトで翻訳したファイル)

翻訳セッションの詳細・使用スクリプトは [work/README.md](work/README.md) を参照。

| ファイル | 対象フィールド | 残り | 残置(源無し) |
|---|---:|---:|---:|
| achievedescription | 3,970 | 0 | 97 |
| achievename | 2,091 | 0 | 0 |
| actionname | 493 | 0 | 0 |
| chapterdescription_epic | 209 | 0 | 0 |
| chapterdescription_famecontents | 22 | 0 | 0 |
| chapterdescription_guide | 79 | 0 | 0 |
| chapterdescription_tutorial | 30 | 0 | 0 |
| chapterdescription_world | 324 | 0 | 3 |
| dungeonmissionname | 479 | 0 | 6 |
| itemname | 70,951 | 0 | 602 |
| kordynamicaction | 325 | 0 | 0 |
| korflash | 3,710 | 0 | 0 |
| koritemdescription | 50,512 | 0 | 597 |
| loadingdescription | 984 | 0 | 8 |
| mapname | 1,716 | 0 | 0 |
| nametagsymboldesc | 35 | 0 | 0 |
| nametagsymboltitle | 36 | 0 | 0 |
| npcfunctionname | 423 | 0 | 1 |
| npcname | 10,268 | 0 | 0 |
| npcnameplural | 8,286 | 0 | 15 |
| npctitle | 731 | 0 | 0 |
| petname | 281 | 0 | 1 |
| recommendcontentsname | 185 | 0 | 0 |
| skillname | 3,111 | 0 | 14 |
| stringadditionaldescription | 14,903 | 0 | 15 |
| stringcommon | 6,376 | 0 | 0 |
| stringfieldenterance | 427 | 0 | 5 |
| stringguide | 1,327 | 0 | 0 |
| stringnpcai | 498 | 0 | 0 |
| titlename | 783 | 0 | 0 |
| usmsubtitletext | 226 | 0 | 0 |

## ✅ 完了(JMS2 既訳のみで追加作業が不要だったファイル)

| ファイル | 対象フィールド | 残り | 残置(源無し) |
|---|---:|---:|---:|
| achievecategoryname | 28 | 0 | 3 |
| achievespecialrewarddescription | 52 | 0 | 0 |
| addressname | 0 | 0 | 0 |
| attendgift | 233 | 0 | 0 |
| categoryname | 429 | 0 | 0 |
| chapterdescription_eventcommon | 5 | 0 | 0 |
| chapterdescription_guild | 6 | 0 | 0 |
| chapterdescription_item | 2 | 0 | 0 |
| continentname | 6 | 0 | 0 |
| dungeonseasonreward | 11 | 0 | 0 |
| guildeventdesc | 4 | 0 | 0 |
| guildhousename | 15 | 0 | 0 |
| guildnpcname | 6 | 0 | 0 |
| interactname | 111 | 0 | 0 |
| islandname | 6 | 0 | 0 |
| jobgroupname | 13 | 0 | 0 |
| jobname | 24 | 0 | 0 |
| keyname | 259 | 0 | 0 |
| maidmanufacturemessage | 189 | 0 | 0 |
| maidpropertystring | 447 | 0 | 0 |
| maplesurvivalskindescription | 18 | 0 | 0 |
| maplesurvivalskinname | 18 | 0 | 0 |
| mapnameportaltooltip | 42 | 0 | 0 |
| maptiledesc | 2 | 0 | 0 |
| petcollectgroupname | 14 | 0 | 0 |
| popupmenu | 28 | 0 | 0 |
| questdispatchscript | 3 | 0 | 0 |
| racename | 12 | 0 | 0 |
| stringcolorpalette | 241 | 0 | 0 |
| stringcolorpalettedesc | 241 | 0 | 0 |

※ addressname が 0 なのは、韓国語が正しい値であるフィールド(`blockNameKor` 等)のみで構成され、集計対象外のため。
