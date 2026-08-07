# -*- coding: utf-8 -*-
import io,os,json,html

UFO='<path d="M10.6 16.4 L21.4 16.4 L25.8 31 L6.2 31 Z" fill="currentColor" opacity=".16"/><path d="M12.5 16.4 L19.5 16.4 L21.9 26.5 L10.1 26.5 Z" fill="currentColor" opacity=".24"/><ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="currentColor"/><path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" fill="none"/>'
AV_SVG='<svg viewBox="0 0 32 32" fill="none"><path d="M10.6 16.4 L21.4 16.4 L25.8 31 L6.2 31 Z" fill="currentColor" opacity=".22"/><path d="M12.5 16.4 L19.5 16.4 L21.9 26.5 L10.1 26.5 Z" fill="currentColor" opacity=".32"/><ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="currentColor"/><path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" fill="none"/></svg>'
SITE='https://newfor.jp'

CSS = '''
:root{--page:#F6F5F2;--band:#fff;--surface:#fff;--surface-2:#F2F1ED;--surface-3:#E5E3DD;
 --border:rgba(18,14,38,.13);--border-2:rgba(18,14,38,.22);--border-3:rgba(18,14,38,.36);
 --tx-1:#0C0A16;--tx-2:#403C55;--tx-3:#57536D;
 --accent:#2F3BD6;--accent-2:#212DBE;--accent-w:rgba(47,59,214,.08);--accent-l:rgba(47,59,214,.30);
 --gold:#C63E08;--gold-w:rgba(198,62,8,.10);--gold-l:rgba(198,62,8,.34);
 --live:#116B1D;--live-w:rgba(17,107,29,.10);--ended:#8E6BD4;--ended-w:rgba(142,107,212,.13);
 --sh:0 1px 2px rgba(24,20,40,.05),0 12px 30px -18px rgba(24,20,40,.3)}
:root[data-theme="dark"]{--page:#08080B;--band:#0C0C11;--surface:#121218;--surface-2:#191922;--surface-3:#22222D;
 --border:rgba(255,255,255,.08);--border-2:rgba(255,255,255,.14);--border-3:rgba(255,255,255,.24);
 --tx-1:#F5F5F8;--tx-2:#CBCBD6;--tx-3:#95959F;
 --accent:#7C8CFF;--accent-2:#9BA4FF;--accent-w:rgba(124,140,255,.13);--accent-l:rgba(124,140,255,.32);
 --gold:#FF6A2B;--gold-w:rgba(255,106,43,.16);--gold-l:rgba(255,106,43,.42);
 --live:#3BB44A;--live-w:rgba(59,180,74,.14);--ended:#A78BFA;--ended-w:rgba(167,139,250,.15);
 --sh:0 1px 2px rgba(0,0,0,.5),0 16px 40px -18px rgba(0,0,0,.8)}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
body{margin:0;background:var(--page);color:var(--tx-1);line-height:1.6;
 font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px}
.rd{max-width:720px;margin:0 auto;padding:0 22px}
@media (max-width:640px){.wrap,.rd{padding:0 17px}}

header{position:sticky;top:0;z-index:95;background:var(--accent);border-bottom:1px solid transparent}
:root[data-theme="dark"] header{background:color-mix(in srgb,var(--page) 88%,transparent);
 backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom-color:var(--border)}
.hd{display:flex;align-items:center;gap:12px;height:66px}
@media (max-width:760px){
 .hd{height:auto;min-height:58px;padding:9px 0 7px;flex-wrap:wrap;gap:7px}
 .brand .mark{width:27px;height:27px}
 .brand .wm{font-size:17px;letter-spacing:.13em}
 nav.main{order:3;width:100%;margin-left:0;gap:1px}
 nav.main a{font-size:12.5px;padding:6px 9px}
 .hd .tgl{margin-left:auto}}
.brand{display:flex;align-items:center;gap:10px;flex-shrink:0}
.brand .mark{width:32px;height:32px;color:#fff}
:root[data-theme="dark"] .brand .mark{color:var(--accent)}
.brand .wm{font-family:ui-monospace,Menlo,monospace;font-size:19px;font-weight:800;letter-spacing:.16em;color:#fff}
:root[data-theme="dark"] .brand .wm{color:var(--tx-1)}
.brand .wm b{color:#FF8A45}
nav.main{display:flex;gap:2px;margin-left:auto;overflow-x:auto;scrollbar-width:none}
nav.main::-webkit-scrollbar{display:none}
nav.main a{padding:8px 12px;border-radius:9px;font-size:13.5px;white-space:nowrap;color:rgba(255,255,255,.88)}
nav.main a:hover{background:rgba(255,255,255,.17);color:#fff}
:root[data-theme="dark"] nav.main a{color:var(--tx-2)}
:root[data-theme="dark"] nav.main a:hover{background:var(--surface-2);color:var(--tx-1)}
.tgl{width:32px;height:32px;border-radius:9px;border:1px solid rgba(255,255,255,.42);background:transparent;
 color:#fff;cursor:pointer;display:grid;place-items:center;flex-shrink:0;margin-left:8px}
:root[data-theme="dark"] .tgl{border-color:var(--border-2);color:var(--tx-2)}

.hero{background:linear-gradient(172deg,#2730CE 0%,#2F3BD6 52%,#3843E6 100%);color:#fff;
 padding:44px 0 52px;position:relative;overflow:hidden}
:root[data-theme="dark"] .hero{background:var(--band);color:var(--tx-1);border-bottom:1px solid var(--border)}
.hero .bg{position:absolute;right:14px;bottom:12px;width:210px;color:#fff;opacity:.13;pointer-events:none}
:root[data-theme="dark"] .hero .bg{color:var(--accent);opacity:.07}
@media (max-width:760px){.hero .bg{width:120px;right:-6px}}
.crumb{font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.06em;
 color:rgba(255,255,255,.8);margin-bottom:14px}
:root[data-theme="dark"] .crumb{color:var(--tx-3)}
.crumb a:hover{text-decoration:underline}
.hero h1{margin:0 0 16px;font-size:clamp(25px,5.2vw,42px);line-height:1.42;letter-spacing:-.035em;font-weight:850;
 max-width:22em}
.hero .dek{margin:0;font-size:clamp(14.5px,2.4vw,16.5px);line-height:1.85;color:rgba(255,255,255,.92);max-width:52em}
:root[data-theme="dark"] .hero .dek{color:var(--tx-2)}
.meta{display:flex;gap:14px;flex-wrap:wrap;margin-top:22px;font-size:12.5px;color:rgba(255,255,255,.85)}
:root[data-theme="dark"] .meta{color:var(--tx-3)}
.meta b{font-weight:700;color:#fff}
:root[data-theme="dark"] .meta b{color:var(--tx-2)}

.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:30px 0 0}
@media (max-width:860px){.kpis{grid-template-columns:1fr 1fr}}
.kpi{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.2);border-radius:13px;padding:15px 16px}
:root[data-theme="dark"] .kpi{background:var(--surface);border-color:var(--border)}
.kpi .k{font-size:11.5px;color:rgba(255,255,255,.82);font-weight:650}
:root[data-theme="dark"] .kpi .k{color:var(--tx-3)}
.kpi .v{font-size:clamp(22px,3.4vw,29px);font-weight:850;letter-spacing:-.04em;line-height:1.2;margin-top:5px;
 white-space:nowrap;color:#fff}
:root[data-theme="dark"] .kpi .v{color:var(--gold)}
.kpi .v em{font-style:normal;font-size:13px;font-weight:700;margin-left:3px;opacity:.85}

main{padding:0 0 40px}
.sum{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);
 border-radius:0 15px 15px 0;padding:24px 26px;margin:38px 0 0;box-shadow:var(--sh)}
@media (max-width:640px){.sum{padding:20px 18px}}
.sum .k{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;letter-spacing:.14em;color:var(--accent);font-weight:700;margin-bottom:12px}
.sum ol{margin:0;padding-left:1.3em}
.sum li{font-size:15.5px;line-height:1.9;margin-bottom:9px;color:var(--tx-1);font-weight:600}
.sum li:last-child{margin-bottom:0}

.toc{background:var(--surface-2);border:1px solid var(--border);border-radius:14px;padding:20px 24px;margin:28px 0 0}
.toc .k{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;letter-spacing:.14em;color:var(--tx-3);font-weight:700;margin-bottom:11px}
.toc ol{margin:0;padding-left:1.4em;font-size:14px;line-height:2}
.toc a:hover{color:var(--accent);text-decoration:underline}

article{margin-top:44px}
article h2{font-size:clamp(20px,3.6vw,27px);letter-spacing:-.032em;font-weight:850;line-height:1.5;
 margin:56px 0 18px;padding-top:10px;scroll-margin-top:80px}
article h3{font-size:17px;font-weight:800;letter-spacing:-.02em;margin:34px 0 12px}
article p{margin:0 0 26px;font-size:18px;line-height:2.05;color:var(--tx-1);letter-spacing:.005em}
@media (max-width:640px){article p{font-size:17px;line-height:2}}
article p strong,article strong{font-weight:800;background:linear-gradient(transparent 62%,var(--gold-w) 62%);padding:0 2px}
article .note{font-size:14.5px;line-height:1.95;color:var(--tx-2);background:var(--surface-2);
 border-radius:12px;padding:16px 20px;margin:0 0 26px}
article ul{margin:0 0 26px;padding-left:1.35em;font-size:17px;line-height:2}
article li{margin-bottom:10px}
blockquote{margin:0 0 26px;padding:18px 22px;background:var(--surface);border:1px solid var(--border);
 border-left:3px solid var(--gold);border-radius:0 12px 12px 0}
blockquote p{margin:0;font-size:16.5px;line-height:1.95;color:var(--tx-2)}

.cap{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;letter-spacing:.13em;color:var(--tx-3);margin-bottom:12px}
.fig{margin:34px 0 40px;background:var(--surface);border:1px solid var(--border);border-radius:16px;
 padding:24px 26px;box-shadow:var(--sh)}
@media (max-width:640px){.fig{padding:19px 15px}}
.fig h4{margin:0 0 4px;font-size:16px;font-weight:800;letter-spacing:-.02em}
.fig .sub{font-size:12.5px;color:var(--tx-3);margin-bottom:18px}

.chart{display:grid;gap:9px}
.crow{display:grid;grid-template-columns:150px 1fr 76px;gap:12px;align-items:center}
@media (max-width:640px){.crow{grid-template-columns:96px 1fr 60px;gap:8px}}
.crow .n{font-size:12.5px;color:var(--tx-2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:600}
@media (max-width:640px){.crow .n{font-size:11px}}
.trk{position:relative;height:13px}
.trk::before{content:"";position:absolute;inset:6px 0 auto 0;height:1px;background:var(--border)}
.bar{position:absolute;top:1px;height:11px;border-radius:4px;min-width:5px}
.bar.live{background:var(--accent)}
.bar.done{background:var(--ended)}
.crow .yr{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;color:var(--tx-3);text-align:right;white-space:nowrap}
.axis{display:flex;justify-content:space-between;font-family:ui-monospace,Menlo,monospace;font-size:10px;
 color:var(--tx-3);margin-top:10px;padding-left:162px}
@media (max-width:640px){.axis{padding-left:104px}}
.lg{display:flex;gap:16px;flex-wrap:wrap;margin-top:16px;font-size:12px;color:var(--tx-2)}
.lg span{display:flex;align-items:center;gap:6px}
.lg i{width:13px;height:9px;border-radius:3px;display:block}
.lg i.live{background:var(--accent)}.lg i.done{background:var(--ended)}

.tl{display:grid;gap:0;margin-top:4px}
.tl li{list-style:none;display:grid;grid-template-columns:78px 1fr auto;gap:14px;align-items:start;
 padding:13px 0;border-bottom:1px solid var(--border)}
@media (max-width:640px){.tl li{grid-template-columns:62px 1fr;gap:9px}}
.tl li:last-child{border-bottom:0}
.tl .y{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:var(--tx-3);padding-top:2px;white-space:nowrap}
.tl .ev{font-size:14.5px;line-height:1.75;font-weight:600}
.tl .ev em{display:block;font-style:normal;font-size:12.5px;color:var(--tx-3);font-weight:400;margin-top:3px;line-height:1.7}
.tl .bd{font-size:11px;font-weight:750;padding:3px 10px;border-radius:999px;white-space:nowrap;align-self:start}
@media (max-width:640px){.tl .bd{grid-column:2;justify-self:start;margin-top:5px}}
.bd.live{background:var(--live-w);color:var(--live)}
.bd.done{background:var(--ended-w);color:#5B3AA6}
:root[data-theme="dark"] .bd.done{color:var(--ended)}
.tlf{display:flex;gap:5px;margin-bottom:16px;flex-wrap:wrap}
.tlf button{border:1px solid var(--border-2);background:transparent;color:var(--tx-2);cursor:pointer;font:inherit;
 font-size:12.5px;font-weight:650;padding:6px 13px;border-radius:9px}
.tlf button.on{background:var(--accent);border-color:var(--accent);color:#fff}
:root[data-theme="dark"] .tlf button.on{color:#140E28}

.memo{background:var(--surface);border:1px solid var(--accent-l);border-radius:16px;padding:26px 28px;margin:44px 0;box-shadow:var(--sh)}
@media (max-width:640px){.memo{padding:21px 17px}}
.memo .mh{display:flex;align-items:center;gap:11px;margin-bottom:16px}
.memo .av{width:30px;height:30px;border-radius:50%;background:var(--accent-w);display:grid;place-items:center;
 color:var(--accent);flex-shrink:0}
.memo .k{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.13em;color:var(--accent);font-weight:700}
.memo .t{font-size:15px;font-weight:800;letter-spacing:-.02em;margin-top:2px}
.memo p{font-size:16.5px;line-height:1.95;margin:0 0 18px}
.memo p:last-child{margin-bottom:0}

.au{display:flex;gap:16px;background:var(--surface-2);border:1px solid var(--border);border-radius:15px;
 padding:22px 24px;margin:40px 0}
@media (max-width:640px){.au{flex-direction:column;gap:12px;padding:19px 17px}}
.au .av{width:52px;height:52px;border-radius:50%;background:var(--accent-w);display:grid;place-items:center;
 color:var(--accent);flex-shrink:0}
.au .nm{font-size:15.5px;font-weight:800;letter-spacing:-.02em}
.au .rl{font-size:12px;color:var(--tx-3);margin-top:2px}
.au .bio{font-size:13.5px;line-height:1.9;color:var(--tx-2);margin-top:9px}
.au .bg2{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px}
.au .bg2 span{font-size:11.5px;color:var(--tx-2);background:var(--surface);border:1px solid var(--border);
 padding:4px 10px;border-radius:8px}
.au .bg2 b{color:var(--gold);font-weight:800}

.src{margin:40px 0 0}
.src h3{font-size:15px;font-weight:800;margin:0 0 14px}
.src ol{margin:0;padding-left:1.5em;font-size:13px;line-height:1.95;color:var(--tx-2)}
.src li{margin-bottom:7px}
.src a{color:var(--accent)}
.src a:hover{text-decoration:underline}
.legal{font-size:12.5px;color:var(--tx-3);line-height:1.9;margin-top:26px;padding-top:20px;border-top:1px solid var(--border)}

.next{margin:44px 0 0;display:grid;grid-template-columns:1fr 1fr;gap:13px}
@media (max-width:640px){.next{grid-template-columns:1fr}}
.next a{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:18px 20px;box-shadow:var(--sh);display:block}
.next a:hover{border-color:var(--accent-l)}
.next .k{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.13em;color:var(--gold);font-weight:700}
.next .t{font-size:14.5px;font-weight:750;line-height:1.65;margin-top:7px;letter-spacing:-.02em}

footer{background:var(--band);border-top:1px solid var(--border);padding:30px 0;margin-top:50px;font-size:12.5px;color:var(--tx-3)}
footer a{color:var(--tx-2)}
footer a:hover{color:var(--accent)}
footer .ln{margin-bottom:9px}
footer .ln a{margin-right:15px}

/* 広告枠 */
.aff{border:1px solid rgba(47,59,214,.22);border-radius:18px;background:var(--surface);overflow:hidden;margin:40px 0}
:root[data-theme="dark"] .aff{border-color:var(--border)}
.aff-h{display:flex;align-items:center;gap:11px;padding:15px 20px;background:var(--accent);flex-wrap:wrap}
.aff-h .pr{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.12em;color:#fff;
 border:1px solid rgba(255,255,255,.45);border-radius:5px;padding:2px 7px}
.aff-h .t{font-size:15px;font-weight:750;letter-spacing:-.02em;color:#fff}
:root[data-theme="dark"] .aff-h{background:var(--surface-2)}
:root[data-theme="dark"] .aff-h .t{color:var(--tx-1)}
:root[data-theme="dark"] .aff-h .pr{color:var(--tx-3);border-color:var(--border-2)}
.aff-tab{display:flex;gap:3px;margin-left:auto;background:rgba(255,255,255,.2);padding:3px;border-radius:10px}
.aff-tab button{border:0;background:transparent;color:#fff;cursor:pointer;font:inherit;font-size:12px;
 font-weight:650;padding:6px 12px;border-radius:8px;white-space:nowrap}
.aff-tab button.on{background:#fff;color:#212DBE}
:root[data-theme="dark"] .aff-tab{background:rgba(127,127,140,.16)}
:root[data-theme="dark"] .aff-tab button{color:var(--tx-2)}
:root[data-theme="dark"] .aff-tab button.on{background:var(--surface);color:var(--tx-1)}
@media (max-width:560px){.aff-tab{margin-left:0;width:100%}.aff-tab button{flex:1}}
.aff-who{padding:11px 20px;font-size:12.5px;color:#2A2266;background:rgba(47,59,214,.06);
 border-bottom:1px solid var(--border);font-weight:650}
:root[data-theme="dark"] .aff-who{background:var(--surface-2);color:var(--tx-2)}
.aff-pane[hidden]{display:none}
.aff-r{display:grid;grid-template-columns:36px 1fr auto;gap:14px;align-items:center;padding:16px 20px;
 border-bottom:1px solid var(--border)}
.aff-r:last-of-type{border-bottom:0}
.aff-r.top{background:var(--gold-w)}
@media (max-width:640px){.aff-r{grid-template-columns:28px 1fr;gap:9px 11px;padding:15px 16px}
 .aff-r .btn-a{grid-column:1/-1;justify-content:center;margin-top:4px}}
.aff-r .rk{font-family:ui-monospace,Menlo,monospace;font-size:18px;font-weight:800;color:var(--tx-3);text-align:center}
.aff-r.top .rk{color:#A83203}
:root[data-theme="dark"] .aff-r.top .rk{color:var(--gold)}
.aff-r .nm{font-size:15px;font-weight:750;letter-spacing:-.02em;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.aff-r .best{font-size:10px;font-weight:700;color:#fff;background:var(--gold);border:1px solid var(--gold);
 padding:3px 9px;border-radius:999px}
:root[data-theme="dark"] .aff-r .best{color:#1A0C04}
.aff-r .ds{display:block;font-size:12.5px;color:var(--tx-2);line-height:1.7;margin-top:3px}
.aff-r .tg2{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px}
.aff-r .tg2 span{font-size:10.5px;color:var(--tx-3);background:var(--surface-2);border:1px solid var(--border);
 padding:2px 8px;border-radius:6px}
.btn-a{display:inline-flex;align-items:center;gap:7px;padding:11px 18px;border-radius:10px;background:#C63E08;
 color:#fff;font-size:13.5px;font-weight:700;white-space:nowrap;text-decoration:none}
.btn-a:hover{background:#A83203}
:root[data-theme="dark"] .btn-a{background:var(--accent);color:#140E28}
.aff-f{padding:12px 20px;font-size:11px;color:var(--tx-2);line-height:1.7;background:var(--surface-2);border-top:1px solid var(--border)}
.affmini{display:flex;align-items:center;gap:16px;background:#fff;border:1px solid rgba(47,59,214,.16);
 border-left:3px solid #2F3BD6;border-radius:0 13px 13px 0;padding:16px 18px;margin:34px 0}
:root[data-theme="dark"] .affmini{background:var(--surface-2);border-color:var(--border);border-left-color:var(--accent)}
.affmini .lead{display:flex;align-items:center;gap:8px;font-size:11.5px;color:var(--tx-3);font-weight:700;margin-bottom:5px}
.affmini .lead .pr{font-family:ui-monospace,Menlo,monospace;font-size:9.5px;letter-spacing:.1em;
 border:1px solid var(--border-2);border-radius:4px;padding:1px 5px}
.affmini .bd{flex:1;min-width:0}
.affmini .nm{display:block;font-weight:750;font-size:15px;letter-spacing:-.018em}
.affmini .ds{display:block;font-size:12.5px;color:var(--tx-2);margin-top:3px;line-height:1.7}
@media (max-width:640px){.affmini{flex-wrap:wrap;gap:11px}.affmini .btn-a{width:100%;justify-content:center}}

/* ── 新規事業マニアの解説 ── */
.voice{display:grid;grid-template-columns:44px 1fr;gap:14px;background:var(--accent-w);
 border:1px solid var(--accent-l);border-radius:16px;padding:20px 22px;margin:32px 0}
@media(max-width:640px){.voice{grid-template-columns:34px 1fr;gap:11px;padding:16px 15px;border-radius:13px}}
.voice .av{width:44px;height:44px;border-radius:50%;background:var(--accent);display:grid;place-items:center;color:#fff}
@media(max-width:640px){.voice .av{width:34px;height:34px}}
.voice .av svg{width:22px;height:22px}
@media(max-width:640px){.voice .av svg{width:17px;height:17px}}
.voice .k{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.12em;
 color:var(--accent);font-weight:700;display:block;margin-bottom:7px}
.voice p{font-size:15.5px;line-height:2;margin:0 0 13px;color:var(--tx-1)}
@media(max-width:640px){.voice p{font-size:14.5px;line-height:1.95}}
.voice p:last-child{margin-bottom:0}
.voice strong{font-weight:700;background:linear-gradient(transparent 62%,var(--accent-l) 62%)}

/* ── 用語解説 ── */
.term{border:1px solid var(--border);border-left:3px solid var(--gold);border-radius:0 12px 12px 0;
 background:var(--surface);padding:15px 18px;margin:24px 0}
.term .k{font-family:ui-monospace,Menlo,monospace;font-size:9.5px;letter-spacing:.13em;
 color:var(--gold);font-weight:700;display:block;margin-bottom:6px}
.term .w{font-size:15.5px;font-weight:800;letter-spacing:-.01em}
.term .w em{font-style:normal;font-size:12px;font-weight:600;color:var(--tx-3);margin-left:8px}
.term p{font-size:14px;line-height:1.95;color:var(--tx-2);margin:7px 0 0}

/* ── 実務のコツ ── */
.tip{background:var(--live-w);border:1px solid rgba(17,107,29,.22);border-radius:14px;padding:17px 20px;margin:26px 0}
:root[data-theme="dark"] .tip{border-color:rgba(59,180,74,.3)}
.tip .k{font-family:ui-monospace,Menlo,monospace;font-size:9.5px;letter-spacing:.13em;
 color:var(--live);font-weight:700;display:block;margin-bottom:8px}
.tip p{font-size:14.5px;line-height:1.95;margin:0 0 10px;color:var(--tx-1)}
.tip p:last-child{margin-bottom:0}
.tip strong{font-weight:700}

.kpi .kn{font-size:11px;line-height:1.7;opacity:.78;margin-top:6px;letter-spacing:0}
@media(max-width:640px){.kpi .kn{font-size:10.5px}}
.forwho{background:var(--surface);border:1px solid var(--accent-l);border-radius:15px;padding:20px 24px;margin:0 0 20px;box-shadow:var(--sh)}
@media(max-width:640px){.forwho{padding:16px 16px;border-radius:13px}}
.forwho .k{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.13em;color:var(--accent);font-weight:700;margin-bottom:11px}
.forwho ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:9px}
.forwho li{font-size:14.5px;line-height:1.75;padding-left:26px;position:relative;color:var(--tx-1)}
@media(max-width:640px){.forwho li{font-size:13.5px;padding-left:23px}}
.forwho li::before{content:"";position:absolute;left:4px;top:.55em;width:9px;height:9px;border-radius:50%;
 border:2.4px solid var(--accent)}

.aff-r .btn-a{white-space:nowrap;line-height:1.4;text-align:center;padding:12px 18px;font-size:12.5px;flex:0 0 auto}
@media(max-width:640px){.aff-r .btn-a{width:100%;font-size:12px;white-space:normal}}
.affmini .btn-a{white-space:normal;line-height:1.4;text-align:center;max-width:200px;font-size:12px;padding:10px 14px}
@media(max-width:640px){.affmini .btn-a{max-width:none;width:100%}}

/* ── 感想投票（帯で目立たせる） ── */
.react-band{background:linear-gradient(168deg,#2730CE 0%,#2F3BD6 46%,#4350EE 100%);
 margin:52px 0;padding:40px 34px;border-radius:22px;position:relative;overflow:hidden;
 box-shadow:0 10px 40px -18px rgba(47,59,214,.75)}
:root[data-theme="dark"] .react-band{background:linear-gradient(168deg,#141433 0%,#1B1B4A 50%,#242463 100%)}
.react-band::before{content:"";position:absolute;right:-90px;top:-70px;width:340px;height:340px;
 border-radius:50%;background:rgba(255,255,255,.07)}
@media(max-width:640px){.react-band{margin:38px 0;padding:26px 17px;border-radius:16px}}
.react-wrap{position:relative;z-index:1}
.react-hd{text-align:center;margin-bottom:26px}
.react-hd .k{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;letter-spacing:.19em;
 color:rgba(255,255,255,.72);font-weight:700}
.react-hd h3{font-size:27px;font-weight:800;letter-spacing:-.03em;margin:9px 0 12px;color:#fff;line-height:1.4}
@media(max-width:640px){.react-hd h3{font-size:21px}}
.react-hd p{font-size:14.5px;line-height:1.95;color:rgba(255,255,255,.9);margin:0}
@media(max-width:640px){.react-hd p{font-size:13.5px}}
.react-hd p b{font-weight:800;color:#fff;background:linear-gradient(transparent 60%,rgba(255,255,255,.26) 60%)}
.react-wrap .vhead,.react-wrap .q{display:none}
.react-wrap .vask{display:none}
.react-wrap .opts{display:flex;flex-direction:column;gap:11px;max-width:660px;margin:0 auto}
.react-wrap .opt{position:relative;display:block;width:100%;text-align:left;font:inherit;cursor:pointer;
 background:#fff;border:0;border-radius:15px;padding:18px 20px;overflow:hidden;
 box-shadow:0 3px 0 rgba(0,0,0,.16);transition:transform .13s ease,box-shadow .13s ease}
:root[data-theme="dark"] .react-wrap .opt{background:#1A1A24}
.react-wrap .vote:not(.voted) .opt:hover{transform:translateY(-3px);box-shadow:0 8px 0 rgba(0,0,0,.2)}
.react-wrap .vote:not(.voted) .opt:active{transform:translateY(0);box-shadow:0 2px 0 rgba(0,0,0,.16)}
.react-wrap .opt .fill{position:absolute;left:0;top:0;bottom:0;width:0;
 background:linear-gradient(90deg,rgba(47,59,214,.20),rgba(47,59,214,.09));
 transition:width .85s cubic-bezier(.22,1,.36,1);z-index:0}
:root[data-theme="dark"] .react-wrap .opt .fill{background:linear-gradient(90deg,rgba(124,140,255,.32),rgba(124,140,255,.12))}
.react-wrap .opt .top{position:relative;z-index:1;display:flex;align-items:center;gap:12px}
.react-wrap .opt .em{display:none}
.react-wrap .opt .nm{font-size:17px;font-weight:800;letter-spacing:-.02em;flex:1 1 auto;color:var(--tx-1)}
@media(max-width:640px){.react-wrap .opt{padding:15px 16px}.react-wrap .opt .nm{font-size:15px}}
.react-wrap .opt .you{font-size:10.5px;font-weight:800;background:var(--accent);color:#fff;
 border-radius:11px;padding:4px 10px;white-space:nowrap}
.react-wrap .opt .pct{font-size:22px;font-weight:800;color:var(--accent);
 font-family:ui-monospace,Menlo,monospace;letter-spacing:-.03em;min-width:56px;text-align:right}
@media(max-width:640px){.react-wrap .opt .pct{font-size:18px;min-width:46px}}
.react-wrap .vote:not(.voted) .opt::after{content:"選ぶ";position:absolute;right:18px;top:50%;
 transform:translateY(-50%);font-size:11.5px;font-weight:800;color:#fff;background:var(--accent);
 border-radius:20px;padding:6px 15px;z-index:1;box-shadow:0 2px 8px -2px rgba(47,59,214,.6)}
.react-wrap .opt.chosen{outline:3px solid #fff;outline-offset:2px}
.react-wrap .vfoot{margin:18px auto 0;max-width:660px;font-size:13px;color:rgba(255,255,255,.86);
 text-align:center;font-weight:600}
.react-wrap .vthx{margin:14px auto 0;max-width:660px;background:rgba(255,255,255,.15);
 border:1px solid rgba(255,255,255,.24);border-radius:13px;padding:15px 18px;
 font-size:13.5px;line-height:1.9;color:#fff;text-align:center}
.react-wrap .vthx b{font-weight:800}
.au .nm .hd2{display:inline-block;font-size:11px;font-weight:700;letter-spacing:0;
 background:var(--accent-w);color:var(--accent);border-radius:11px;padding:3px 10px;margin-left:10px;vertical-align:middle}

/* 表 */
.tbl{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:6px 0 0}
.tbl table{border-collapse:collapse;width:100%;min-width:520px;font-size:14px}
.tbl th,.tbl td{padding:11px 12px;text-align:left;border-bottom:1px solid var(--line);line-height:1.6}
.tbl th{font-size:11.5px;font-weight:800;color:var(--tx-3);letter-spacing:.02em;
  background:var(--surface-2);border-bottom:1.5px solid var(--line);white-space:nowrap;position:sticky;top:0}
.tbl td:first-child{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;color:var(--tx-3);
  width:1%;white-space:nowrap;font-variant-numeric:tabular-nums}
.tbl th.r,.tbl td.r{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;font-weight:700}
.tbl tbody tr:hover{background:var(--surface-2)}
.tbl td:nth-child(2){white-space:nowrap;word-break:keep-all}
.tbl table{min-width:600px}
.tbl tbody tr:nth-child(-n+3) td.r{color:var(--blue)}
@media (max-width:640px){.tbl table{font-size:13px;min-width:480px}.tbl th,.tbl td{padding:9px 9px}}
'''

from afflinks import END as AFFEND, END_DEFAULT as AFFEND_DEFAULT

AFF_JS = r'''
/* ============================================================
   NEWFOR 広告枠

   1行の説明では押されません。読む人が知りたいのは「自分に向いているか」。
   だから1件ごとに、要点・本文・向いている人・気になるところ・事実の一覧を出します。
   「気になるところ」は必ず出します。良い面だけ並べた瞬間に信用されなくなるからです。

   見た目のCSSはここから流し込みます。トップと企業DBは手書きHTMLで、
   ページ側のCSSに新しい書き方が入っていないためです。
   ============================================================ */
var ARROW='<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7M9 7h8v8"/></svg>';
var G=__AFFDATA__;

(function(){
 if(document.getElementById('nf-aff-css'))return;
 var st=document.createElement('style'); st.id='nf-aff-css';
 st.textContent=[
 '.nfa,.nfa *{box-sizing:border-box}',
 '.nfa{display:block;border:1px solid rgba(47,59,214,.22);border-radius:18px;overflow:hidden;margin:40px 0;background:var(--surface,#fff)}',
 '.nfa-h{display:block;padding:16px 22px;background:#2F3BD6}',
 '.nfa-h .pr{display:inline-block;font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.12em;color:#fff;border:1px solid rgba(255,255,255,.5);border-radius:4px;padding:2px 7px;margin-right:10px;vertical-align:2px}',
 '.nfa-h .t{font-size:16.5px;font-weight:800;letter-spacing:-.02em;color:#fff}',
 '.nfa-who{padding:12px 22px;font-size:12.5px;font-weight:700;color:#2A2266;background:rgba(47,59,214,.06);border-bottom:1px solid rgba(47,59,214,.12)}',
 '.nfa-lead{padding:16px 22px 4px;font-size:13.5px;line-height:1.95;color:var(--tx-2,#57536D)}',
 '.nfa-r{display:block;padding:22px;border-top:1px solid rgba(47,59,214,.12)}',
 '.nfa-r.top{background:rgba(224,74,12,.045)}',
 '.nfa-hd{display:flex;align-items:baseline;align-items:baseline;gap:10px;flex-wrap:wrap}',
 '.nfa-hd .rk{font-family:ui-monospace,Menlo,monospace;font-size:19px;font-weight:800;color:#E04A0C;min-width:20px}',
 '.nfa-hd .nm{font-size:18px;font-weight:800;letter-spacing:-.02em;color:var(--tx-1,#1A1730)}',
 '.nfa-hd .best{display:inline-block;font-size:10.5px;font-weight:800;color:#fff;background:#E04A0C;border-radius:5px;padding:3px 8px;margin-left:8px;vertical-align:2px}',
 '.nfa-catch{margin-top:8px;font-size:14.5px;font-weight:800;color:#2F3BD6;line-height:1.7}',
 '.nfa-body{margin-top:10px;font-size:13.5px;line-height:2;color:var(--tx-2,#57536D)}',
 '.nfa-body strong{color:var(--tx-1,#1A1730);font-weight:800}',
 '.nfa-cols{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}',
 '@media(max-width:680px){.nfa-cols{grid-template-columns:1fr}}',
 '.nfa-box{border-radius:12px;padding:13px 15px;font-size:12.5px;line-height:1.85}',
 '.nfa-box b{display:block;font-size:12px;font-weight:800;margin-bottom:6px;letter-spacing:.02em}',
 '.nfa-box ul{margin:0;padding-left:17px}',
 '.nfa-box li{margin:3px 0}',
 '.nfa-fit{background:rgba(47,59,214,.06);color:#2A2266}',
 '.nfa-fit b{color:#2F3BD6}',
 '.nfa-care{background:rgba(224,74,12,.07);color:#5A3320}',
 '.nfa-care b{color:#B8400F}',
 '.nfa-spec{margin:14px 0 0;display:grid;grid-template-columns:auto 1fr;gap:0;border-top:1px solid rgba(47,59,214,.12);font-size:12.5px}',
 '.nfa-spec dt{padding:8px 14px 8px 0;font-weight:800;color:var(--tx-3,#8C8497);white-space:nowrap;border-bottom:1px solid rgba(47,59,214,.08)}',
 '.nfa-spec dd{padding:8px 0;margin:0;color:var(--tx-2,#57536D);border-bottom:1px solid rgba(47,59,214,.08)}',
 '.nfa-tg{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}',
 '.nfa-tg span{font-size:11px;color:var(--tx-2,#57536D);border:1px solid rgba(47,59,214,.2);border-radius:5px;padding:3px 9px}',
 '.nfa .nfa-cta{display:inline-flex;align-items:center;justify-content:center;gap:7px;margin-top:16px;width:100%;max-width:340px;background:#C6410B;color:#fff;font-size:14px;font-weight:800;text-decoration:none;border-radius:11px;padding:14px 20px}',
 '.nfa-cta:hover{background:#A83203}',
 '.nfa-f{padding:14px 22px;font-size:11.5px;line-height:1.8;color:var(--tx-3,#8C8497);background:rgba(47,59,214,.04);border-top:1px solid rgba(47,59,214,.12)}',
 '[data-theme="dark"] .nfa{background:var(--surface,#17141F);border-color:rgba(255,255,255,.12)}',
 '[data-theme="dark"] .nfa-h{background:#232030}',
 '[data-theme="dark"] .nfa-who{background:rgba(255,255,255,.05);color:#C9C2D6}',
 '[data-theme="dark"] .nfa-r.top{background:rgba(255,138,69,.07)}',
 '[data-theme="dark"] .nfa-fit{background:rgba(154,166,255,.1);color:#C7CDF7}',
 '[data-theme="dark"] .nfa-fit b{color:#9AA6FF}',
 '[data-theme="dark"] .nfa-care{background:rgba(255,138,69,.1);color:#EBC7B2}',
 '[data-theme="dark"] .nfa-care b{color:#FF8A45}',
 '[data-theme="dark"] .nfa-catch{color:#9AA6FF}'
 ].join('\n');
 document.head.appendChild(st);
})();

var A8='https://px.a8.net/svt/ejp?a8mat=';
var A8IMG='https://www13.a8.net/0.gif?a8mat=';
function affLive(k){var g=G[k];if(!g)return null;
  var it=g.items.filter(function(x){return x.mat&&x.mat.length>8});
  return it.length?{g:g,items:it}:null;}
/* 成果計測の1×1画像。A8の規定どおり、リンクと一緒に置きます */
function px(m){return '<img border="0" width="1" height="1" src="'+A8IMG+m+'" alt="" loading="lazy">';}
function b2(t){return String(t||'').replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');}
function li(a){return (a||[]).map(function(x){return '<li>'+x+'</li>'}).join('');}
function affRow(it,i,cta){
  return '<div class="nfa-r'+(i===0?' top':'')+'">'
   +'<div class="nfa-hd"><span class="rk">'+(i+1)+'</span><span class="nm">'+it.n
   +(it.best?'<span class="best">NEWFORのおすすめ</span>':'')+'</span></div>'
   +'<div class="nfa-catch">'+it.catch+'</div>'
   +'<div class="nfa-body">'+b2(it.body)+'</div>'
   +'<div class="nfa-cols">'
     +'<div class="nfa-box nfa-fit"><b>こんな方に向いています</b><ul>'+li(it.fit)+'</ul></div>'
     +'<div class="nfa-box nfa-care"><b>気になるところ</b><ul>'+li(it.care)+'</ul></div>'
   +'</div>'
   +'<dl class="nfa-spec">'+(it.spec||[]).map(function(s){return '<dt>'+s[0]+'</dt><dd>'+s[1]+'</dd>'}).join('')+'</dl>'
   +'<div class="nfa-tg">'+(it.t||[]).map(function(x){return '<span>'+x+'</span>'}).join('')+'</div>'
   +'<a class="nfa-cta" href="'+A8+it.mat+'" target="_blank" rel="nofollow sponsored noopener">'+(it.cta||cta)+ARROW+'</a>'
   +px(it.mat)+'</div>';}
function affBuild(el){
  var live=affLive(el.getAttribute("data-aff")||"job");
  if(!live){el.remove();return;}
  el.innerHTML='<div class="nfa"><div class="nfa-h"><span class="pr">広告</span>'
   +'<span class="t">'+live.g.title+'</span></div>'
   +'<div class="nfa-who">'+live.g.who+'</div>'
   +(live.g.lead?'<div class="nfa-lead">'+live.g.lead+'</div>':'')
   +live.items.map(function(it,i){return affRow(it,i,live.g.cta)}).join('')
   +'<div class="nfa-f">本枠は広告（アフィリエイトプログラムを含みます）。'
   +'掲載内容は各社の公表情報にもとづくNEWFORの整理で、各社の公式見解ではありません。'
   +'並び順は、この記事を読んでいる方との近さで決めており、報酬額では変えません。</div></div>';
}
function affMini(el){
  var live=affLive(el.getAttribute("data-aff")||"pro");
  if(!live){el.remove();return;}
  var it=live.items[0];
  el.innerHTML='<div class="affmini"><span class="bd"><span class="lead"><span class="pr">広告</span>'+live.g.who+'</span>'
   +'<span class="nm">'+it.n+'</span><span class="ds">'+it.catch+'</span></span>'
   +'<a class="nfa-cta" href="'+A8+it.mat+'" target="_blank" rel="nofollow sponsored noopener">'+(it.cta||live.g.cta)+ARROW+'</a>'
   +px(it.mat)+'</div>';}
Array.prototype.forEach.call(document.querySelectorAll(".affslot"),affBuild);
Array.prototype.forEach.call(document.querySelectorAll(".affmini-slot"),affMini);
'''

# 広告の中身は afflinks.py が持っています。ここで焼き込むと、
# afflinks.py を直しても反映されません（実際に1度そうなりました）。
import json as _json, hashlib as _hl, os as _os
from afflinks import G as _AFFG
AFF_JS = AFF_JS.replace('__AFFDATA__', _json.dumps(_AFFG, ensure_ascii=False, separators=(',',':')))
# 外部ファイルとして書き出す。ページ側は <script src="/assets/aff.js?v=…"> を読むだけ。
_os.makedirs('gh/assets', exist_ok=True)
io.open('gh/assets/aff.js','w',encoding='utf-8').write(AFF_JS)
AFF_V = _hl.md5(AFF_JS.encode('utf-8')).hexdigest()[:8]

print("artgen part1 written")

def esc(s): return s

def render(a):
    """a: dict with article data -> full HTML string"""
    slug=a['slug']; url='/articles/%s/'%slug
    ld={"@context":"https://schema.org","@graph":[
      {"@type":"Article","@id":SITE+url+"#article","headline":a['title'],"description":a['desc'],
       "image":SITE+"/assets/og-a-%s.png"%slug,"datePublished":a['pub'],"dateModified":a['mod'],
       "author":{"@type":"Person","@id":SITE+"/#author","name":"Soichiro","alternateName":"新規事業マニア"},
       "publisher":{"@type":"Organization","@id":SITE+"/#org","name":"NEWFOR"},
       "mainEntityOfPage":SITE+url,"inLanguage":"ja","articleSection":a.get("section","新規事業ヒストリー"),
       "keywords":a['kw']},
      {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"NEWFOR","item":SITE+"/"},
        {"@type":"ListItem","position":2,"name":"記事一覧","item":SITE+"/articles/"},
        {"@type":"ListItem","position":3,"name":a['company'],"item":SITE+url}]}]}
    if a.get('legal'): ld["@graph"][0]["about"]={"@type":"Corporation","name":a['legal']}

    # KPIs
    def _kpi(t):
        k,v,u = t[0],t[1],t[2]
        note = ('<div class="kn">%s</div>'%t[3]) if len(t)>3 and t[3] else ''
        return '<div class="kpi"><div class="k">%s</div><div class="v">%s<em>%s</em></div>%s</div>'%(k,v,u,note)
    kpi=''.join(_kpi(t) for t in a['kpis'])
    # summary
    summ=''.join('<li>%s</li>'%s for s in a['summary'])
    # toc
    heads=[(i,t) for i,(tag,t) in enumerate(a['body']) if tag=='h2']
    toc=''.join('<li><a href="#s%d">%s</a></li>'%(i,t) for i,t in heads)
    toc+='<li><a href="#memo">%s</a></li>'%a['memo_t']
    # body
    bd=[]
    for i,(tag,t) in enumerate(a['body']):
        if tag=='h2': bd.append('<h2 id="s%d">%s</h2>'%(i,t))
        elif tag=='h3': bd.append('<h3>%s</h3>'%t)
        elif tag=='p': bd.append('<p>%s</p>'%t)
        elif tag=='note': bd.append('<div class="note">%s</div>'%t)
        elif tag=='voice':
            bd.append('<div class="voice"><span class="av">%s</span><div>'
              '<span class="k">新規事業マニアの解説</span>%s</div></div>'
              %(AV_SVG,''.join('<p>%s</p>'%x for x in t)))
        elif tag=='term':
            w,rd,ds=t
            bd.append('<div class="term"><span class="k">用語</span>'
              '<span class="w">%s%s</span><p>%s</p></div>'
              %(w,('<em>%s</em>'%rd) if rd else '',ds))
        elif tag=='tip':
            bd.append('<div class="tip"><span class="k">実務のコツ</span>%s</div>'
              %''.join('<p>%s</p>'%x for x in t))
        elif tag=='quote': bd.append('<blockquote><p>%s</p></blockquote>'%t)
        elif tag=='ul': bd.append('<ul>%s</ul>'%''.join('<li>%s</li>'%x for x in t))
        elif tag=='aff': bd.append('<div class="affmini-slot" data-aff="%s"></div>'%t)
        elif tag=='chart': bd.append(chart_html(a))
        elif tag=='timeline': bd.append(timeline_html(a))
        elif tag=='raw': bd.append(t)
    body='\n'.join(bd)
    memo=''.join('<p>%s</p>'%p for p in a['memo'])
    src=''.join('<li><a href="%s" rel="noopener nofollow" target="_blank">%s</a></li>'%(u,t) for t,u in a['sources'])
    nxt=''.join('<a href="%s"><div class="k">%s</div><div class="t">%s</div></a>'%(u,k,t) for k,t,u in a['next'])

    return TPL.format(title=a['title'],desc=a['desc'],url=SITE+url,slug=slug,company=a['company'],
      no=a['no'],h1=a['h1'],dek=a['dek'],date=a['datejp'],read=a['read'],kpi=kpi,summ=summ,toc=toc,
      forwho=('<div class="k">この記事はこんな方に</div><ul>%s</ul>'
        %''.join('<li>%s</li>'%x for x in a.get('forwho',[])) if a.get('forwho') else ''),
      body=body,memo=memo,memo_t=a['memo_t'],src=src,nxt=nxt,ld=json.dumps(ld,ensure_ascii=False,separators=(',',':')),
      css=CSS,affv=AFF_V,affend=AFFEND.get(slug,AFFEND_DEFAULT),ufo=UFO,tljs=TL_JS if any(t=='timeline' for t,_ in a['body']) else '')

def chart_html(a):
    lo,hi=a['span']
    rows=[]
    for n,s,e,live in a['chart']:
        left=(s-lo)/(hi-lo)*100
        end=e if e else hi
        w=max(1.6,(end-s)/(hi-lo)*100)
        yr=('%d–'%s) if live else ('%d–%d'%(s,e))
        rows.append('<div class="crow"><span class="n" title="%s">%s</span>'
          '<span class="trk"><span class="bar %s" style="left:%.2f%%;width:%.2f%%"></span></span>'
          '<span class="yr">%s</span></div>'%(n,n,'live' if live else 'done',left,w,yr))
    ticks=''.join('<span>%d</span>'%y for y in a['ticks'])
    return ('<div class="fig"><div class="cap">CHART</div><h4>%s</h4><div class="sub">%s</div>'
      '<div class="chart">%s</div><div class="axis">%s</div>'
      '<div class="lg"><span><i class="live"></i>継続中</span><span><i class="done"></i>終了・譲渡</span></div></div>'
      )%(a['chart_t'],a['chart_s'],''.join(rows),ticks)

def timeline_html(a):
    items=[]
    for y,ev,note,live in a['timeline']:
        bd='<span class="bd live">継続中</span>' if live else '<span class="bd done">終了・譲渡</span>'
        note='<em>%s</em>'%note if note else ''
        items.append('<li data-s="%s"><span class="y">%s</span><span class="ev">%s%s</span>%s</li>'%(
          'live' if live else 'done',y,ev,note,bd))
    return ('<div class="fig"><div class="cap">TIMELINE</div><h4>%s</h4><div class="sub">%s</div>'
      '<div class="tlf"><button class="on" data-f="all">すべて</button>'
      '<button data-f="live">継続中</button><button data-f="done">終了・譲渡</button></div>'
      '<ul class="tl" id="tl">%s</ul></div>')%(a['tl_t'],a['tl_s'],''.join(items))

TL_JS = '''
(function(){var tl=document.getElementById("tl");if(!tl)return;
 Array.prototype.forEach.call(document.querySelectorAll(".tlf button"),function(b){
  b.addEventListener("click",function(){
   var f=b.getAttribute("data-f");
   Array.prototype.forEach.call(document.querySelectorAll(".tlf button"),function(x){x.classList.toggle("on",x===b)});
   Array.prototype.forEach.call(tl.children,function(li){
    li.style.display=(f==="all"||li.getAttribute("data-s")===f)?"":"none";});});});})();
'''

TPL = '''<!DOCTYPE html>
<html lang="ja" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="author" content="Soichiro">
<meta name="theme-color" content="#2F3BD6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#08080B" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="article">
<meta property="og:site_name" content="NEWFOR">
<meta property="og:locale" content="ja_JP">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://newfor.jp/assets/og-a-{slug}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://newfor.jp/assets/og-a-{slug}.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-96.png" sizes="96x96" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<script type="application/ld+json">{ld}</script>
<style>{css}</style>
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
  <div class="wrap">
    <div class="crumb"><a href="/">NEWFOR</a> ／ <a href="/articles/">記事一覧</a> ／ #{no}　{company}</div>
    <h1>{h1}</h1>
    <p class="dek">{dek}</p>
    <div class="meta"><span>Soichiro</span><span><b>{date}</b></span><span>じっくり読んで 約{read}分</span></div>
    <div class="kpis">{kpi}</div>
  </div>
</div>

<main>
<div class="rd">
  <div class="forwho">{forwho}</div>
  <div class="sum"><div class="k">3行でいうと</div><ol>{summ}</ol></div>
  <div class="toc"><div class="k">目次</div><ol>{toc}</ol></div>

  <article>
{body}
  </article>

  <div class="react-band">
    <div class="react-wrap">
      <div class="react-hd">
        <span class="k">READERS' VOICE</span>
        <h3>ここまで読んだ、あなたへ</h3>
        <p><b>ひとつ選ぶと、ほかの読者が何を選んだかが、その場で見えます。</b><br>この記録がどう受け取られたのかを、みんなで確かめる場所です。</p>
      </div>
      <div class="vote-slot" data-poll="reaction-{slug}"></div>
    </div>
  </div>

  <div class="memo" id="memo" style="scroll-margin-top:84px">
    <div class="mh">
      <span class="av"><svg width="16" height="16" viewBox="0 0 32 32" fill="none">{ufo}</svg></span>
      <div><div class="k">NEWFOR MEMO</div><div class="t">{memo_t}</div></div>
    </div>
    {memo}
  </div>

  <div class="affslot" data-aff="{affend}"></div>

  <div class="au">
    <span class="av"><svg width="26" height="26" viewBox="0 0 32 32" fill="none">{ufo}</svg></span>
    <div>
      <div class="nm">Soichiro<span class="hd2">新規事業マニア</span></div>
      <div class="rl">40代 ／ 事業開発</div>
      <div class="bio">新規事業マニア。20代でスタートアップを立ち上げ、1社を上場企業へ売却。その後、外資系コンサルティングファーム、通信大手、大手人材グループ、国内大手ITサービスの中で、社員として新規事業の立ち上げに携わる。並行して顧問として10社近くの新規事業を担当。事業立ち上げ歴20年。名前は、本田宗一郎への敬意から。</div>
      <div class="bg2"><span><b>20年</b> 事業立ち上げ歴</span><span><b>1社</b> 上場企業へ売却</span><span><b>4社</b> 事業会社の中で立ち上げ</span><span><b>10社</b> 顧問として担当</span></div>
    </div>
  </div>

  <div class="next">{nxt}</div>

  <div class="src">
    <h3>出典</h3>
    <ol>{src}</ol>
    <div class="legal">掲載内容は公開情報（各社プレスリリース・IR資料・報道）に基づく筆者の整理であり、各社の公式見解ではありません。事実の誤りや抜け漏れのご指摘、掲載の取り下げのご連絡は<a href="/about/">運営者情報</a>のページから受け付けています。<br>本サイトはアフィリエイトプログラムによる収益を得ています。詳しくは<a href="/ads/">広告について</a>。</div>
  </div>
</div>
</main>

<footer><div class="wrap">
  <div class="ln"><a href="/">トップ</a><a href="/companies/">企業を探す</a><a href="/articles/">記事一覧</a><a href="/about/">運営者情報</a><a href="/ads/">広告について</a><a href="/privacy/">プライバシーポリシー</a></div>
  <div>NEWFOR ／ ニューフォー　公開情報に基づく筆者の見解であり、各社の公式見解ではありません。<br>© 2026 NEWFOR</div>
</div></footer>

<script>
(function(){{"use strict";
var theme="light",root=document.documentElement;
var moon="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z";
var sun="M12 3v2m0 14v2M5.6 5.6l1.4 1.4m10 10l1.4 1.4M3 12h2m14 0h2M5.6 18.4l1.4-1.4m10-10l1.4-1.4M12 8a4 4 0 100 8 4 4 0 000-8z";
document.getElementById("tgl").addEventListener("click",function(){{
  theme=theme==="dark"?"light":"dark";root.setAttribute("data-theme",theme);
  document.getElementById("ic-moon").setAttribute("d",theme==="dark"?moon:sun);}});
{tljs}
}})();
</script>
<script src="/assets/aff.js?v={affv}" defer></script>
<script src="/assets/vote.js?v=4" defer></script>
</body></html>
'''
