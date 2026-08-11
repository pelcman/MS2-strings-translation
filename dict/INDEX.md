# dict/ — 翻訳辞書・インデックス

翻訳の一貫性を保つための「唯一の正」。作業ファイルはここに置かない(作業は `work/`)。

| ファイル | 内容 | 更新タイミング |
|---|---|---|
| [terms.json](terms.json) | 一般用語の確定訳(職業・レアリティ・部位・接尾辞・定型) | 新しい用語規則を確定したら追記 |
| [proper-nouns.json](proper-nouns.json) | 固有名詞(地名・ボス・NPC・シリーズ・素材) | 新規固有名詞を訳したら**必ず**追記 |
| [style-guide.md](style-guide.md) | 記号・数字・定型パターンの表記ルール | ルールを新たに確定したら追記 |
| [corpus/itemname-pairs.tsv](corpus/itemname-pairs.tsv) | 既存JMS2訳の対訳コーパス EN/KO/JA/class/key 約28,000行 | データファイル更新時に再生成(work/scripts/build_corpus.py) |

## 使い方

訳語を確認する(EN/KO/JAどの言語でも検索可):

```
python work/scripts/lookup.py ブーツ
python work/scripts/lookup.py "Reward Box"
python work/scripts/lookup.py 주문서
```

## 優先順位

1. corpus の既存訳(JMS2公式) — 最優先
2. terms.json / proper-nouns.json の確定訳
3. どちらにもない → 英語準拠のカタカナ or 自然な和訳で新規決定し、辞書に追記

同名の用語でも文脈(KR原文)によって訳が変わるものがある(Star=スパイク/手裏剣、Fragment=欠片/破片 等)。
迷ったら KO 列で実体を確認する。
