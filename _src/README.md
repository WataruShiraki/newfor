# NEWFOR のソース

このフォルダに、サイトを組み立てるスクリプトと記事データが入っています。
**リポジトリのルート（このフォルダの1つ上）が、そのまま公開されるサイトです。**
Vercel が main ブランチを見て自動で公開します。

## 企業を1社増やすとき（記事は要りません）

1. `companies/<slug>.py` を作る。中身は `C=dict(slug, name, legal, ind, article, timeline, sources)`
2. `timeline` は `('2026.03','事業名','説明（数字を1つ以上）', 継続中かどうか)` の並び
3. **年表が10件以上ないと、検索エンジンに載りません**（noindex になります）。
   これは、中身の薄いページを量産するとサイト全体の評価が下がるためです
4. `python3 mkcomp.py` を実行するとページができます
5. `companies/index.html` の `C` `BARS` `RANGE` `LATEST` も作り直してください

記事（`articles/a0NN_*.py`）は、書けた企業にだけ足します。`C` の `article` に
記事の slug を入れると、企業ページから記事への導線が出ます。

## 記事を1本増やすとき

1. `articles/a0NN_<slug>.py` を作る（既存のファイルをそのまま真似るのが早いです）
2. `mkreports.py` と `buildarticles.py` の `MODS` に追加する
3. 企業ページも作るなら `mkcomp.py` の `MAP` に1行足す
4. `bash build.sh` を実行して `dist/` に生成する
5. 生成物をリポジトリのルートへ反映する（下の「反映のしかた」）

## 反映のしかた

```bash
cd _src
bash build.sh                                   # dist/ に生成
cp dist/index.html ../index.html                # ※ トップは手で管理しています
for d in dist/articles/*/; do cp "$d/index.html" "../articles/$(basename $d)/index.html"; done
for p in about ads privacy; do cp dist/$p/index.html ../$p/index.html; done
cp dist/llms.txt dist/404.html ../
python3 mklist.py      # 記事一覧
python3 mkcomp.py      # 企業ページ
python3 analytics.py   # 計測タグ
```

## 手で管理しているファイル（build.sh では作られません）

- `index.html`（トップ）
- `companies/index.html`（企業データベース）

この2つは生成元がなく、直接編集しています。数字を変えるときは、記事データ
（`articles/a0*.py` の `timeline`）から計算し直してください。ページ内の
`BARS` `RANGE` `LATEST` `C` 配列がそれにあたります。

## 記事データの決まりごと

- `timeline` は `('2026.03', '事業名', '説明', 継続中かどうか)` の並びです
- 日付が確認できないものは載せません（`2018.??` のような書き方はしない）
- 提供を終えた事業は、説明の中に終了年を書いてください
  （「2024年3月末に提供を終えた」のように書くと、チャートが正しい長さの帯になります）

## 書くときの約束

1. 否定的な言葉を使わない（失敗・撤退・寿命）。「提供を終えた」「譲渡した」と書く
2. 誇張しない。「全記録」「一件残らず」は使わない
3. 出典のない数字を置かない。確認できないものは書かない
4. 絵文字を使わない
5. 読者は大企業の新規事業担当者。明日の仕事に使えるかで判断する
6. 大きな金額や専門用語には、必ず説明を添える
7. 著者名は Soichiro

## 記事の材料

`../data/queue.json` に、毎日の自動収集で見つかった候補が入っています。
`status` が `new` のものが未処理です。使ったら `used` に変えてください。
