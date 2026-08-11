# work/ — 作業用ディレクトリ

翻訳作業のスクリプト・翻訳マップ・中間生成物を置く。**確定した訳語・規則は `dict/` へ**。

```
work/
├── scripts/            # 汎用ツール
│   ├── lookup.py       # 対訳コーパス検索 (python work/scripts/lookup.py <語>)
│   └── build_corpus.py # dict/corpus/itemname-pairs.tsv の再生成
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
```

## 注意

- `dict/corpus/itemname-pairs.tsv` には、この itemname セッションで**新規に訳した2,243件も含まれる**
  (JMS2公式訳と新規訳の区別はコーパス上ではつかない)。どれが新規訳かは
  `work/itemname/auto_map.json` / `manual_*.json` で判別できる。
- 新しいデータ(UI・ストーリー等)の作業は `work/<データ名>/` を新設して行う。
