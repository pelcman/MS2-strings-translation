# work/ — 作業用ディレクトリ

翻訳作業のスクリプト・翻訳マップ・中間生成物を置く。**確定した訳語・規則は `dict/` へ**。

```
work/
├── scripts/            # 汎用ツール
│   ├── lookup.py       # 対訳コーパス検索 (python work/scripts/lookup.py <語>)
│   ├── build_corpus.py # dict/corpus/itemname-pairs.tsv の再生成
│   ├── status.py       # README の進捗表を再生成(残り/欠落キー/残置)
│   ├── coverage.py     # jp にキーが無いものを含む実カバー率
│   ├── audit.py        # 6種類の未訳パターンを検出
│   ├── ph_report.py    # プレースホルダーのうち翻訳元があるものを抽出
│   ├── audit_numbers.py # KO と JA で数値が食い違うエントリを検出
│   ├── audit_en_tm.py  # 曖昧な英語名による自動補完を検出
│   ├── extract_missing.py # jp に無いキーを ko/en から抽出
│   ├── tm_prefill.py   # 翻訳メモリ(KO一致/EN一致/元から日本語)で自動補完
│   └── apply_missing.py # 欠落キーの訳を jp へ追加(キー順・書式を検証)
├── npcname/            # 2026-08-11 NPC・モンスター名翻訳セッション
│   ├── real_names.txt     # 実コンテンツ名1,184種の抽出(KO/EN対訳)
│   ├── dev_names.txt      # 開発用324種(バランステスト等)
│   ├── npc_map.json       # KO名 → JA(既訳TM準拠: ポイン/クゥーク/ゲッコー等)
│   ├── tm_hits.json       # TM完全一致分
│   ├── plural_map.json    # plural側のみに存在する85種
│   └── apply_npcname.py   # 適用(npcnameplural は単数訳+:s で自動生成)
├── skillname/          # 2026-08-11 スキル名翻訳セッション
│   ├── extract.txt        # プレースホルダー158件の抽出(KR/CN/EN対訳)
│   ├── skillname_ja.json  # キー → JA(144件適用。KRはバフデータから復元)
│   └── apply_skillname.py # 適用(※skillname.json は末尾改行なしの例外ファイル)
├── stringadditionaldescription/ # 2026-08-11 バフ/デバフ翻訳セッション
│   ├── freq3plus.txt      # 頻度3以上175種の抽出
│   ├── freq3plus_ja.json  # ###n → JA(2,499文字列)
│   ├── apply_freq3.py     # 適用スクリプト
│   ├── tail.txt           # 残り608種の抽出
│   ├── tail_structs.txt   # 数値正規化した構造一覧(192構造)
│   ├── tail_rules.json    # 正規化パターン → JAテンプレート({}に数値代入)
│   └── apply_tail.py      # テンプレート適用(686文字列) → 翻訳可能分は完訳
├── koritemdescription/ # 2026-08-11 アイテム説明文翻訳セッション
│   ├── freq3plus.txt      # 頻度3以上の定型文76種の抽出(###n ↔ KO原文)
│   ├── freq3plus_ja.json  # ###n → JA訳マップ
│   ├── apply_freq3.py     # 定型文76種の適用(1,287文字列)
│   ├── clusters2.txt      # バッチ2のクラスタ抽出(@@TAG ↔ KO原文)
│   ├── crafted2_ja.json   # バッチ2の手作り訳(SCROLL/QBR/PROC/PETKO)
│   ├── apply_batch2.py    # バッチ2適用(TM+ルール生成+手作り、725文字列)
│   ├── tail.txt           # 一点物438種の抽出(###n ↔ KO原文)
│   ├── tail_ja.json       # ###n → JA訳マップ(528文字列)
│   └── apply_tail.py      # 一点物の適用 → これで翻訳可能分は完訳
├── uifiles/            # 2026-08-11 UI系小型ファイル一括翻訳セッション
│   ├── apply_ui.py        # 汎用適用(KO完全一致マップ): python work/uifiles/apply_ui.py <データ名> <マップJSON>
│   ├── apply_rules.py     # 汎用適用(数値→#正規化テンプレート、KO不可時はEN::キーでENフォールバック)
│   ├── apply_sfe.py       # stringfieldenterance 専用(行単位TM+装備ガイド行のルール生成)
│   ├── <データ名>.txt      # 各ファイルの未翻訳抽出(###n key= / KO| / EN|)
│   ├── mapname_ja.json / titlename_ja.json / achievename_ja.json  # 完全一致マップ
│   ├── achievedesc_rules.json / achievedesc_en_rules.json  # 実績説明(KO源280+EN源124)
│   ├── dungeonmission_rules.json / npctitle_ja.json / stringnpcai_ja.json
│   ├── sfe_map.json / sfe_missing.txt      # stringfieldenterance 行マップ
│   ├── usmsubtitle_ja.json                 # キリアンの真実 字幕(KR40+CN40、CN固有名詞はKR準拠に正規化)
│   ├── korflash_ja.json / stringcommon_ja.json  # UI文字列(EN::キー=KO空欄/英語混入分)
│   └── *.backup.json      # 適用直前のバックアップ
└── itemname/           # 2026-08 アイテム名翻訳セッションの成果物
    ├── auto_map.json   # ルールベース翻訳の結果 (EN→JA 1,062種)
    ├── manual_en.json  # 手動翻訳マップ EN→JA (exact + gendered)
    ├── manual_ko.json  # 手動翻訳マップ KO→JA (EN欠落分)
    ├── translate.py    # ルールエンジン(シリーズ×部位×職業などのパターン)
    ├── extract.py      # 未翻訳エントリ抽出
    ├── apply.py        # マップ適用+フォーマット保全
    ├── verify.py       # 適用後検証
    ├── fish_map.json      # 釣り魚名46種 KO→JA (2026-08-11 追加セッション)
    ├── apply_fish.py      # 魚名マップの適用(基本+景品98エントリ、フォーマット保全込み)
    ├── fishdesc_map.json  # 釣り魚詳細説明文46種 (koritemdescription 用、改行はリテラル\n)
    └── apply_fishdesc.py  # 説明文マップの適用(98エントリ)
├── scriptquest/        # 2026-08-12〜17 ストーリー会話 18,339件の翻訳セッション
│   ├── targets.json       # 未訳エントリの抽出 (キー -> [KO, EN])
│   ├── todo.txt / todo_story.txt / todo_kritias.txt  # 未訳分の作業リスト(適用のたび再生成)
│   ├── glossary.tsv       # KO->JA 固有名詞対訳(作業用。確定分は dict/ へ集約済み)
│   ├── sq_map*.json       # バッチ001-105 (KO原文 -> JA訳)
│   ├── sq_kri*.json       # クリティアス編バッチ001-019
│   ├── sq_sto*.json       # ストーリー本編バッチ001-039
│   ├── notes_*.md         # 各ワーカーの訳語メモ(確定分は dict/ へ集約済み)
│   ├── apply_sq.py        # sq_*.json をまとめて適用(ラウンドトリップ検証付き)
│   ├── unify.py           # 訳語統一(FIX表/正規表現/話者別)。公式訳の行には適用しない
│   ├── check_map.py       # sq_*.json の検査(キー一致/ハングル残存/$pp残存/タグ整合)
│   ├── extract_subset.py  # 未訳分から作業リストを再生成
│   └── progress.py        # 進捗表示(読み取り専用)
└── missing/            # 2026-08-13〜17 キー欠落44,276件の補完セッション
    ├── <データ名>.tsv          # 欠落キーの抽出 (キー/フィールド/KO/EN)
    ├── <データ名>.backup.json  # 補完直前のバックアップ
    └── notes_*.md              # 各ワーカーの訳語メモ(確定分は dict/ へ集約済み)
```

## 注意

- `dict/corpus/itemname-pairs.tsv` には、この itemname セッションで**新規に訳した2,243件も含まれる**
  (JMS2公式訳と新規訳の区別はコーパス上ではつかない)。どれが新規訳かは
  `work/itemname/auto_map.json` / `manual_*.json` で判別できる。
- 新しいデータ(UI・ストーリー等)の作業は `work/<データ名>/` を新設して行う。
- 以下は JMS2 でも韓国語のままの内部ラベル/開発者メモのため、ハングル残存チェックの対象外とする
  (addressname の `*Kor` と同様): stringcommon の `comment`/`commend`/`desc`/`commnet`、
  maidmanufacturemessage の `npc`(全27件が韓国語。メッセージ欄は既訳)、
  chapterdescription_* の `isTutorial`(値「중복」=重複マーカー)。
