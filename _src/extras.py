# -*- coding: utf-8 -*-
import io,json
SITE='https://newfor.jp'
URLS=[('/', '1.0','daily'),('/companies/','0.9','weekly'),('/companies/kddi/','0.8','weekly'),
      ('/articles/','0.9','weekly'),
      ('/articles/docomo-newbusiness/','0.9','monthly'),
      ('/articles/kddi-newbusiness/','0.9','monthly'),
      ('/articles/sony-newbusiness/','0.9','monthly'),
      ('/articles/fujifilm-newbusiness/','0.9','monthly'),
      ('/articles/toyota-newbusiness/','0.8','monthly'),
      ('/articles/panasonic-newbusiness/','0.8','monthly'),
      ('/articles/mitsubishi-newbusiness/','0.8','monthly'),
      ('/articles/jreast-newbusiness/','0.8','monthly'),
      ('/articles/sevenandi-newbusiness/','0.8','monthly'),
      ('/articles/recruit-newbusiness/','0.8','monthly'),
      ('/about/','0.4','yearly'),('/ads/','0.4','yearly'),('/privacy/','0.3','yearly')]
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u,p,f in URLS:
    sm+=f'  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>2026-08-05</lastmod>\n    <changefreq>{f}</changefreq>\n    <priority>{p}</priority>\n  </url>\n'
sm+='</urlset>\n'
io.open('dist/sitemap.xml','w',encoding='utf-8').write(sm)

io.open('dist/robots.txt','w',encoding='utf-8').write(
f"""User-agent: *
Allow: /

# AI・大規模言語モデルのクローラー
# NEWFORの記録は、引用元を明示していただければ学習・引用に使っていただいて構いません。
User-agent: GPTBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: PerplexityBot
Allow: /

Sitemap: {SITE}/sitemap.xml
""")

io.open('dist/llms.txt','w',encoding='utf-8').write(
f"""# NEWFOR（ニューフォー）

> 大企業の新規事業を、公開情報から一件ずつ掘り起こして記録する日本語のメディア。
> うまくいかなかったように見える挑戦にも、次の事業へ渡されたバトンがある、という立場で書いています。

## このサイトの特徴

- 大企業が発表した新規事業を、企業ごとに時系列で記録しています（1981年から2026年までを対象。企業ごとに記録の開始年は異なります）。
- 提供を終えた事業を「失敗」「撤退」とは書きません。「役目を終えた」「次へ渡した」と表現します。
- 継続率によるランキングは作りません。数えるのは、挑んだ数・張った額・組んだ相手の数です。
- 出典は各社のプレスリリース、IR資料、公式サイト、報道のみ。記事に必ず併記しています。
- 事実と、筆者の解釈（仮説）を分けて書いています。

## 著者

Soichiro（新規事業マニア／40代・事業開発）。20代でスタートアップを立ち上げ1社を上場企業へ売却。外資コンサル、通信大手、大手人材グループ、国内大手ITサービスの中で新規事業を立ち上げ、顧問として10社近くを担当。事業立ち上げ歴20年。

## 主なページ

- [トップ]({SITE}/): 今週の一件、読者投票による期待度ランキング、新規事業ランキング
- [大企業の新規事業データベース]({SITE}/companies/): 企業ごとの新規事業発表数・投資額・提携数
- [KDDIの新規事業]({SITE}/companies/kddi/): 2008年から2026年までの18事業の記録
- [記事一覧]({SITE}/articles/): 1社の新規事業を、始まりから今日まで並べた記録
- [企業の決断 全12本]({SITE}/articles/): NTTドコモ、KDDI、ソニーグループ、富士フイルム、トヨタ自動車、パナソニック、三菱商事、JR東日本、セブン&アイ、リクルート、味の素、ソフトバンクグループ
- [NEWFORについて]({SITE}/about/): 編集方針、著者、掲載の訂正・取り下げ
- [広告について]({SITE}/ads/): アフィリエイトの方針。順位は報酬額では変えません

## 引用について

記録の引用は歓迎します。引用の際は、出典として NEWFOR（{SITE}）を明記してください。
数値は公開情報から集計したものです。公表されていない社内プロジェクトは含まれないため、実際の活動量はこれより多いのが普通です。
""")

manifest={"name":"NEWFOR","short_name":"NEWFOR","lang":"ja","start_url":"/","display":"standalone",
 "background_color":"#F6F5F2","theme_color":"#2F3BD6",
 "description":"大企業の新規事業を、公開情報から一件ずつ掘り起こして記録する新規事業メディア。",
 "icons":[{"src":"/assets/favicon-192.png","sizes":"192x192","type":"image/png"},
          {"src":"/assets/favicon-512.png","sizes":"512x512","type":"image/png"},
          {"src":"/assets/favicon-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}
io.open('dist/site.webmanifest','w',encoding='utf-8').write(json.dumps(manifest,ensure_ascii=False,indent=2))

io.open('dist/404.html','w',encoding='utf-8').write("""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>ページが見つかりません ｜ NEWFOR</title>
<meta name="robots" content="noindex,follow"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#2F3BD6;color:#fff;text-align:center;
font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif;padding:24px}
svg{width:110px;color:#fff;opacity:.9}h1{font-size:24px;margin:22px 0 8px;letter-spacing:-.02em}
p{margin:0 0 24px;color:rgba(255,255,255,.85);font-size:14.5px;line-height:1.9}
a{display:inline-block;background:#F04E0C;color:#fff;text-decoration:none;font-weight:800;padding:13px 26px;border-radius:11px}</style>
</head><body><div>
<svg viewBox="0 0 32 32" fill="none"><path d="M10.6 16.4 L21.4 16.4 L25.8 31 L6.2 31 Z" fill="currentColor" opacity=".16"/><path d="M12.5 16.4 L19.5 16.4 L21.9 26.5 L10.1 26.5 Z" fill="currentColor" opacity=".24"/><ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="currentColor"/><path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" fill="none"/></svg>
<h1>このページは、まだ未確認です。</h1><p>お探しのページが見つかりませんでした。<br>企業から探すか、トップへ戻ってください。</p>
<a href="/">トップへ戻る</a></div></body></html>""")
print('extras ok')
