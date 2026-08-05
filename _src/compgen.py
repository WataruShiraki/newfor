# -*- coding: utf-8 -*-
"""企業ページ生成 ─ 記事の年表データから /companies/<slug>/ を作る"""
import io,os,re,sys,json
sys.path.insert(0,'articles')
import artgen
from artgen import CSS,UFO,AFF_JS,SITE

NOW=2026.6   # 2026年8月

def ym(s):
    """'2015.11' -> 2015.917"""
    m=re.match(r'(\d{4})\.(\d{1,2})',str(s))
    if not m:
        m=re.match(r'(\d{4})',str(s))
        return float(m.group(1)) if m else None
    return int(m.group(1))+(int(m.group(2))-1)/12.0

END_W=r'(?:終え|終了|終結|移した|移管|統合|譲渡|売却|手放し|公有化|解消|走り切っ|役目を終え)'

def find_end(note,start=None):
    """本文から終了年月を拾う。拾えなければ None（＝期間が公表されていない）"""
    if not note: return None
    # 2026年2月に…終えた ／ 2025年3月末に販売を終えた
    m=re.search(r'(20\d\d)年(\d{1,2})月(?:末)?(?:に|で|時点)?.{0,16}?'+END_W,note)
    if m: return int(m.group(1))+(int(m.group(2))-1)/12.0
    # 同年9月30日に提供を終えた
    m=re.search(r'同年(\d{1,2})月.{0,12}?'+END_W,note)
    if m and start: return int(start)+(int(m.group(1))-1)/12.0
    # 2021年に役目を終えた ／ 2021年に帝人へ移した
    m=re.search(r'(20\d\d)年(?:に|には)?.{0,16}?'+END_W,note)
    if m: return int(m.group(1))+0.5
    # 約4年半で生産を終えた ／ 5年間の提供を走り切った
    m=re.search(r'(?:約)?(\d+)年(半)?(?:間)?(?:で|の).{0,14}?'+END_W,note)
    if m and start: return start+int(m.group(1))+(0.5 if m.group(2) else 0)
    return None

EXTRA_CSS='''
.cwrap{max-width:1000px}
.cstat{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:0 0 6px}
@media(max-width:700px){.cstat{grid-template-columns:repeat(2,1fr)}}
.cstat .c{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.2);border-radius:13px;padding:14px 15px}
.cstat .l{font-size:11px;letter-spacing:.06em;opacity:.82;display:block;margin-bottom:5px}
.cstat .v{font-size:26px;font-weight:800;letter-spacing:-.03em;line-height:1}
.cstat .v small{font-size:12px;font-weight:700;margin-left:3px;opacity:.9}
.cbox{background:var(--surface);border:1px solid var(--line);border-radius:17px;padding:26px 28px;margin:30px 0;box-shadow:var(--sh)}
@media(max-width:640px){.cbox{padding:19px 15px;border-radius:14px}}
.cbox h2{font-size:19px;font-weight:800;letter-spacing:-.02em;margin:0 0 4px}
.cbox .sub{font-size:12.5px;color:var(--muted);margin:0 0 18px}
.cch{display:flex;flex-direction:column;gap:7px}
.crow2{display:grid;grid-template-columns:150px 1fr 96px;gap:11px;align-items:center;font-size:12.5px}
@media(max-width:640px){.crow2{grid-template-columns:104px 1fr;gap:7px}.crow2 .yr2{grid-column:2;font-size:11px;text-align:left;margin-top:-3px}}
.crow2 .n2{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600}
.crow2 .trk2{position:relative;height:12px;background:var(--track);border-radius:7px;overflow:hidden}
.crow2 .b2{position:absolute;top:0;height:12px;border-radius:7px}
.b2.live{background:var(--accent)}
.b2.done{background:var(--ended)}
.b2.unk{background:var(--ended);border-radius:50%;min-width:9px;max-width:9px;opacity:.9}
.crow2 .yr2{font-size:11px;color:var(--muted);font-family:ui-monospace,Menlo,monospace;text-align:right}
.cax{display:flex;justify-content:space-between;font-size:10.5px;color:var(--muted);font-family:ui-monospace,Menlo,monospace;margin-top:9px;padding-top:7px;border-top:1px solid var(--line)}
.clg{display:flex;gap:15px;flex-wrap:wrap;font-size:11.5px;color:var(--muted);margin-top:12px}
.clg i{display:inline-block;width:19px;height:8px;border-radius:5px;margin-right:5px;vertical-align:middle}
.clg i.live{background:var(--accent)}.clg i.done{background:var(--ended)}
.clg i.unk{background:var(--ended);border-radius:50%;width:9px;min-width:9px}
.cfil{display:flex;gap:7px;flex-wrap:wrap;margin:0 0 15px}
.cfil button{font:inherit;font-size:12px;font-weight:700;padding:7px 13px;border-radius:20px;border:1px solid var(--line);
  background:var(--bg);color:var(--muted);cursor:pointer}
.cfil button.on{background:var(--accent);border-color:var(--accent);color:#fff}
.clist{list-style:none;margin:0;padding:0}
.clist li{display:grid;grid-template-columns:78px 1fr auto;gap:13px;padding:14px 0;border-top:1px solid var(--line);align-items:start;font-size:14.5px}
@media(max-width:640px){.clist li{grid-template-columns:66px 1fr;gap:9px;font-size:13.5px}.clist .bd2{grid-column:2}}
.clist li:first-child{border-top:0}
.clist .y2{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:var(--muted);padding-top:2px}
.clist .ev2{font-weight:700;line-height:1.6}
.clist .ev2 em{display:block;font-style:normal;font-weight:400;font-size:13px;color:var(--muted);margin-top:3px;line-height:1.8}
.bd2{font-size:10.5px;font-weight:700;padding:3px 9px;border-radius:11px;white-space:nowrap;height:fit-content;margin-top:2px}
.bd2.live{background:var(--accent-w);color:var(--accent)}
.bd2.done{background:var(--ended-w);color:var(--ended-d)}
.cnote{background:var(--note);border-left:3px solid var(--line2);border-radius:0 10px 10px 0;padding:13px 16px;font-size:12.5px;color:var(--muted);line-height:1.9;margin:16px 0 0}
.crep{display:block;background:var(--surface);border:1px solid var(--accent-l);border-radius:15px;padding:21px 24px;text-decoration:none;color:inherit;margin:30px 0;box-shadow:var(--sh)}
.crep .k2{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.13em;color:var(--accent);font-weight:700}
.crep .t2{font-size:17px;font-weight:800;letter-spacing:-.02em;margin-top:6px;line-height:1.55}
.crep .d2{font-size:13px;color:var(--muted);margin-top:7px;line-height:1.8}
.csrc{list-style:none;padding:0;margin:0;display:grid;gap:2px}
.csrc li{padding:9px 0;border-bottom:1px solid var(--line);font-size:13.5px;line-height:1.7}
.csrc li:last-child{border-bottom:0}
.csrc a{color:var(--tx-2);text-decoration:none;display:inline-flex;align-items:baseline;gap:7px}
.csrc a:hover{color:var(--accent)}
.csrc a::before{content:"→";color:var(--tx-3);font-size:11px}
.cothers{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.cothers a{font-size:12.5px;font-weight:600;padding:7px 13px;border-radius:19px;border:1px solid var(--line);
  background:var(--bg);text-decoration:none;color:var(--muted)}
.cothers a:hover{border-color:var(--accent);color:var(--accent)}
'''

TPL='''<!DOCTYPE html>
<html lang="ja" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#2F3BD6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#08080B" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:site_name" content="NEWFOR">
<meta property="og:locale" content="ja_JP">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://newfor.jp/assets/og-{ogslug}.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://newfor.jp/assets/og-{ogslug}.png">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<script type="application/ld+json">{ld}</script>
<style>{css}{ecss}</style>
</head>
<body>
<header><div class="wrap hd">
  <a class="brand" href="/"><svg class="mark" viewBox="0 0 32 32" fill="none" aria-hidden="true">{ufo}</svg><span class="wm">NEW<b>FOR</b></span></a>
  <nav class="main"><a href="/articles/">記事一覧</a><a href="/companies/">企業を探す</a><a href="/#monthly">ランキング</a><a href="/about/">About</a></nav>
  <button class="tgl" id="tgl" aria-label="配色を切り替える">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <path id="ic-moon" d="M12 3v2m0 14v2M5.6 5.6l1.4 1.4m10 10l1.4 1.4M3 12h2m14 0h2M5.6 18.4l1.4-1.4m10-10l1.4-1.4M12 8a4 4 0 100 8 4 4 0 000-8z"/></svg>
  </button>
</div></header>

<div class="hero">
  <svg class="bg" viewBox="0 0 32 32" fill="none" aria-hidden="true">{ufo}</svg>
  <div class="wrap cwrap">
    <div class="crumb"><a href="/">NEWFOR</a> ／ <a href="/companies/">企業を探す</a> ／ {name}</div>
    <h1>{name}の新規事業</h1>
    <p class="dek">{lead}</p>
    <div class="cstat">{stat}</div>
  </div>
</div>

<div class="wrap cwrap" style="padding-top:34px;padding-bottom:56px">

  <div class="cbox">
    <h2>事業稼働チャート</h2>
    <div class="sub">{name}の主な新規事業／{lo}–2026</div>
    <div class="cch">{chart}</div>
    <div class="cax"><span>{lo}</span><span>2026</span></div>
    <div class="clg"><span><i class="live"></i>継続中</span><span><i class="done"></i>終了・譲渡</span>{unklg}</div>
    {unknote}
  </div>

  <div class="affmini-slot" data-aff="learn"></div>

  <div class="cbox">
    <h2>新規事業の一覧</h2>
    <div class="sub">公開情報から拾った{n}件。年の古い順に並べています</div>
    <div class="cfil"><button class="on" data-f="all">すべて（{n}）</button><button data-f="live">継続中（{nlive}）</button><button data-f="done">終了・譲渡（{ndone}）</button></div>
    <ul class="clist" id="clist">{list}</ul>
  </div>

  {rep}
  <div class="cbox">
    <h2>この一覧の出どころ</h2>
    <div class="sub">1件ずつ、次の公開情報にあたって記録しています</div>
    <ul class="csrc">{srcs}</ul>
  </div>

  <div class="affslot" data-aff="learn"></div>

  <div class="cbox">
    <h2>ほかの企業を見る</h2>
    <div class="sub">記録が揃っている企業です</div>
    <div class="cothers">{others}</div>
  </div>

  <div class="cnote">この一覧は、企業のプレスリリース・IR資料・公式サイトなど、公開されている情報だけを元に作成しています。網羅を保証するものではありません。誤りや抜けを見つけられた場合は、<a href="/about/">About</a> のフォームからお知らせください。</div>

</div>

<footer><div class="wrap">
  <div class="fnav"><a href="/">トップ</a><a href="/companies/">企業を探す</a><a href="/articles/">記事一覧</a><a href="/about/">About</a><a href="/ads/">広告について</a><a href="/privacy/">プライバシー</a></div>
  <p class="cp">© 2026 NEWFOR</p>
</div></footer>

<script>
(function(){{var t=document.getElementById("tgl"),r=document.documentElement;
 t&&t.addEventListener("click",function(){{r.setAttribute("data-theme",r.getAttribute("data-theme")==="dark"?"light":"dark");}});}})();
(function(){{var L=document.getElementById("clist");if(!L)return;
 Array.prototype.forEach.call(document.querySelectorAll(".cfil button"),function(b){{
  b.addEventListener("click",function(){{
   var f=b.getAttribute("data-f");
   Array.prototype.forEach.call(document.querySelectorAll(".cfil button"),function(x){{x.classList.toggle("on",x===b);}});
   Array.prototype.forEach.call(L.children,function(li){{
    li.style.display=(f==="all"||li.getAttribute("data-s")===f)?"":"none";}});
  }});}});}})();
{affjs}
</script>
</body></html>'''


def render(c):
    biz=c['biz']            # [(name, start_float, end_float or None, live, note)]
    lo=int(min(b[1] for b in biz))
    span=2026.6-lo
    rows=[]; unk=False
    for n,s,e,live,note in biz:
        left=(s-lo)/span*100
        if live:
            w=max(1.8,(NOW-s)/span*100); cls='live'; yr='%d–'%int(s)
        elif e:
            w=max(1.8,(e-s)/span*100); cls='done'; yr='%d–%d'%(int(s),int(e))
        else:
            w=0.7; cls='done unk'; yr='%d'%int(s); unk=True
        rows.append('<div class="crow2"><span class="n2" title="%s">%s</span>'
          '<span class="trk2"><span class="b2 %s" style="left:%.2f%%;width:%.2f%%"></span></span>'
          '<span class="yr2">%s</span></div>'%(n,n,cls,left,w,yr))
    items=[]
    for n,s,e,live,note in biz:
        bd='<span class="bd2 live">継続中</span>' if live else '<span class="bd2 done">終了・譲渡</span>'
        y='%d.%02d'%(int(s),round((s-int(s))*12)+1)
        note='<em>%s</em>'%note if note else ''
        items.append('<li data-s="%s"><span class="y2">%s</span><span class="ev2">%s%s</span>%s</li>'%(
          'live' if live else 'done',y,n,note,bd))
    nlive=sum(1 for b in biz if b[3]); ndone=len(biz)-nlive
    stat=''.join('<div class="c"><span class="l">%s</span><span class="v">%s<small>%s</small></span></div>'%(l,v,u)
        for l,v,u in [('記録した新規事業',len(biz),'件'),('記録の範囲','%d–'%lo,'2026')])
    others=''.join('<a href="/companies/%s/">%s</a>'%(s,n) for s,n in c['others'])
    srcs=''.join('<li><a href="%s" rel="noopener nofollow" target="_blank">%s</a></li>'%(u,t)
                 for t,u in c.get('srcs',[]))
    rep=('<a class="crep" href="%s"><span class="k2">企業の決断</span>'
         '<span class="t2">%s</span><span class="d2">この一覧の背景を、%d年分の記録として読み解いた記事です。</span></a>'
         %(c['rep'],c['rept'],2026-lo)) if c.get('rep') else ''
    U=SITE+'/companies/%s/'%c['slug']
    ld={"@context":"https://schema.org","@graph":[
      {"@type":"CollectionPage","@id":U+"#page","name":"%sの新規事業 一覧"%c['name'],
       "url":U,"description":c['desc'],"inLanguage":"ja",
       "isPartOf":{"@type":"WebSite","name":"NEWFOR","url":SITE},
       "about":{"@type":"Organization","name":c['legal'],"alternateName":c['name']},
       "mainEntity":{"@id":U+"#list"}},
      {"@type":"ItemList","@id":U+"#list",
       "name":"%sが手がけた新規事業"%c['name'],"numberOfItems":len(biz),
       "itemListOrder":"https://schema.org/ItemListOrderAscending",
       "itemListElement":[
         {"@type":"ListItem","position":i+1,
          "item":{"@type":"CreativeWork","name":n,"description":note,
                  "datePublished":"%d"%int(st),
                  "provider":{"@type":"Organization","name":c['legal']}}}
         for i,(n,st,e,lv,note) in enumerate(biz)]},
      {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"NEWFOR","item":SITE+"/"},
        {"@type":"ListItem","position":2,"name":"企業を探す","item":SITE+"/companies/"},
        {"@type":"ListItem","position":3,"name":c['name'],"item":U}]}]}
    return TPL.format(title=c['title'],desc=c['desc'],url=SITE+'/companies/%s/'%c['slug'],
        ogslug=c['ogslug'],name=c['name'],lead=c['lead'],stat=stat,lo=lo,yspan=2026-lo,
        chart=''.join(rows),list=''.join(items),n=len(biz),nlive=nlive,ndone=ndone,
        unklg='<span><i class="unk"></i>その年だけの出来事</span>' if unk else '',
        unknote='<div class="cnote">丸い印で示しているのは、譲渡の決定や買収の提案など、その年で完結した出来事です。期間のある事業は帯で示しています。終了した年が公表されていない事業も、同じ丸い印にしています。</div>' if unk else '',
        rep=rep,others=others,srcs=srcs,
        robots=('noindex,follow' if c.get('thin') else 'index,follow,max-image-preview:large,max-snippet:-1'),
        ld=json.dumps(ld,ensure_ascii=False,separators=(',',':')),
        css=CSS,ecss=EXTRA_CSS,ufo=UFO,affjs=AFF_JS)
