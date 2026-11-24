# 翻訳ワーカー向け指示(2026-11 再同期セッション)

MapleStory 2 のゲーム文字列を日本語化するプロジェクト。リポジトリ:
`c:\Users\chro\Desktop\MS2-strings-translation`(以下ルート)。まず以下を読むこと:

- `AGENTS.md` — 翻訳方針(優先順位・間違えやすい点)
- `dict/style-guide.md` — 表記ルール(特に「敬称・タグ」「記号(会話データ)」の節は必須)
- `dict/proper-nouns.json`(固有名詞。`speaker_voice` に話者別の口調)、`dict/terms.json`(用語・`speech_quirks`)

## 担当

`work/resync/batches/<バッチ名>.in.json` の全ユニットを翻訳する。各ユニット:
`{"id", "field", "ko"(韓国語原文=オリジナル), "en"(英語版), "npc"/"npc_ja"(話者。scriptnpc のみ), "n"(同型の件数)}`

- **KO を正**として訳す(EN は意訳・改変が多いので意味の確認用)。KO が無い/中国語の場合は EN と併用。
  中国語原文(setitemname 等)は EN と同一 ID の既訳を参考に実体を特定する。
- `n` があるユニットは「数値だけ違う同型文」の代表。代表を普通に訳せば、残りはスクリプトが数値を差し替えて生成する。
  そのため**原文の数値は訳文にもそのまま(同じ値を同じ個数)残す**こと(漢数字にしない、まとめない)。

## 出力

`work/resync/batches/<バッチ名>.out01.json`, `.out02.json` … に `{"<id>": "訳文", ...}` の JSON(UTF-8、
`ensure_ascii=False`)で書く。100〜150ユニットごとに分割して書いてよい(Python で json.dump するのが安全)。
終わったら必ず検査を実行し、問題 0 になるまで直す:

```
PYTHONIOENCODING=utf-8 python work/resync/check_batch.py <バッチ名>
```

## 厳守事項

- `$map:..$` `$npc:..$` `$npcName:..$` `$item:..$` `$MyPCName$` `{0}` `<font ...>` `</font>` などのタグは**すべて保持**
  (数・中身とも原文どおり。位置は日本語の語順に合わせて移動可)。
- 韓国語の助詞タグ `$pp:를,을$` `$pp2:로,으로$` 等は**削除**し日本語の助詞を書く。
- 改行は原文と**同数**。原文が実改行(JSON の `\n`)ならそのまま実改行、原文がリテラル `\n`(バックスラッシュ+n)なら
  リテラルのまま。行頭・行末の空白、空行も原文どおり。
- 文中の「！」「？」は全角、波ダッシュは「〜」(U+301C)、`...` は「…」、引用符 '…' "…" は「…」。
- `$MyPCName$님` → `$MyPCName$さん`、NPC タグ+님 → `様`。
- 固有名詞・アイテム名・地名・スキル名は必ず既訳を調べて合わせる:
  - `python work/scripts/lookup.py <語>`(itemname 対訳コーパス、EN/KO/JA どれでも可)
  - `json_weblate/jp/*.json` と `json_weblate/ko/*.json` を同じキーで突き合わせて既訳を検索(Grep で KO 語を ko ファイルから探し、同キーの jp を見る)
  - 例: スキル名は `skillname.json`、NPC 名は `npcname.json`、マップ名は `mapname.json`、セット/アイテム名は `itemname.json`
- 辞書に無い新規固有名詞は英語準拠のカタカナ。**新しく決めた固有名詞・用語は最終報告に一覧で書く**(辞書への追記は統括側で行う)。
- `json_weblate/` 以下のデータファイルや dict/ は**編集しない**(出力は batches/ の out ファイルのみ)。

## 最終報告

1. check_batch の最終結果行
2. 新規に決めた固有名詞・用語(KO / EN / JA)と、判断に迷った箇所の一覧(簡潔に)
