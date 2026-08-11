# work/ — 作業用ディレクトリ

翻訳作業のスクリプト・翻訳マップ・中間生成物を置く。**確定した訳語・規則は `dict/` へ**。

```
work/
├── scripts/            # 汎用ツール
│   ├── lookup.py       # 対訳コーパス検索 (python work/scripts/lookup.py <語>)
│   └── build_corpus.py # dict/corpus/itemname-pairs.tsv の再生成
└── itemname/           # 2026-08 アイテム名翻訳セッションの成果物
    ├── auto_map.json   # ルールベース翻訳の結果 (EN→JA 1,062種)
    ├── manual_en.json  # 手動翻訳マップ EN→JA (exact + gendered)
    ├── manual_ko.json  # 手動翻訳マップ KO→JA (EN欠落分)
    ├── translate.py    # ルールエンジン(シリーズ×部位×職業などのパターン)
    ├── extract.py      # 未翻訳エントリ抽出
    ├── apply.py        # マップ適用+フォーマット保全
    ├── verify.py       # 適用後検証
    ├── fish_map.json   # 釣り魚名46種 KO→JA (2026-08-11 追加セッション)
    └── apply_fish.py   # 魚名マップの適用(基本+景品98エントリ、フォーマット保全込み)
```

## 注意

- `dict/corpus/itemname-pairs.tsv` には、この itemname セッションで**新規に訳した2,243件も含まれる**
  (JMS2公式訳と新規訳の区別はコーパス上ではつかない)。どれが新規訳かは
  `work/itemname/auto_map.json` / `manual_*.json` で判別できる。
- 新しいデータ(UI・ストーリー等)の作業は `work/<データ名>/` を新設して行う。
