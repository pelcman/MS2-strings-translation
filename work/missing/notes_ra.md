# notes_ra — 欠落補完 ワーカー R-A(loadingdescription / stringcommon / stringadditionaldescription / questdescription_final)

担当 4 ファイルすべて完了。出力件数 = 入力件数(22 / 168 / 185 / 454)。

## 作業ツール(すべて `work/missing/_ra_*`)

- `_ra_lookup.py <語> …` — jp/ko 全ファイルの同キー同フィールドを突合した KO→JA 対訳の部分一致検索
  (`_ra_pairs.pkl` キャッシュ。無ければ再生成が必要)
- `_ra_sib.py <データ名> [開始行] [終了行]` — **欠落キーの「地域違い兄弟キー」を jp から探す**。
  `s_xxx--KR` に対して `s_xxx--` / `s_xxx--JP` の JMS2 公式訳を並べて出す。stringcommon で 23 行が
  これで公式訳をほぼそのまま流用できた。**最初にこれを回すのが最も効率が良い。**
- `_ra_match.py` / `_ra_apply.py` — `$tag:ID$` をスロット化・数字を `#` に正規化したテンプレート照合。
  `_ra_apply.py` は**参照ペア(ko\*, JA\*)のスロット列と数字列が完全一致する場合のみ**位置代入するので、
  notes_qd で警告されていた「数値の取り違え」が原理的に起きない。questdescription_final 87 行を自動生成。
- `_ra_qbuild.py` — auto + 手訳マップ(`_ra_q_map.json`) + キー別上書き(`_ra_q_ovr.json`)を合成して出力。
- `_ra_final.py` — 4 ファイル一括検証(件数・ハングル・簡体字・`$pp:`残存・`{n}`・タグ・改行・`|`・CRLF)。

## 公式既訳の発見(出典付き・推測ではない)

### stringcommon / loadingdescription
| KO | JA | 出典 |
|---|---|---|
| 디자이너스 샵 | デザイナーズショップ | korflash `$s_homemenu_dialog_blueprintshop` |
| 메럿 충전샵 | ブルーメロットチャージショップ | korflash `$s_gamemenu_btn_MeratCharge` |
| 파운더스 팩 | **パウンダースパック**(ファウンダーズではない) | nametagsymboldesc 33--NA |
| 인형의 저택 | **人形の邸宅**(館ではない) | mapname 61000035 |
| 보호막 | **シールド**(保護膜ではない) | korflash `$s_tooltip_myinfo_stat_0_8` |
| 초보 모험가 / 숙련 모험가 | 新米冒険者 / 熟練冒険者(korflash)、**初心冒険者**(questdescription_final) | korflash `$s_dungeon_room_findHelper_*` / questdescription_final 70210090 |
| 도움 요청 | ヘルプ要請 | korflash `$s_dungeon_room_findHelper_button_tooltip` |
| 친절한 기사 상자 | 親切な騎士ボックス | itemname 20301515 |
| 장식도 선물 | 装飾度プレゼント(stringcommon 内)/ 장식도 점수 = ハウスカスタムスコア | stringcommon `s_ugcHousingPoint_Reward_Desc1--` |
| 초보자용 황금 미끼 (1시간) | 初心者向け黄金エサ(1時間) | itemname 20000307 |
| 목걸이/반지 제작 | ネックレス製作 / 指輪製作 | achievedescription 23500009/23500010 |
| 고객센터 | サポート | stringcommon `s_manufacture_error_msg` |
| 판매기한이 만료 | 販売期間が満了 | stringcommon `s_mail_error_ad_expired` |
| 스타일 박스 / 스타일 코인 | スタイルボックス / スタイルコイン | korflash `$s_item_lullubox_item_break_tooltip-NA` |
| 라펜샤드 / 젬스톤 / 더키볼 | ラペンシャード / ジェムストーン / ダッキーボール | achievedescription 21100057 ほか |
| 크리스탈 파편 | クリスタルの破片 | itemname 20301722 |
| 교감하기 | 共鳴する | koritemdescription 20301393(벚꽃나무와 교감) |

`s_burning_levelup_event_*` / `s_buring_levelup_envent_desc_popup` / `s_ugcHousingPoint_Reward_Desc1〜5` /
`s_treewatering_*` / `s_mesoMarket_register_notice` / `s_meratmarket_tooltip_*` /
`s_maple_survival_*` は **jp に地域違いの公式訳がある**ので、数値だけ差し替えて流用した。

### stringadditionaldescription
| KO | JA | 出典 |
|---|---|---|
| 전투력 N 증가 (전장에서 미적용) | 戦闘力がN増加(戦場では未適用) | stringadditionaldescription 90051812 |
| 환영 시공의 힘 | **幻影時空の力**(幻影の時空ではない) | koritemdescription 13100313 |
| 고대의 힘 | 古代の力 | stringadditionaldescription 90051642 |
| 전장 및 투기장에서 HP a, 방어력 관통 b%, STR c, 크리티컬 회피 d 증가 | 戦場および闘技場でHPがa、防御力貫通がb%、STRがc、クリティカル回避がd増加 | 90051634〜90051637 |
| 행동 불가 시간 감소 | 行動不能時間減少 | 90051638 |
| 프리미엄 클럽 혜택 | プレミアムクラブ特典 | 100000014 |
| 고독한 막대과자 | **孤独なポッキー** | itemname 20301693-Event-CN |

### questdescription_final
| KO | JA | 出典 |
|---|---|---|
| 보름달 방앗간 / 달토끼 방앗간 | **満月製粉所 / 月ウサギの製粉所**(餅つき所ではない) | koritemdescription 20302813-Event-JP |
| 향긋한 쑥 월병 / 달콤한 꿀 월병 | 香り高いヨモギ月餅 / 甘いハチミツ月餅 | itemname 20301973--CN / 20301974--CN |
| 일곱 번째 달밤 | **七度目の月夜** | scriptquest 713172114003307--KR |
| 은하수 정원 / 사랑의 댄스파티 / 럭키 가이 | 天の川の庭園 / 愛のダンスパーティ / ラッキーガイ | mapname 63000062 / korflash `$s_gamemenu_popup_coupledance` / scriptquest 713172114003636 |
| 달아난 달토끼 | 逃げた月ウサギ | npcname 27000034 |
| 문라이트 번지 점프 | ムーンライトバンジージャンプ | mapname 80000016 |
| 찌리릿 하트가오리 / 꽃길 우파루파 | ピリピリハートエイ / 花道のウーパールーパー | itemname 33040252 / 33040254 |
| 꽃 풍선 | 花風船 | koritemdescription 30001201--CN |
| 트라이아 침공, 그 후 | トライア侵攻、その後 | questdescription_final 91000000 |
| 아리까리 상단 | アヤフヤ商団 | questdescription_final 70700001 |
| 모험[일반/어려움] 보너스 상자 | 冒険[ノーマル/ハード] **ボーナスボックス(`]` の後に半角スペース)** | questdescription_final 89020002 / 89010391 |
| 숨바꼭질 | かくれんぼ | itemname 20301437 |
| 황금 보물 상자 | 黄金宝箱 | questdescription_final 70500010 |
| 길드 퀘스트の注記4行 | 89010015 の公式訳をそのまま流用 | questdescription_final 89010015 |

### ★称号名は KO の直訳ではなく JP 公式称号名を使う
80010214〜80010217 の「'○○' 칭호를 한 캐릭터」は、JMS2 公式(scriptquest 713172114003649 等)が
**JP 版の称号名**に置き換えている。titlename.json で確認した対応:

| KO 称号 | JP 称号 | titlename |
|---|---|---|
| 불가사의한 | **ルーン剣術を極めた** | 10000498-JobChange_01- |
| 고압적인 | **やすらぎの天使** | 10000493-JobChange_01- |
| 마음을 훔치는 | 心を奪う | 10000197 |
| 불청객 | 招かれざる客 | 10000050 |

## 新規に決めた訳(既訳なし・今回確定)

| KO | JA | 判断根拠 |
|---|---|---|
| 권리침해센터 | 権利侵害センター | loadingdescription 251--KR。korflash に「권리침해 신고센터」の JA 既訳が無かったため直訳 |
| 중국 전용 툴팁. 번역할 필요 없음. | 中国専用ツールチップ。翻訳の必要はありません。 | loadingdescription 305〜310--CN。EN も韓国語のまま(ダミー文言)だが、ハングル残存を避けるため訳出 |
| 프렛리스 베이스 기타 / 마림바 / 플루트 / 홍키통크 피아노 / 프렌치 호른 / 파이프 오르간 | フレットレスベースギター / マリンバ / フルート / ホンキートンクピアノ / フレンチホルン / パイプオルガン | いずれも itemname 34000100〜34000112 の楽器名に一致 |
| 에네르 트리거 | エネルトリガー | 에네르=エネル(achievedescription 21400041) |
| 던전 밸런스 테스트 | ダンジョンバランステスト | 開発用テキスト。実적용=実適用 |
| 크리티아스 필드N 레벨 | クリティアスフィールドNレベル | 크리티아스=クリティアス |
| 머쉬킹 | マッシュキング | korflash `$s_world_champion_explain1`(achievecategoryname 24 は「王様キノコ」だが、この content 系は マッシュキング) |
| 까르보나 / 까사노바 | カルボナ / カサノバ | npcname 11004101 / 11004102(既訳あり) |
| 금슬의 비결 | おしどり夫婦の秘訣 | 80010190。금슬=夫婦仲 |
| 각 잡힌 남자 | 折り目正しい男 | 80010197。근위대장フレイへの告白クエスト |
| 골골 거리며 살지 말고 | 弱ってばかりいないで | 80010198 |
| 아이돌은 아무나 하나 | アイドルは誰でもなれるものじゃない | 80010194。韓国の慣用句「아무나 하나」 |
| 태초의 버섯 섬과 맞닿은 그곳 | 太初のキノコ島に接するあの場所 | 80010123 |
| 타임 몬스터 | タイムモンスター | 80010400〜402(파풀라투스=ビシャスプラント は $npc$ タグなので訳出不要) |
| 모험도희영신춘(冒险岛喜迎新春) | **冒険島喜迎新春** | 80010580-Event-CN。itemname 30001493〜30001499 の JP が 冒/険/島/喜/迎/新/春 なので、簡体字を残さずこの 7 文字を採用。KO のハングル読み+簡体字の重複は JP では同一表記になるため括弧書きを省いた |
| 모험[일반/레이드] | 冒険[ノーマル/レイド] | 89010122 等。`[ノーマル/ハード]` の既訳に合わせ `]` の後に半角スペース |

## 判断が分かれる点(レビュー向け)

1. **`초보 모험가`** — korflash は「新米冒険者」、questdescription_final は「初心冒険者」で**既訳が割れている**。
   今回は questdescription_final 側(89010141 等)を **初心冒険者**、stringcommon/loadingdescription 側を
   **新米冒険者** とし、それぞれのファイルの既訳に合わせた。統一するなら要一括修正。
2. **`모험단계` / `모험렙레`**(89010121 / 89010151 の manual)は KO 側の誤記。
   同一クエストの name は `모험레벨` なので、JA は 3 フィールドとも **冒険レベル** に統一した。
3. **`스타일 코인샵`** は korflash `$s_gamemenu_btn_pssbshop`=アバターコインショップ、
   `$s_item_lullubox_style_shop_tooltip-NA`=スタイルコインショップ と既訳が割れている。
   今回対象(`s_shop_text_notice_pssb--NA`)は「スタイルボックス/スタイルコイン」のみ使用で回避した。
4. **`s_ugcHousingPoint_Reward_Desc1〜5--KR`** は KO の項目リスト行頭が `   - `(半角スペース3つ)、
   jp 既存の `--` 版は `- `。今回は**KO のインデントをそのまま維持**し、文言だけ公式訳を流用した。
5. **`이벤트 던전 '$dungeonTitle:29006001$ N회 클리어하기`**(80010400〜402 manual)は
   KO 原文の引用符が閉じていない。JA は `「…」` で閉じた。
6. **`중국 전용 툴팁`(loadingdescription 305〜310--CN)** は本来ダミー。翻訳不要と判断するなら削除候補。
