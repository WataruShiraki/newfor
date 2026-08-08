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

# ── 絞り込みの3つの軸 ──
#
# これまではジャンルの4つだけでした。読む人は「自分の業種」や
# 「いま困っていること」から探します。軸を足して、掛け合わせられるようにします。
INDS=[]
for c in CARDS:
    if c['indshow'] and c['indshow'] not in INDS: INDS.append(c['indshow'])
INDS.sort()

def chips(kind,items):
    """items は (値, 表示名, 英字) の並び"""
    out=[]
    for v,ja,en in items:
        n=sum(1 for c in CARDS if (c['genre']==v if kind=='g'
                                   else c['indshow']==v if kind=='ind'
                                   else v in c['topics']))
        out.append('<button class="gtab%s" data-k="%s" data-v="%s">%s%s'
                   '<span class="cnt">%d</span></button>'
                   %('' if n else ' empty',kind,v,ja,
                     '<span class="en">%s</span>'%en if en else '',n))
    return ''.join(out)

# 携帯だと札が縦に伸びて、記事にたどり着く前に画面3つぶんスクロールすることに
# なります。そこで携帯のときだけ閉じておいて、押したら開く形にします。
FILTERS=(
  '<button class="ftoggle" id="ftoggle" aria-expanded="false">'
  '絞り込む<span class="fnum" id="fnum" hidden>0</span>'
  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
  'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>'
  '</button>'
  '<div class="ffilters" id="ffilters">'
  '<div class="fgrp"><div class="flab">ジャンル</div><div class="gtabs">'
  + chips('g',[(g[0],g[1],g[2]) for g in GENRES]) + '</div></div>'
  '<div class="fgrp"><div class="flab">業種</div><div class="gtabs">'
  + chips('ind',[(i,i,'') for i in INDS]) + '</div></div>'
  '<div class="fgrp"><div class="flab">こんな方におすすめ</div><div class="gtabs">'
  + chips('t',[(k,ja,'') for k,ja in mkreports.TOPICS]) + '</div></div></div>')

BAR=('<div class="fbar">'
     '<span class="fhit"><b id="fhit">%d</b> 本の記事</span>'
     '<span class="fright">'
     '<span class="fsorts">'
     '<button class="fsort on" data-s="new">新着順</button>'
     '<button class="fsort" data-s="old">古い順</button>'
     '<button class="fsort" data-s="short">短い順</button></span>'
     '<button class="fclr" id="fclr" hidden>絞り込みを解除</button>'
     '</span></div>'%len(CARDS))

GD=json.dumps({g[0]:g[3] for g in GENRES},ensure_ascii=False,separators=(',',':'))
GN=json.dumps({g[0]:g[1] for g in GENRES},ensure_ascii=False,separators=(',',':'))

BODY=('<p class="rlead">大企業の新規事業を、公開情報から記録しているメディアです。'
      '<b>新しい記事が上に並びます。</b>ジャンル・業種・お悩みで絞り込めます。</p>'
      + FILTERS
      +'<div class="gdesc" id="gdesc">気になるところから探せます。企業を1社ずつ追った記録、金額のランキング、担当者向けの実務メモがあります。</div>'
      + BAR
      +'<div class="rgrid" id="rgrid">\n'+'\n'.join(card(c) for c in CARDS)+'\n</div>'
      +'<div class="gempty" id="gempty" style="display:none">'
       '<b>この組み合わせに当てはまる記事は、まだありません</b>'
       '<span id="gemsg">絞り込みをひとつ外してみてください。</span></div>')

JS='''<script>
/* 記事一覧の絞り込みと並べ替え
   ─────────────────────────────────
   3つの軸（ジャンル・業種・お悩み）を掛け合わせます。同じ軸の中で
   2つ以上えらんだときは「どちらか」、軸をまたぐと「かつ」です。
   選んだ状態は住所（?g=&ind=&t=）に残します。人に送れるようにするためです。 */
(function(){
  var DESC=%s;
  var ALL="気になるところから探せます。企業を1社ずつ追った記録、金額のランキング、担当者向けの実務メモがあります。";
  var chips=[].slice.call(document.querySelectorAll(".gtab[data-k]"));
  var cards=[].slice.call(document.querySelectorAll(".rcard"));
  var sorts=[].slice.call(document.querySelectorAll(".fsort"));
  var gd=document.getElementById("gdesc"),ge=document.getElementById("gempty");
  var hit=document.getElementById("fhit"),clr=document.getElementById("fclr");
  var sel={g:[],ind:[],t:[]}, mode="new";

  function has(list,v){return list.indexOf(v)>=0;}
  function vals(c,k){
    return k==="g" ? [c.dataset.g] : k==="ind" ? [c.dataset.ind] : (c.dataset.t||"").split(" ");
  }
  /* ある軸を仮に v だけにしたら何本になるか。数えて札に出します */
  function countWith(k,v){
    var n=0;
    cards.forEach(function(c){
      var ok=true;
      ["g","ind","t"].forEach(function(kk){
        var want = (kk===k) ? [v] : sel[kk];
        if(!want.length) return;
        var mine=vals(c,kk);
        if(!want.some(function(x){return has(mine,x);})) ok=false;
      });
      if(ok)n++;
    });
    return n;
  }
  function match(c){
    var ok=true;
    ["g","ind","t"].forEach(function(k){
      if(!sel[k].length) return;
      var mine=vals(c,k);
      if(!sel[k].some(function(x){return has(mine,x);})) ok=false;
    });
    return ok;
  }
  function draw(){
    var n=0, shown=[];
    cards.forEach(function(c){
      var m=match(c);
      c.style.display=m?"":"none";
      if(m){n++;shown.push(c);}
    });
    /* 並べ替えは order でやります。DOMを組み替えないので、
       スクロール位置が飛びません */
    shown.sort(function(a,b){
      if(mode==="short"){
        var d=Number(a.dataset.read)-Number(b.dataset.read);
        if(d) return d;
      }
      var x=a.dataset.no, y=b.dataset.no;
      return mode==="old" ? (x<y?-1:1) : (x>y?-1:1);
    }).forEach(function(c,i){c.style.order=i;});

    hit.textContent=n;
    ge.style.display=n?"none":"";
    var one=(sel.g.length===1&&!sel.ind.length&&!sel.t.length)?sel.g[0]:null;
    gd.textContent=one?(DESC[one]||ALL):ALL;
    chips.forEach(function(b){
      var k=b.dataset.k,v=b.dataset.v,c=countWith(k,v);
      b.classList.toggle("on",has(sel[k],v));
      b.classList.toggle("empty",!c);
      var s=b.querySelector(".cnt"); if(s)s.textContent=c;
    });
    var any=sel.g.length+sel.ind.length+sel.t.length;
    clr.hidden=!any;
    var fn=document.getElementById("fnum");
    if(fn){fn.hidden=!any;fn.textContent=any;}
    if(history.replaceState){
      var q=[];
      ["g","ind","t"].forEach(function(k){
        if(sel[k].length) q.push(k+"="+sel[k].map(encodeURIComponent).join(","));
      });
      history.replaceState(null,"",location.pathname+(q.length?"?"+q.join("&"):""));
    }
  }
  chips.forEach(function(b){b.addEventListener("click",function(){
    var k=b.dataset.k,v=b.dataset.v,i=sel[k].indexOf(v);
    if(i>=0) sel[k].splice(i,1); else sel[k].push(v);
    draw();
  });});
  sorts.forEach(function(b){b.addEventListener("click",function(){
    sorts.forEach(function(x){x.classList.remove("on");});
    b.classList.add("on"); mode=b.dataset.s; draw();
  });});
  clr.addEventListener("click",function(){sel={g:[],ind:[],t:[]};draw();});

  /* 携帯用の開け閉め。開いているかどうかは aria-expanded に持たせます */
  var tg=document.getElementById("ftoggle"), box=document.getElementById("ffilters");
  tg.addEventListener("click",function(){
    var open=box.classList.toggle("open");
    tg.setAttribute("aria-expanded",open?"true":"false");
  });

  /* 住所に絞り込みが書いてあれば、それを復元します */
  ["g","ind","t"].forEach(function(k){
    var m=location.search.match(new RegExp("[?&]"+k+"=([^&]*)"));
    if(!m) return;
    decodeURIComponent(m[1]).split(",").forEach(function(v){
      if(v&&chips.some(function(b){return b.dataset.k===k&&b.dataset.v===v;})) sel[k].push(v);
    });
  });
  draw();
})();
</script>'''%GD

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
<meta property="og:image" content="%(site)s/assets/og-articles.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="%(site)s/assets/og-articles.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-96.png" sizes="96x96" type="image/png">
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
