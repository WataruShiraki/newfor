# -*- coding: utf-8 -*-
import io,os,json
SITE='https://newfor.jp'
UFO='<path d="M10.6 16.4 L21.4 16.4 L25.8 31 L6.2 31 Z" fill="currentColor" opacity=".16"/><path d="M12.5 16.4 L19.5 16.4 L21.9 26.5 L10.1 26.5 Z" fill="currentColor" opacity=".24"/><ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="currentColor"/><path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" fill="none"/>'

CSS = '''
:root{--page:#F6F5F2;--surface:#fff;--surface-2:#F2F1ED;--border:rgba(18,14,38,.13);
 --tx-1:#0C0A16;--tx-2:#403C55;--tx-3:#57536D;--blue:#2F3BD6;--blue-2:#212DBE;--orange:#C63E08;
 --sh:0 1px 2px rgba(24,20,40,.05),0 12px 30px -18px rgba(24,20,40,.3)}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--tx-1);line-height:1.95;
 font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:760px;margin:0 auto;padding:0 22px}
@media (max-width:640px){.wrap{padding:0 16px}}
header{background:var(--blue);color:#fff;position:sticky;top:0;z-index:9}
.hd{display:flex;align-items:center;gap:11px;height:66px;max-width:1180px;margin:0 auto;padding:0 22px}
.hd a{display:flex;align-items:center;gap:11px;color:#fff;text-decoration:none}
.hd svg{width:32px;height:32px;color:#fff}
.wm{font-family:ui-monospace,Menlo,monospace;font-size:19.5px;font-weight:800;letter-spacing:.16em}
.wm b{color:#FF8A45}
.hd nav{margin-left:auto;display:flex;gap:3px;overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none}
.hd nav::-webkit-scrollbar{display:none}
.hd nav a{font-size:13px;padding:7px 11px;border-radius:8px;color:rgba(255,255,255,.9);white-space:nowrap}
.hd nav a:hover{background:rgba(255,255,255,.15);color:#fff}
@media (max-width:760px){
 .hd{height:auto;min-height:58px;padding:9px 16px 7px;flex-wrap:wrap;gap:7px}
 .hd svg{width:27px;height:27px}
 .wm{font-size:17px;letter-spacing:.13em}
 .hd nav{order:3;width:100%;margin-left:0;gap:1px}
 .hd nav a{font-size:12.5px;padding:6px 9px}}
.top{background:linear-gradient(170deg,#2730CE,#3843E6);color:#fff;padding:44px 0 50px;position:relative;overflow:hidden}
.top .bg{position:absolute;right:-30px;bottom:-46px;width:230px;color:#fff;opacity:.13}
.top .crumb{font-size:12px;color:rgba(255,255,255,.78);margin-bottom:12px}
.top .crumb a{color:rgba(255,255,255,.9)}
.top h1{margin:0;font-size:clamp(24px,5vw,34px);letter-spacing:-.03em;font-weight:850;line-height:1.4}
.top p{margin:12px 0 0;font-size:14.5px;color:rgba(255,255,255,.9);max-width:60ch}
main{padding:44px 0 60px}
h2{font-size:19px;letter-spacing:-.025em;font-weight:800;margin:40px 0 12px;padding-top:8px}
h2:first-child{margin-top:0}
h3{font-size:15.5px;font-weight:750;margin:26px 0 8px}
p{margin:0 0 18px;font-size:15px;color:var(--tx-2)}
p b,li b{color:var(--tx-1);font-weight:750}
ul{margin:0 0 18px;padding-left:1.3em;font-size:15px;color:var(--tx-2)}
li{margin-bottom:8px}
a{color:var(--blue)}
.box{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:22px 24px;box-shadow:var(--sh);margin:0 0 22px}
.box p:last-child{margin-bottom:0}
.todo{background:#FFF6F0;border:1px solid rgba(198,62,8,.3);border-radius:12px;padding:16px 20px;margin:0 0 22px;font-size:14px;color:#7A2A05}
.todo b{color:#5C2004}
dl{margin:0}
dt{font-weight:750;font-size:14.5px;margin-top:18px}
dt:first-child{margin-top:0}
dd{margin:4px 0 0;font-size:14.5px;color:var(--tx-2)}
footer{background:#fff;border-top:1px solid var(--border);padding:28px 0;font-size:12.5px;color:var(--tx-3)}
footer a{margin-right:14px}
.reveal{font:inherit;font-size:13.5px;font-weight:700;color:#fff;background:var(--blue);border:0;
 border-radius:9px;padding:8px 15px;cursor:pointer}
.reveal:hover{background:var(--blue-2)}
.mini{font-size:12.5px;color:var(--tx-3);margin-top:-8px}
.up{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;color:var(--tx-3);letter-spacing:.04em;margin-top:34px}
'''

def page(path,title,desc,h1,lead,crumb,body,noindex=False):
    ld={"@context":"https://schema.org","@type":"WebPage","url":SITE+path,"name":title,
        "description":desc,"inLanguage":"ja","isPartOf":{"@id":SITE+"/#site"},
        "publisher":{"@id":SITE+"/#org"}}
    html=f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{path}">
<meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-image-preview:large'}">
<meta name="theme-color" content="#2F3BD6">
<meta property="og:type" content="website">
<meta property="og:site_name" content="NEWFOR">
<meta property="og:locale" content="ja_JP">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/assets/og-top.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-96.png" sizes="96x96" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False,separators=(',',':'))}</script>
<style>{CSS}</style>
</head>
<body>
<header><div class="hd">
  <a href="/"><svg viewBox="0 0 32 32" fill="none" aria-hidden="true">{UFO}</svg><span class="wm">NEW<b>FOR</b></span></a>
  <nav class="main"><a href="/articles/">記事一覧</a><a href="/companies/">企業を探す</a><a href="/#monthly">ランキング</a><a href="/about/">About</a></nav>
</div></header>
<div class="top">
  <svg class="bg" viewBox="0 0 32 32" fill="none" aria-hidden="true">{UFO}</svg>
  <div class="wrap">
    <div class="crumb">{crumb}</div>
    <h1>{h1}</h1>
    <p>{lead}</p>
  </div>
</div>
<main><div class="wrap">
{body}
<div class="up">最終更新：2026年8月5日</div>
</div></main>
<footer><div class="wrap">
  <p><a href="/">トップ</a><a href="/companies/">企業を探す</a><a href="/articles/">記事一覧</a><a href="/about/">運営者情報</a><a href="/ads/">広告について</a><a href="/privacy/">プライバシーポリシー</a></p>
  <p>公開情報に基づく筆者の見解であり、各社の公式見解ではありません。<br>© 2026 NEWFOR</p>
</div></footer>
</body></html>'''
    out='dist'+path+'index.html'
    os.makedirs(os.path.dirname(out),exist_ok=True)
    io.open(out,'w',encoding='utf-8').write(html)
    print('->',path)
