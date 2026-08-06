# -*- coding: utf-8 -*-
"""/articles/ の記事一覧ページを生成する"""
import io,os,json
from pages import CSS,UFO,SITE
import mkreports
from mkreports import GENRES,CARDS,EXTRA,card

TITLE='記事一覧 ｜ 大企業の新規事業を記録する ｜ NEWFOR'
DESC='大企業の新規事業を、始めた年から今日まで公開情報だけで記録しています。新規事業ヒストリー、ランキング、新規事業のお供、入門の4ジャンル。'
H1='記事一覧'
LEAD='大企業の新規事業を、公開情報から記録しています。'

cnt={g[0]:sum(1 for c in CARDS if c['genre']==g[0]) for g in GENRES}
tabs=['<button class="gtab on" data-g="all">すべて<span class="cnt">%d</span></button>'%len(CARDS)]
for slug,ja,en,desc in GENRES:
    tabs.append('<button class="gtab%s" data-g="%s">%s<span class="en">%s</span>'
                '<span class="cnt">%d</span></button>'
                %('' if cnt[slug] else ' empty',slug,ja,en,cnt[slug]))
GD=json.dumps({g[0]:g[3] for g in GENRES},ensure_ascii=False,separators=(',',':'))
GN=json.dumps({g[0]:g[1] for g in GENRES},ensure_ascii=False,separators=(',',':'))

BODY=('<p class="rlead">大企業の新規事業を、公開情報から記録しているメディアです。'
      '<b>ジャンルで絞り込めます。</b></p>'
      +'<div class="gtabs">'+''.join(tabs)+'</div>'
      +'<div class="gdesc" id="gdesc">気になるジャンルから探せます。企業を1社ずつ追った記録、金額のランキング、担当者向けの実務メモがあります。</div>'
      +'<div class="rgrid" id="rgrid">\n'+'\n'.join(card(c) for c in CARDS)+'\n</div>'
      +'<div class="gempty" id="gempty" style="display:none">'
       '<b>このジャンルは準備中です</b><span id="gemsg"></span></div>')

JS='''<script>
(function(){
  var DESC=%s, NAME=%s;
  var ALL="気になるジャンルから探せます。企業を1社ずつ追った記録、金額のランキング、担当者向けの実務メモがあります。";
  var tabs=[].slice.call(document.querySelectorAll(".gtab"));
  var cards=[].slice.call(document.querySelectorAll(".rcard"));
  var gd=document.getElementById("gdesc"),ge=document.getElementById("gempty"),gm=document.getElementById("gemsg");
  function show(g){
    tabs.forEach(function(t){t.classList.toggle("on",t.dataset.g===g);});
    var n=0;
    cards.forEach(function(c){
      var hit=(g==="all"||c.dataset.g===g);
      c.style.display=hit?"":"none"; if(hit)n++;
    });
    gd.textContent=(g==="all")?ALL:(DESC[g]||ALL);
    ge.style.display=n?"none":"";
    if(!n)gm.textContent="「"+(NAME[g]||"")+"」の記事は、いま準備しています。公開までもう少しお待ちください。";
    if(history.replaceState)history.replaceState(null,"",g==="all"?location.pathname:location.pathname+"?g="+g);
  }
  tabs.forEach(function(t){t.addEventListener("click",function(){show(t.dataset.g);});});
  var q=(location.search.match(/[?&]g=([a-z]+)/)||[])[1];
  if(q&&tabs.some(function(t){return t.dataset.g===q;}))show(q);
})();
</script>'''%(GD,GN)

ld=[{"@context":"https://schema.org","@type":"CollectionPage","url":SITE+"/articles/","name":TITLE,
     "description":DESC,"inLanguage":"ja","isPartOf":{"@id":SITE+"/#site"},
     "publisher":{"@id":SITE+"/#org"}},
    {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"NEWFOR","item":SITE+"/"},
      {"@type":"ListItem","position":2,"name":"記事一覧","item":SITE+"/articles/"}]},
    {"@context":"https://schema.org","@type":"ItemList","name":"NEWFORの記事一覧",
     "itemListElement":[{"@type":"ListItem","position":i+1,"name":c['h1'],
                         "url":SITE+"/articles/"+c['slug']+"/"} for i,c in enumerate(CARDS)]}]

html='''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(site)s/articles/">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#2F3BD6">
<meta property="og:type" content="website">
<meta property="og:site_name" content="NEWFOR">
<meta property="og:locale" content="ja_JP">
<meta property="og:url" content="%(site)s/articles/">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:image" content="%(site)s/assets/og-top.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
%(ld)s
<style>%(css)s%(extra)s</style>
</head>
<body>
<header><div class="hd">
  <a href="/"><svg viewBox="0 0 32 32" fill="none" aria-hidden="true">%(ufo)s</svg><span class="wm">NEW<b>FOR</b></span></a>
  <nav class="main"><a href="/articles/">記事一覧</a><a href="/companies/">企業を探す</a><a href="/#monthly">ランキング</a><a href="/about/">About</a></nav>
</div></header>
<div class="top">
  <svg class="bg" viewBox="0 0 32 32" fill="none" aria-hidden="true">%(ufo)s</svg>
  <div class="wrap">
    <div class="crumb"><a href="/">NEWFOR</a> ／ 記事一覧</div>
    <h1>%(h1)s</h1>
    <p>%(lead)s</p>
  </div>
</div>
<main><div class="wrap">
%(body)s
</div></main>
%(js)s
<footer><div class="wrap">
  <p><a href="/">トップ</a><a href="/articles/">記事一覧</a><a href="/companies/">企業を探す</a><a href="/about/">運営者情報</a><a href="/ads/">広告について</a><a href="/privacy/">プライバシーポリシー</a></p>
  <p>公開情報に基づく筆者の見解であり、各社の公式見解ではありません。<br>本サイトはアフィリエイトプログラムによる収益を得ています。詳しくは<a href="/ads/">広告について</a>。<br>© 2026 NEWFOR</p>
</div></footer>
</body></html>'''%dict(
  title=TITLE,desc=DESC,site=SITE,css=CSS,extra=EXTRA,ufo=UFO,h1=H1,lead=LEAD,body=BODY,js=JS,
  ld='\n'.join('<script type="application/ld+json">%s</script>'
               %json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in ld))

# .wrap を一覧ページだけ広くする
html=html.replace('</style>','\n.wrap{max-width:1180px}\nmain .wrap{max-width:1180px}\n</style>')

os.makedirs('gh/articles',exist_ok=True)
io.open('gh/articles/index.html','w',encoding='utf-8').write(html)
print('-> gh/articles/index.html  cards=%d'%len(CARDS))
