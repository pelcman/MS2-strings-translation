# MapleStory 2 日本語ローカライズプロジェクト

MapleStory 2 (MS2) のゲームクライアント文字列データを日本語化するプロジェクト。
日本版 (JMS2, 2019-2020運営) は未翻訳のまま実装されなかったデータが多く、それを英語版・韓国語版を元に補完する。
翻訳データは Weblate で管理されており、`json_weblate/` 以下がその実データ。

## ディレクトリ構成

```
MS2-strings-translation/
├── AGENTS.md / CLAUDE.md        # 本ドキュメント(翻訳方針)
├── json_weblate/                # ★Weblate 管理の文字列データ(1データ種=1ファイル×3言語)
│   ├── jp/                      # 日本語(翻訳先)。※フォルダ名は「ja」ではなく「jp」
│   ├── en/                      # 英語(翻訳元の基本)
│   └── ko/                      # 韓国語(オリジナル。実体確認・EN欠落分の補完用)
├── dict/                        # ★辞書・インデックス(翻訳の一貫性の源。作業ファイルを置かない)
│   ├── INDEX.md                 # 辞書の使い方
│   ├── style-guide.md           # 表記ルール(記号・性別・レベル表記など)
│   ├── terms.json               # 一般用語の確定訳 (EN/KO → JA)
│   ├── proper-nouns.json        # 固有名詞辞書 (人名・地名・ボス・シリーズ名)
│   └── corpus/
│       └── itemname-pairs.tsv   # itemname の対訳コーパス EN/KO/JA (約27,850行・自動生成)
└── work/                        # ★作業用(スクリプト・翻訳マップ・中間生成物・バックアップ)
    ├── scripts/                 # 汎用ツール (lookup.py = コーパス検索, build_corpus.py = コーパス再生成)
    └── itemname/                # itemname 翻訳セッション (2026-08) の成果物アーカイブ
```

新しいデータ(UI・ストーリー等)を翻訳するときは `work/<データ名>/` を作って作業し、
確定した訳語・規則は `dict/` に追記する。**dict が唯一の正であり、work は使い捨て**。
`json_weblate/` は Weblate と同期されるため、**翻訳データ以外のファイル(バックアップ等)を置かない**。

## データ形式

`json_weblate/{jp,en,ko}/<データ名>.json`(各言語 64〜67 ファイル)。各 JSON は次の形:

```json
{ "キー": { "フィールド": "文字列", ... }, ... }
```

- 翻訳対象の文字列フィールド名はファイルにより異なる:
  `name`(大半)/ `value`(stringcommon, korflash)/ `desc`・`complete`・`manual*`(achievedescription,
  questdescription_final)/ `text`(loadingdescription)/ `tooltipDescription`・`guideDescription`
  (koritemdescription, stringadditionaldescription)など。
  `class`・`regionID`・`npc`・`type`・`grade` など翻訳対象でないフィールドも混在する。
- フィールドが空のエントリ `{}` や、文字列フィールド自体が無いエントリも存在する(触らない)。
- **キーは3言語で完全共通ではない。翻訳対象は jp ファイルに存在するキーのみ。**
  en/ko には jp に無いキーが多数あり、逆に jp にあって en に無いキーもある(itemname で約1,800件。
  その場合は ko から訳す)。確認した範囲では jp のキーは ko に全て存在する。
- ファイル構成も一部異なる: `chapterdescription_event*` は jp=eventcommon のみ、
  en=eventcn/eventkr/eventna、ko=4種すべて。
- 保存形式: UTF-8・改行 LF・`indent=2`・`ensure_ascii=False`・末尾改行あり。

### 未翻訳エントリの見分け方(2パターン)

1. **プレースホルダー形式**: `ITEMNAME_10000041_NAME:[F]Fishing02` のような
   「大文字英数字をアンダースコアで連結 + `:[F]タグ`」。`:[L]JP` が続く変種や、
   `:[F]...` が付かない `ITEMNAME_20001133_NAME` だけの形式もある。
   判定正規表現: `^[A-Z0-9$]+(_+[A-Z0-9$]+)+(:\[F\].*)?$`
   (`STRINGTRIGGER_52000194_QD__52000194__1_NAME` のように**アンダースコアが連続する**形式もあるため `_+`)
2. **韓国語原文の残存**: jp ファイルにハングルがそのまま残っているもの
   (scriptquest 約2.7万・stringtrigger 約1万・npcnameplural 約1,000・questdescription_final 約600 文字列)。

ただし addressname の `blockNameKor`/`blockModifierKor` のように**韓国語・英語が正しい値のフィールド**も
あるため、ハングル検出時はフィールド名を確認すること。

## 翻訳方針(優先順位順)

1. **既存の日本語訳(JMS2公式訳)との一貫性を最優先。**
   訳す前に必ず `dict/corpus/itemname-pairs.tsv` と `dict/terms.json` で既存訳を確認する。
   検索: `python work/scripts/lookup.py <語>`(コーパスは itemname 由来。他データ種の訳語は
   terms.json / proper-nouns.json と jp データ内の既訳を検索して確認する)
2. **翻訳元は英語版を基本**とし、英語名が曖昧・誤訳っぽい・不明な場合は**韓国語版で実体を確認**する
   (韓国語がオリジナル。英語版は独自リネームが多い。例: EN "Tassets" = KR 팬츠 → パンツ)。
   en にキーが無い場合は ko から訳す。
3. **固有名詞は `dict/proper-nouns.json` に従う。** 辞書にない新規固有名詞は英語準拠のカタカナ表記とし、
   訳したら必ず辞書に追記する。既存訳に別表記があればそちらが正
   (例: Kharon→ケルベス、Leshy→モラン、Archer→レンジャー)。
4. **全言語で未翻訳(`..._NAME:[F]Develop` 等のプレースホルダーのみで実名が存在しない)ものは翻訳しない。**
   そのまま残す。

### 特に間違えやすい点

- レアリティ対応は EN と JA でずれている: **EN Epic→エクセレント、EN Ascendant→エピック**、Legendary→レジェンダリー。
- 職業 Archer は**レンジャー**(アーチャーではない)。
- 性別表記 (F)/(M)/(Female)/(Male)/(여)/(남) はすべて **(女)/(男)**。
- 「Scroll」は装備入手用なら**呪文書**(KR 주문서)、それ以外は文脈判断(スクロール/書)。
- 「Fragment」は装備・ボックスの欠片なら**〜の欠片**(KR 조각)、素材の破片なら**破片**(KR 파편)。

## 標準ワークフロー(新規データを翻訳するとき)

1. **抽出**: jp ファイルの未翻訳エントリ(プレースホルダー形式 or ハングル残存)を列挙し、
   en/ko の同キーの値と突き合わせる。作業は `work/<データ名>/` で行う。
2. **規則調査**: 対象データに頻出する語を corpus / terms.json で確認し、訳語を確定する。
   曖昧な語は KO 名で実体確認。既存訳がない規則はここで決めて dict に追記。
3. **翻訳**: パターン化されている名前はルールベーススクリプト、残りは手動マップ(JSON)で翻訳。
   マップは `work/<データ名>/` に保存する。
4. **適用**: 適用前に必ず `work/<データ名>/<ファイル名>.backup.json` としてバックアップを作る
   (`json_weblate/` 内には置かない)。JSON は `ensure_ascii=False, indent=2` + LF + 末尾改行で
   元フォーマットを完全に保つ(適用前にラウンドトリップ一致を検証)。
5. **検証**(必須):
   - 変更されたのが対象の未翻訳エントリのみ(翻訳済みエントリ・非対象フィールド・キー順は不変)
   - プレースホルダー残数 = 翻訳元が存在しなかった件数と一致
   - ハングル・中国語(簡体字)の残存なし(addressname の `*Kor` 等、正当な韓国語フィールドは除く)
   - JSON としてパース可能で、改行コード LF・末尾改行が維持されている
6. **辞書更新**: 新しく確定した固有名詞・用語を `dict/proper-nouns.json` / `dict/terms.json` に追記。
   `json_weblate/*/itemname.json` を更新した場合は `python work/scripts/build_corpus.py` で
   コーパスを再生成する。

## 表記ルール

詳細は `dict/style-guide.md`。要点:

- コロンは全角「：」でスペースなし(例: `称号：優しい花嫁`、`アクション受講証：気合`)
- 括弧は半角 `()`、スペースなしで連結(例: `服(上)(女)`、`1ソケット変換呪文書(LV50/イヤリング)`)
- レベルは `(LV70)` 形式、接頭辞なら `70レベル〜`
- 数字・英字は半角
- 行頭の分類接頭辞は `(ネットカフェ) ` `(景品) ` のように後ろ半角スペース1つ
