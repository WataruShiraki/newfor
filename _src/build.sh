#!/bin/bash
# サイトを一度に作り直す。これ1本で公開用の gh/ まで揃います。
#
# 生成物の置き場所は2つあります。混ぜると事故になるので、ここに書いておきます。
#
#   dist/ に作ってから gh/ へ写すもの … 固定ページ、記事本文、llms.txt ほか
#   gh/ に直接作るもの                … 企業ページ、記事一覧、トップと企業DBの中の数
#
# 1つの出力先を2つのスクリプトが作らないようにしてください。
# 古いほうが後から走ると、公開中のページを古い内容で上書きします（llms.txt で起きました）。
# 最後の checkgen.py が、それを毎回見張っています。
set -e
cd /home/claude

# ── dist/ に作る ──
python3 publish.py        # 旧・手書きHTMLの変換（いまは対象なし）
python3 mkpages.py        # /about/ /ads/ /privacy/
python3 buildarticles.py  # /articles/<slug>/        ← articles/a0*.py
python3 assets.py
node png.js
python3 kartegen.py       # /shindan/ スタートアップ調達診断（OGPの材料も書き出します）
python3 ogspec.py       # OGP画像の中身を実データから組み立てる（og.js より先に）
node og.js              # 全ページぶんのOGP画像 1200×630
# OGP画像は1枚250KBほどになる。減色すると70KBほどまで落ちて、見た目は変わらない。
# SNSの取得が速くなり、GitHubへ上げる量も3分の1になる。
command -v pngquant >/dev/null && for f in dist/assets/og-*.png; do
  pngquant --quality=70-92 --speed 1 --force --ext .png "$f" 2>/dev/null || true
done
python3 extras.py         # llms.txt / sitemap.xml / robots.txt ← companies/ と articles/
python3 fixlinks.py
# サイト直下の favicon.ico（古い環境とクローラ向けの保険）
python3 -c "from PIL import Image; Image.open('dist/assets/favicon-512.png').convert('RGBA').save('dist/favicon.ico',format='ICO',sizes=[(16,16),(32,32),(48,48)])"

# ── dist/ から gh/ へ写す ──
for d in dist/articles/*/; do
  b=$(basename "$d"); [ "$b" = "index.html" ] && continue
  mkdir -p "gh/articles/$b"; cp "$d/index.html" "gh/articles/$b/index.html"
done
for p in about ads privacy; do
  [ -f "dist/$p/index.html" ] && { mkdir -p "gh/$p"; cp "dist/$p/index.html" "gh/$p/index.html"; }
done
for f in llms.txt sitemap.xml robots.txt 404.html favicon.ico; do
  [ -f "dist/$f" ] && cp "dist/$f" "gh/$f"
done
cp -r dist/assets/. gh/assets/ 2>/dev/null || true

# ── gh/ に直接作る ──
python3 mkcomp.py         # gh/companies/<slug>/  ← companies/*.py
python3 mklist.py         # gh/articles/          ← articles/a0*.py
python3 money.py          # 年表から「払った額」を抜き出す（/tmp/money.json）
python3 quiz.py           # トップの「今日の1問」を作る（/tmp/quiz.json）
python3 mktop.py          # gh/index.html の中の数と一覧
python3 mkcompidx.py      # gh/companies/index.html の中の数と一覧
python3 newsgen.py        # gh/news/ 1件1ページ＋一覧（companies/*.py の年表から）

python3 mkaff.py         # トップと企業DBの広告枠を、記事と同じ中身にそろえる
python3 pickup.py        # ヘッダー下の「ピックアップ」帯（直近の投票が流れる）

# ── いちばん最後。ページを作り直したあとでないと、タグが消えます ──
python3 analytics.py      # Search Console の所有権確認タグ／GA4 の計測タグ

# ── 見張り ──
python3 checkgen.py
echo "=== build done ==="
