# MapleStory 2 翻訳プロジェクト

翻訳方針・ディレクトリ構成・ワークフローの本文は @AGENTS.md を参照(同一内容を共有)。

Claude Code 向けメモ:

- 翻訳対象データは `json_weblate/{jp,en,ko}/<データ名>.json`(日本語フォルダは「ja」ではなく「jp」)
- 訳す前に必ず `python work/scripts/lookup.py <語>` で既存訳を確認すること
- 訳語の判断に迷ったら `dict/terms.json`・`dict/proper-nouns.json`・`dict/style-guide.md` が正
- データファイルへの適用前に必ず `work/<データ名>/` にバックアップ(`*.backup.json`)を作成し
  (`json_weblate/` 内には置かない)、適用後は AGENTS.md の「検証(必須)」を実施
- 新しく確定した訳語は dict へ追記してから作業を終えること
- `json_weblate/*/itemname.json` を更新したら `python work/scripts/build_corpus.py` でコーパス再生成
