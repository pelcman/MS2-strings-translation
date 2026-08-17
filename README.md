# MapleStory 2 日本語ローカライズ — 翻訳データ

MapleStory 2 (MS2) クライアント文字列データの日本語化プロジェクト。
日本版 (JMS2, 2019-2020) で未翻訳のまま残ったデータを、英語版・韓国語版を元に補完する。

- 翻訳方針・ワークフロー: [AGENTS.md](AGENTS.md)(CLAUDE.md と共通)
- 辞書・用語集: [dict/](dict/)(terms.json / proper-nouns.json / style-guide.md)
- 作業ファイル・スクリプト: [work/](work/)([work/README.md](work/README.md) 参照)
- 翻訳データ本体: `json_weblate/{jp,en,ko}/`(Weblate と同期)

## 進捗サマリー(2026-08-17 時点)

| 区分 | 件数 |
|---|---:|
| 対象フィールド総数(64ファイル) | 295,975 |
| **翻訳可能な未訳** | **0** |
| **jp にキーが無かったもの(補完済み)** | **0** |
| 残置(全言語で原文が存在せず翻訳不可) | 1,460 |

**翻訳可能な文字列はすべて日本語化済み。**

### 用語の定義

- **残り** = 未翻訳(プレースホルダー形式またはハングル残存)のうち、KO/EN のいずれかに実文があるもの
- **欠落キー** = ko に実文があるのに jp にキーが無いもの。Weblate 上に翻訳枠が存在しないため、
  キーを追加しないと翻訳できない。XML に変換すると `MAPNAME_02020001_NAME:[F]...` のような
  生の文字列がゲーム内に表示される。2026-08 のセッションで全件(44,276)を補完した
- **残置(源無し)** = 全言語でプレースホルダーのみ(翻訳元が存在しない)。AGENTS.md 方針4によりそのまま残す
- 開発者向けメモ等の正当な韓国語フィールドは集計対象外
  (stringcommon の comment/desc 系、maidmanufacturemessage の npc、chapterdescription の isTutorial、
  addressname の *Kor、stringtrigger・scriptquest の npc(話者ID)と type(トリガー関数名)。
  いずれも JP・EN とも原文のまま)
- 文字集めイベントのアイテム(1文字ずつ集めて文章にするもの)は翻訳せず原文の文字を維持する

## 検証スクリプト

| スクリプト | 用途 |
|---|---|
| `python work/scripts/status.py` | 下の進捗表を再生成 |
| `python work/scripts/coverage.py` | jp にキーが無いものを含む実カバー率 |
| `python work/scripts/audit.py` | 6種類の未訳パターンを検出(プレースホルダー/ハングル残存/ダミー値/KO・EN丸写し/キー欠落) |
| `python work/scripts/ph_report.py` | プレースホルダーのうち翻訳元が存在するものを抽出 |
| `python work/scripts/audit_numbers.py` | KO と JA で数値が食い違うエントリを検出 |
| `python work/scriptquest/progress.py` | scriptquest の進捗(読み取り専用) |

## ファイル別の状況

| ファイル | 対象フィールド | 残り | 欠落キー | 残置(源無し) | 状態 |
|---|---:|---:|---:|---:|---|
| achievecategoryname | 28 | 0 | 0 | 3 | ✅ 完了 |
| achievedescription | 4,513 | 0 | 0 | 97 | ✅ 完了 |
| achievename | 2,250 | 0 | 0 | 0 | ✅ 完了 |
| achievespecialrewarddescription | 52 | 0 | 0 | 0 | ✅ 完了 |
| actionname | 894 | 0 | 0 | 0 | ✅ 完了 |
| addressname | 0 | 0 | 0 | 0 | ✅ 完了 |
| attendgift | 233 | 0 | 0 | 0 | ✅ 完了 |
| categoryname | 765 | 0 | 0 | 0 | ✅ 完了 |
| chapterdescription_epic | 211 | 0 | 0 | 0 | ✅ 完了 |
| chapterdescription_eventcommon | 12 | 0 | 0 | 0 | ✅ 完了 |
| chapterdescription_famecontents | 22 | 0 | 0 | 0 | ✅ 完了 |
| chapterdescription_guide | 80 | 0 | 0 | 0 | ✅ 完了 |
| chapterdescription_guild | 6 | 0 | 0 | 0 | ✅ 完了 |
| chapterdescription_item | 2 | 0 | 0 | 0 | ✅ 完了 |
| chapterdescription_tutorial | 30 | 0 | 0 | 0 | ✅ 完了 |
| chapterdescription_world | 325 | 0 | 0 | 3 | ✅ 完了 |
| continentname | 6 | 0 | 0 | 0 | ✅ 完了 |
| dungeonmissionname | 550 | 0 | 0 | 6 | ✅ 完了 |
| dungeonseasonreward | 11 | 0 | 0 | 0 | ✅ 完了 |
| guildeventdesc | 4 | 0 | 0 | 0 | ✅ 完了 |
| guildhousename | 15 | 0 | 0 | 0 | ✅ 完了 |
| guildnpcname | 6 | 0 | 0 | 0 | ✅ 完了 |
| interactname | 111 | 0 | 0 | 0 | ✅ 完了 |
| islandname | 6 | 0 | 0 | 0 | ✅ 完了 |
| itemname | 77,596 | 0 | 0 | 602 | ✅ 完了 |
| jobgroupname | 13 | 0 | 0 | 0 | ✅ 完了 |
| jobname | 24 | 0 | 0 | 0 | ✅ 完了 |
| keyname | 259 | 0 | 0 | 0 | ✅ 完了 |
| kordynamicaction | 407 | 0 | 0 | 0 | ✅ 完了 |
| korflash | 3,710 | 0 | 0 | 0 | ✅ 完了 |
| koritemdescription | 66,356 | 0 | 0 | 597 | ✅ 完了 |
| loadingdescription | 1,007 | 0 | 0 | 8 | ✅ 完了 |
| maidmanufacturemessage | 189 | 0 | 0 | 0 | ✅ 完了 |
| maidpropertystring | 447 | 0 | 0 | 0 | ✅ 完了 |
| maplesurvivalskindescription | 18 | 0 | 0 | 0 | ✅ 完了 |
| maplesurvivalskinname | 18 | 0 | 0 | 0 | ✅ 完了 |
| mapname | 1,861 | 0 | 0 | 0 | ✅ 完了 |
| mapnameportaltooltip | 42 | 0 | 0 | 0 | ✅ 完了 |
| maptiledesc | 2 | 0 | 0 | 0 | ✅ 完了 |
| nametagsymboldesc | 75 | 0 | 0 | 0 | ✅ 完了 |
| nametagsymboltitle | 74 | 0 | 0 | 0 | ✅ 完了 |
| npcfunctionname | 735 | 0 | 0 | 1 | ✅ 完了 |
| npcname | 10,503 | 0 | 0 | 0 | ✅ 完了 |
| npcnameplural | 9,282 | 0 | 0 | 15 | ✅ 完了 |
| npctitle | 1,282 | 0 | 0 | 0 | ✅ 完了 |
| petcollectgroupname | 14 | 0 | 0 | 0 | ✅ 完了 |
| petname | 282 | 0 | 0 | 1 | ✅ 完了 |
| popupmenu | 32 | 0 | 0 | 0 | ✅ 完了 |
| questdescription_final | 31,687 | 0 | 0 | 61 | ✅ 完了 |
| questdispatchscript | 3 | 0 | 0 | 0 | ✅ 完了 |
| racename | 12 | 0 | 0 | 0 | ✅ 完了 |
| recommendcontentsname | 185 | 0 | 0 | 0 | ✅ 完了 |
| scriptquest | 40,348 | 0 | 0 | 32 | ✅ 完了 |
| skillname | 3,794 | 0 | 0 | 14 | ✅ 完了 |
| stringadditionaldescription | 16,996 | 0 | 0 | 15 | ✅ 完了 |
| stringcolorpalette | 241 | 0 | 0 | 0 | ✅ 完了 |
| stringcolorpalettedesc | 241 | 0 | 0 | 0 | ✅ 完了 |
| stringcommon | 6,605 | 0 | 0 | 0 | ✅ 完了 |
| stringfieldenterance | 756 | 0 | 0 | 5 | ✅ 完了 |
| stringguide | 1,333 | 0 | 0 | 0 | ✅ 完了 |
| stringnpcai | 498 | 0 | 0 | 0 | ✅ 完了 |
| stringtrigger | 7,787 | 0 | 0 | 0 | ✅ 完了 |
| titlename | 899 | 0 | 0 | 0 | ✅ 完了 |
| usmsubtitletext | 230 | 0 | 0 | 0 | ✅ 完了 |

※ addressname が 0 なのは、韓国語が正しい値であるフィールド(`blockNameKor` 等)のみで構成され、集計対象外のため。
