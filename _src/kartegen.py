# -*- coding: utf-8 -*-
"""スタートアップ調達診断（/shindan/）を作る

  gh/shindan/                 入口＋18問の診断＋結果（1ページで動きます）
  gh/shindan/records/         先人の記録 一覧
  gh/shindan/records/<id>/    記録の詳細（20ページ）
  gh/shindan/stories/         読みもの 一覧
  gh/shindan/stories/<id>/    読みもの 本文
  gh/shindan/words/           言葉の意味（47語）

もとになるデータは karte/site_data.json・karte/stories.json・karte/q18.js。
色と部品は本体（artgen.py）と同じものを使い、差し色のオレンジを強めています。
KOTOBA.md の禁止語は SAY で言い換えてから出します。
"""
import io, os, json, re, html

BASE = '/shindan'
OUT = 'gh/shindan'
SITE = 'https://newfor.jp'

D = json.load(open('karte/site_data.json', encoding='utf-8'))
STORIES = json.load(open('karte/stories.json', encoding='utf-8'))
Q18 = io.open('karte/q18.js', encoding='utf-8').read()
CASES, GLOSS, EVENTS, LESSONS = D['cases'], D['glossary'], D['events'], D['lessons']

# ── 挑戦を否定する言葉を、事実を変えずに言い換える（KOTOBA.md）──
SAY = [
 ('調達に失敗して', '調達が決まらないまま'), ('次の調達に失敗', '次の調達が決まらないまま'),
 ('失敗談', '振り返り'), ('失敗しやすい', 'つまずきやすい'), ('失敗ではない', '悪いことではない'),
 ('失敗と同じ扱い', '対象外の扱い'), ('失敗', 'うまくいかなかったこと'),
 ('撤退を宣言', '事業の縮小を決めた'), ('段階的に撤退', '段階的に縮小'),
 ('撤退しても', '事業をやめても'), ('窓口撤廃', '窓口の取りやめ'), ('撤退', '事業の縮小'),
 ('頓挫', '止まった'), ('生き残り', '続けること'), ('生き残', '続け'),
 ('消えた', 'なくなった'), ('消滅', 'なくなること'), ('淘汰', '入れ替わり'),
 ('挫折', 'つまずき'), ('寿命', '続く長さ'), ('倒産', '破産手続き'), ('次の事業準備中', '次の事業にとりかかっている'), ('準備中', '準備を進めている'),
]
def say(t):
    if not t: return ''
    t = str(t)
    for a, b in SAY: t = t.replace(a, b)
    return t
def esc(t): return html.escape(say(t), quote=False)

STATUS = {'継続中': ('live', '続いています'), 'ピボット': ('pivot', '違う道へ'),
          'M&A': ('live', '会社を引き継いだ'), 'クローズ（自主廃業）': ('done', '一度たたんだ'),
          'クローズ（破産手続き）': ('done', '一度たたんだ'), 'クローズ（倒産）': ('done', '一度たたんだ')}
def stat(c):
    k, l = STATUS.get(c.get('status_current', ''), ('done', '記録のみ'))
    return '<span class="st %s">%s</span>' % (k, l)

# ─────────────────────────────  CSS  ─────────────────────────────
CSS = '''
:root{--page:#F6F5F2;--band:#fff;--surface:#fff;--surface-2:#F2F1ED;--surface-3:#E5E3DD;
 --border:rgba(18,14,38,.13);--border-2:rgba(18,14,38,.22);--border-3:rgba(18,14,38,.36);
 --tx-1:#0C0A16;--tx-2:#403C55;--tx-3:#57536D;
 --accent:#2F3BD6;--accent-2:#212DBE;--accent-w:rgba(47,59,214,.08);--accent-l:rgba(47,59,214,.30);
 --gold:#C63E08;--gold-2:#E8490F;--gold-w:rgba(198,62,8,.10);--gold-l:rgba(198,62,8,.34);
 --live:#116B1D;--live-w:rgba(17,107,29,.10);--ended:#8E6BD4;--ended-w:rgba(142,107,212,.13);
 --track:#E2E0DA;--sh:0 1px 2px rgba(24,20,40,.05),0 12px 30px -18px rgba(24,20,40,.3)}
:root[data-theme="dark"]{--page:#08080B;--band:#0C0C11;--surface:#121218;--surface-2:#191922;--surface-3:#22222D;
 --border:rgba(255,255,255,.08);--border-2:rgba(255,255,255,.14);--border-3:rgba(255,255,255,.24);
 --tx-1:#F5F5F8;--tx-2:#CBCBD6;--tx-3:#95959F;
 --accent:#7C8CFF;--accent-2:#9BA4FF;--accent-w:rgba(124,140,255,.13);--accent-l:rgba(124,140,255,.32);
 --gold:#FF6A2B;--gold-2:#FF7A3D;--gold-w:rgba(255,106,43,.16);--gold-l:rgba(255,106,43,.42);
 --live:#3BB44A;--live-w:rgba(59,180,74,.14);--ended:#A78BFA;--ended-w:rgba(167,139,250,.15);
 --track:#26262F;--sh:0 1px 2px rgba(0,0,0,.5),0 16px 40px -18px rgba(0,0,0,.8)}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--tx-1);line-height:1.6;
 font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
svg{display:block}
.wrap{max-width:1100px;margin:0 auto;padding:0 22px}
.rd{max-width:780px;margin:0 auto;padding:0 22px}
.mono{font-family:ui-monospace,Menlo,monospace}
.nav{background:#2730CE;position:sticky;top:0;z-index:60}
.nav .in{display:flex;align-items:center;justify-content:space-between;height:52px;gap:14px}
.brand{display:flex;align-items:center;gap:9px;color:#fff;flex:none}
.brand .mark{width:26px;height:26px}
.brand .wm{font-family:ui-monospace,Menlo,monospace;font-size:17px;font-weight:800;letter-spacing:.15em}
.brand .wm em{font-style:normal;color:#FF8A4C}
.brand .sl{font-size:11px;color:rgba(255,255,255,.72);border-left:1px solid rgba(255,255,255,.3);padding-left:9px;font-weight:600}
.nav .lk{display:flex;gap:17px;align-items:center;overflow-x:auto}
.nav .lk a{font-size:13px;color:rgba(255,255,255,.86);font-weight:600;white-space:nowrap;padding-bottom:2px;border-bottom:2px solid transparent}
.nav .lk a:hover{color:#fff;border-color:rgba(255,138,76,.5)}
.nav .lk a.on{color:#fff;border-color:#FF8A4C}
.tgl{width:27px;height:27px;border-radius:50%;border:1px solid rgba(255,255,255,.35);background:none;color:#fff;cursor:pointer;font-size:12px;flex:none}
.crumb{font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.05em;color:rgba(255,255,255,.72);padding:14px 0 0}
.crumb a:hover{color:#FF8A4C}
.hero{background:linear-gradient(172deg,#2730CE 0%,#2F3BD6 52%,#3843E6 100%);color:#fff;padding:26px 0 46px;position:relative;overflow:hidden}
.htag{display:inline-flex;align-items:center;gap:7px;background:rgba(255,138,76,.22);border:1px solid rgba(255,138,76,.5);
 border-radius:100px;padding:5px 14px;font-size:11.5px;font-weight:800;margin-bottom:16px;color:#FFD9C4}
h1{margin:0 0 14px;font-size:clamp(25px,4.3vw,39px);line-height:1.4;letter-spacing:-.04em;font-weight:850}
.hero .dek{margin:0 0 20px;font-size:15.5px;line-height:1.9;color:rgba(255,255,255,.92);max-width:34em}
.facts{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:22px}
.facts span{font-size:11.5px;font-weight:700;background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.2);border-radius:8px;padding:6px 11px}
.cta{display:inline-flex;align-items:center;gap:10px;background:var(--gold-2);color:#fff;font-weight:800;font-size:16px;
 padding:15px 30px;border-radius:12px;box-shadow:0 10px 26px -10px rgba(232,73,15,.95);border:0;cursor:pointer;font-family:inherit}
.cta:hover{background:var(--gold)}
.cta.sm{font-size:14px;padding:11px 21px}
.cta.gh{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.32);box-shadow:none;color:#fff}
.cta.ol{background:transparent;border:1.5px solid var(--gold-l);color:var(--gold);box-shadow:none}
.cta.ol:hover{background:var(--gold-w)}
.blk{padding:46px 0}
.shd{display:flex;align-items:center;gap:12px;border-bottom:2px solid var(--tx-1);padding-bottom:11px;margin:0 0 24px;flex-wrap:wrap}
.shd .m{width:25px;height:25px;color:var(--gold)}
.shd h2{margin:0;font-size:20px;letter-spacing:-.03em;font-weight:850}
.shd .sub{font-size:12.5px;color:var(--tx-3);font-weight:600}
.shd .more{margin-left:auto;font-size:12.5px;color:var(--gold);font-weight:800}
.shd .more:hover{text-decoration:underline}
p{font-size:15.5px;line-height:1.95;margin:0 0 16px}
.lead{color:var(--tx-2)}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.c3{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:24px 22px;box-shadow:var(--sh);display:block}
.c3:hover{border-color:var(--gold-l)}
.c3 .ill{width:70px;height:70px;margin-bottom:13px;color:var(--accent)}
.c3 .ill .fillw{fill:var(--accent-w)}
.c3 .no{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;letter-spacing:.13em;color:var(--gold);font-weight:800}
.c3 h4{margin:7px 0 8px;font-size:16px;font-weight:850;letter-spacing:-.02em}
.c3 p{font-size:13.5px;line-height:1.85;color:var(--tx-2);margin:0}
.c3 .go{font-size:12.5px;color:var(--gold);font-weight:800;margin-top:12px;display:block}
.opt{display:grid;grid-template-columns:24px 1fr;gap:13px;align-items:start;border:1.5px solid var(--border-2);border-radius:13px;
 padding:14px 17px;margin-bottom:9px;font-size:15px;line-height:1.7;cursor:pointer;background:var(--surface);width:100%;text-align:left;font-family:inherit;color:inherit}
.opt:hover{border-color:var(--gold-l);background:var(--gold-w)}
.opt.sel{border-color:var(--gold);background:var(--gold-w)}
.opt .rd{width:19px;height:19px;border-radius:50%;border:2px solid var(--border-3);margin-top:3px}
.opt.sel .rd{border-color:var(--gold);background:radial-gradient(circle,var(--gold) 0 5px,transparent 6px)}
.opt b{font-weight:750;display:block}
.opt small{display:block;color:var(--tx-3);font-size:12.5px;font-weight:400;margin-top:3px;line-height:1.75}
.chapn{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-bottom:6px;font-size:11.5px;font-weight:700;color:var(--tx-3)}
.chapn b{color:var(--gold)}
.chap{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-bottom:24px}
.chap div{border-radius:100px;overflow:hidden;background:var(--track);height:6px;position:relative}
.chap div i{position:absolute;inset:0 auto 0 0;background:var(--gold);border-radius:100px;transition:.25s}
.qt{font-size:clamp(19px,2.8vw,24px);font-weight:850;letter-spacing:-.03em;margin:8px 0 6px;line-height:1.5}
.qn{font-size:13.5px;color:var(--tx-3);margin:0 0 18px;line-height:1.85;background:var(--surface-2);border-radius:11px;padding:13px 16px}
.fig{margin:22px 0;background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:22px 24px;box-shadow:var(--sh)}
.fig .cap{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.14em;color:var(--gold);font-weight:800}
.fig h4{margin:7px 0 3px;font-size:16.5px;font-weight:850;letter-spacing:-.02em}
.fig .sb{font-size:12.5px;color:var(--tx-3);margin-bottom:18px;line-height:1.8}
.bars{display:grid;gap:13px}
.bar .lb{display:flex;align-items:baseline;gap:10px;font-size:14.5px;line-height:1.6;margin-bottom:6px}
.bar .lb b{font-weight:750}
.bar .lb .tg{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;color:var(--tx-3);margin-left:auto;white-space:nowrap}
.bar .tr{position:relative;height:26px;background:var(--track);border-radius:5px;overflow:hidden}
.bar .fl{position:absolute;inset:0 auto 0 0;background:var(--accent);border-radius:0 5px 5px 0;
 display:flex;align-items:center;justify-content:flex-end;padding-right:10px;transition:.5s}
.bar .fl u{text-decoration:none;color:#fff;font-weight:800;font-size:13.5px;font-family:ui-monospace,Menlo,monospace}
.bar:hover .fl{background:var(--gold)}
.axis{display:flex;justify-content:space-between;font-family:ui-monospace,Menlo,monospace;font-size:10.5px;color:var(--tx-3);margin-top:9px;padding-top:8px;border-top:1px solid var(--border)}
.den{font-size:12.5px;color:var(--tx-2);background:var(--surface-2);border-radius:11px;padding:13px 16px;margin-top:15px;line-height:1.85}
.tl2 .row{display:grid;grid-template-columns:100px 1fr;gap:13px;align-items:center;margin-bottom:10px}
.tl2 .nm{font-size:12.5px;font-weight:700;color:var(--tx-2);text-align:right}
.tl2 .tr{position:relative;height:29px;background:var(--track);border-radius:6px;display:flex;overflow:hidden}
.tl2 .sg{height:100%;display:flex;align-items:center;justify-content:center;font-size:11.5px;font-weight:700;color:#fff;border-right:2px solid var(--surface);white-space:nowrap;overflow:hidden}
.tl2 .sg.a{background:var(--accent)}.tl2 .sg.b{background:#6E77E3}.tl2 .sg.c{background:#98A0EE}.tl2 .sg.r{background:var(--gold)}
.verdict{border-radius:20px;overflow:hidden;border:1px solid var(--gold-l);margin-bottom:6px;background:var(--surface)}
.vtop{background:linear-gradient(150deg,rgba(198,62,8,.14),rgba(47,59,214,.09));padding:26px 28px}
.vk{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;letter-spacing:.14em;color:var(--gold);font-weight:800}
.vt{font-size:clamp(21px,3.4vw,30px);font-weight:850;letter-spacing:-.04em;margin:10px 0 0;line-height:1.42}
.vbody{padding:20px 28px 24px}.vbody p{margin:0;font-size:15px;line-height:1.95;color:var(--tx-2)}
.vshare{display:flex;gap:9px;padding:0 28px 22px;flex-wrap:wrap}
.vshare button,.vshare a{font-size:12.5px;font-weight:800;border:1.5px solid var(--border-2);border-radius:10px;padding:9px 15px;color:var(--tx-2);background:none;cursor:pointer;font-family:inherit}
.vshare button:hover,.vshare a:hover{border-color:var(--gold);color:var(--gold)}
.check{border-top:1px solid var(--border);padding:24px 0}
.ck{display:inline-flex;font-family:ui-monospace,Menlo,monospace;font-size:10.5px;letter-spacing:.13em;color:#fff;background:var(--gold);border-radius:6px;padding:4px 10px;font-weight:800}
.check h3{margin:11px 0 10px;font-size:19px;font-weight:850;letter-spacing:-.025em;line-height:1.5}
.check .ld{font-size:14.5px;line-height:1.95;color:var(--tx-2);margin:0 0 15px}
.steps{display:grid;gap:9px;margin:0;padding:0;list-style:none}
.steps li{display:grid;grid-template-columns:28px 1fr;gap:13px;font-size:14.5px;line-height:1.9;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 16px;align-items:center}
.steps li b{font-family:ui-monospace,Menlo,monospace;color:var(--gold);font-size:13px}
.warn{display:grid;gap:10px}
.wn{display:grid;grid-template-columns:30px 1fr;gap:13px;background:var(--gold-w);border:1px solid var(--gold-l);border-radius:13px;padding:14px 17px}
.wn svg{width:27px;color:var(--gold)}
.wn b{display:block;font-size:14.5px;font-weight:850;margin-bottom:4px}
.wn p{margin:0;font-size:13.5px;line-height:1.85;color:var(--tx-2)}
.tip{background:var(--live-w);border:1px solid rgba(17,107,29,.22);border-radius:14px;padding:16px 19px}
.tip .k{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.14em;color:var(--live);font-weight:800;display:block;margin-bottom:9px}
.tip p{font-size:14.5px;line-height:1.9;margin:0 0 7px}.tip p:last-child{margin:0}
.term{border:1px solid var(--border);border-left:3px solid var(--gold);border-radius:0 12px 12px 0;background:var(--surface);padding:15px 18px;margin:16px 0}
.term .k{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.14em;color:var(--gold);font-weight:800}
.term .w{display:block;font-weight:850;font-size:15px;margin:5px 0 6px}
.term p{font-size:14px;line-height:1.9;color:var(--tx-2);margin:0}
.term .cau{font-size:13px;color:var(--gold);margin-top:8px;font-weight:600}
.rrow{display:grid;grid-template-columns:96px 1fr auto;gap:16px;align-items:start;padding:17px 4px;border-bottom:1px solid var(--border)}
.rrow:hover{background:var(--surface-2)}
.rrow .id{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:var(--tx-3);padding-top:3px;line-height:1.8}
.rrow h4{margin:0 0 6px;font-size:15.5px;font-weight:750;line-height:1.6;letter-spacing:-.01em}
.rrow:hover h4{color:var(--gold)}
.rrow p{font-size:13.5px;line-height:1.85;color:var(--tx-2);margin:0 0 8px}
.tags{display:flex;flex-wrap:wrap;gap:6px}
.tags span,.tags a{font-size:11px;background:var(--surface-2);border:1px solid var(--border);border-radius:100px;padding:3px 10px;color:var(--tx-2)}
.tags a:hover{border-color:var(--gold);color:var(--gold)}
.st{font-size:10.5px;padding:3px 10px;border-radius:100px;white-space:nowrap;margin-top:3px;font-weight:800}
.st.live{color:var(--live);background:var(--live-w)}
.st.done{color:var(--ended);background:var(--ended-w)}
.st.pivot{color:var(--gold);background:var(--gold-w)}
.mt{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:var(--gold);font-weight:800}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
.chip{font-size:12.5px;border:1.5px solid var(--border-2);border-radius:100px;padding:6px 14px;color:var(--tx-2);cursor:pointer;background:none;font-family:inherit}
.chip.on{background:var(--gold);border-color:var(--gold);color:#fff;font-weight:800}
.gl{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:18px 20px;margin-bottom:12px}
.gl .cat{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.12em;color:var(--gold);font-weight:800}
.gl h3{margin:6px 0 4px;font-size:17px;font-weight:850;letter-spacing:-.02em}
.gl .rdg{font-size:11.5px;color:var(--tx-3);font-family:ui-monospace,Menlo,monospace}
.gl .sh{font-size:15px;font-weight:700;margin:9px 0 6px;line-height:1.85}
.gl .lo{font-size:14px;color:var(--tx-2);line-height:1.9;margin:0}
.gl .cau{font-size:13.5px;color:var(--gold);margin-top:9px;line-height:1.85;font-weight:600}
article h3{font-size:20px;font-weight:850;letter-spacing:-.025em;margin:34px 0 12px}
article p{font-size:16.5px;line-height:2.05}
article .tease{color:var(--gold);font-weight:750}
article hr{border:0;border-top:1px solid var(--border);margin:28px 0}
.rel{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px 22px;margin:26px 0}
.rel .k{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.14em;color:var(--gold);font-weight:800;display:block;margin-bottom:12px}
.rel a{color:var(--accent);font-weight:700;border-bottom:1px solid var(--accent-l)}
.rel a:hover{color:var(--gold);border-color:var(--gold-l)}
.rel ul{margin:0;padding-left:1.2em}.rel li{font-size:14.5px;line-height:1.95;margin-bottom:6px}
.nxt{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:30px 0}
.nxt a{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:18px 20px;box-shadow:var(--sh)}
.nxt a:hover{border-color:var(--gold-l)}
.nxt .k{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.13em;color:var(--gold);font-weight:800}
.nxt .t{font-size:15px;font-weight:800;margin-top:7px;line-height:1.65;letter-spacing:-.02em}
.mission{background:linear-gradient(150deg,var(--accent-w),var(--gold-w));border:1px solid var(--accent-l);border-radius:20px;padding:30px 32px;display:grid;grid-template-columns:96px 1fr;gap:24px;align-items:center;margin:40px 0}
.mission svg{width:92px;height:92px;color:var(--accent)}
.mission .fillw{fill:var(--accent-w)}
footer{background:var(--surface-2);border-top:1px solid var(--border);padding:36px 0;margin-top:52px;font-size:13px;color:var(--tx-3)}
footer a{color:var(--tx-2);font-weight:600}footer a:hover{color:var(--gold)}
footer .fl{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:14px}
.hide{display:none!important}
@media(max-width:860px){.g3,.nxt,.mission{grid-template-columns:1fr}.rrow{grid-template-columns:1fr;gap:8px}.brand .sl{display:none}}
'''

UFO = '<svg class="mark" viewBox="0 0 32 32" fill="none"><path d="M10.6 16.4 L21.4 16.4 L25.8 31 L6.2 31 Z" fill="currentColor" opacity=".22"/><path d="M12.5 16.4 L19.5 16.4 L21.9 26.5 L10.1 26.5 Z" fill="currentColor" opacity=".32"/><ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="currentColor"/><path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" fill="none"/></svg>'
MARK = '<svg class="m" viewBox="0 0 32 32" fill="none"><ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="currentColor"/><path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="currentColor" stroke-width="2.3" fill="none"/></svg>'

NAVS = [('', '診断'), ('/records/', '先人の記録'), ('/stories/', '読みもの'), ('/words/', '言葉の意味')]

def nav(cur, crumb=''):
    lk = ''.join('<a href="%s%s"%s>%s</a>' % (BASE, p, ' class="on"' if p == cur else '', t) for p, t in NAVS)
    lk += '<a href="/articles/">新規事業ヒストリー</a>'
    return ('<div class="nav"><div class="wrap in"><a class="brand" href="%s/">%s'
            '<span class="wm">NEW<em>FOR</em></span><span class="sl">スタートアップ調達診断</span></a>'
            '<div class="lk">%s<button class="tgl" onclick="tt()" aria-label="配色を切り替える"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 3v2m0 14v2M5.6 5.6l1.4 1.4m10 10l1.4 1.4M3 12h2m14 0h2M5.6 18.4l1.4-1.4m10-10l1.4-1.4M12 8a4 4 0 100 8 4 4 0 000-8z"/></svg></button></div></div>'
            '%s</div>') % (BASE, UFO, lk, crumb)

def crumb(*parts):
    out = ['<a href="/">NEWFOR</a>', '<a href="%s/">調達診断</a>' % BASE]
    out += list(parts)
    return '<div class="wrap"><div class="crumb">%s</div></div>' % ' ／ '.join(out)

FOOT = ('<footer><div class="wrap"><div class="fl">'
        '<a href="%s/">調達診断</a><a href="%s/records/">先人の記録</a><a href="%s/stories/">読みもの</a>'
        '<a href="%s/words/">言葉の意味</a><a href="/">NEWFOR トップ</a><a href="/articles/">新規事業ヒストリー</a>'
        '<a href="/companies/">企業データベース</a><a href="/about/">NEWFORについて</a></div>'
        'これから成功する経営者を、一人でも増やすために。　記録はすべて公開情報から、出典つきで要約しています。'
        '</div></footer>') % (BASE, BASE, BASE, BASE)

TT = '<script>function tt(){var r=document.documentElement;r.dataset.theme=r.dataset.theme==="dark"?"light":"dark";try{localStorage.setItem("nf-t",r.dataset.theme)}catch(e){}}try{var _t=localStorage.getItem("nf-t");if(_t)document.documentElement.dataset.theme=_t}catch(e){}</script>'

def page(title, desc, url, body, extra_head='', extra_js='', og='og-shindan.png'):
    return ('<!DOCTYPE html>\n<html lang="ja" data-theme="light">\n<head>\n<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>%s</title>\n<meta name="description" content="%s">\n'
            '<link rel="canonical" href="%s%s">\n'
            '<meta property="og:title" content="%s"><meta property="og:description" content="%s">\n'
            '<meta property="og:url" content="%s%s"><meta property="og:image" content="%s/assets/%s">\n'
            '<meta property="og:type" content="website"><meta name="twitter:card" content="summary_large_image">\n'
            '<link rel="icon" href="/favicon.ico">\n<style>%s</style>%s\n</head>\n<body>%s%s%s\n</body>\n</html>'
            ) % (title, desc, SITE, url, title, desc, SITE, url, SITE, og, CSS, extra_head, body, FOOT, TT + extra_js)

def w(path, s):
    p = os.path.join(OUT, path).replace('//', '/')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, 'w', encoding='utf-8').write(s)
    return p

# ─────────────────────────────  イラスト  ─────────────────────────────
ILL = {
'seed': '<svg class="ill" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path class="fillw" d="M32 54c-9 0-16-6-16-14 0-9 7-17 16-24 9 7 16 15 16 24 0 8-7 14-16 14Z" stroke="currentColor"/><path d="M32 46V24M32 32l-7-6M32 38l7-6"/></svg>',
'scale': '<svg class="ill" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M32 12v34M18 22h28"/><path class="fillw" d="M18 22 11 38h14L18 22Z"/><path class="fillw" d="M46 22 39 38h14L46 22Z"/><path d="M11 38a7 7 0 0 0 14 0M39 38a7 7 0 0 0 14 0"/><path d="M24 50h16"/></svg>',
'bars': '<svg class="ill" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path class="fillw" d="M8 46h48v6H8z"/><path d="M8 52h48"/><path d="M14 46V34h8v12M26 46V26h8v20M38 46V18h8v28"/></svg>',
'two': '<svg class="ill" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="22" cy="20" r="7"/><circle cx="42" cy="20" r="7" class="fillw"/><path d="M10 46c0-7 5-12 12-12s12 5 12 12M30 46c0-7 5-12 12-12s12 5 12 12"/></svg>',
'runway': '<svg class="ill" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path class="fillw" d="M6 44h52v8H6z"/><path d="M6 48h52"/><path d="M14 48V40M24 48V40M34 48V40M44 48V40" opacity=".45"/><path d="M20 30l16-8 12 6-16 8-12-6Z" class="fillw"/><path d="M36 22l4-8"/><circle cx="41" cy="12" r="2.5"/></svg>',
'book': '<svg class="ill" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path class="fillw" d="M10 14h18a6 6 0 0 1 6 6v30a6 6 0 0 0-6-6H10V14Z"/><path d="M54 14H36a6 6 0 0 0-6 6v30a6 6 0 0 1 6-6h18V14Z"/></svg>',
'talk': '<svg class="ill" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path class="fillw" d="M10 14h44v30H32l-11 8v-8H10z"/><path d="M20 26h24M20 34h14"/></svg>',
'star': '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path class="fillw" d="M32 6l6.6 13.4 14.9 2.2-10.8 10.5 2.6 14.8L32 39.9l-13.3 7 2.6-14.8L10.5 21.6l14.9-2.2L32 6Z"/><path d="M20 56h24" opacity=".5"/></svg>',
}

MISSION = ('<div class="wrap"><div class="mission">%s<div>'
  '<div class="mono" style="font-size:10.5px;letter-spacing:.14em;color:var(--gold);font-weight:800">MISSION</div>'
  '<p style="font-size:clamp(18px,2.5vw,23px);font-weight:850;letter-spacing:-.03em;line-height:1.6;margin:10px 0 12px">'
  'これから成功する経営者を、<br>一人でも増やすために。</p>'
  '<p style="font-size:14.5px;line-height:1.95;color:var(--tx-2);margin:0">'
  '先に道を通った経営者が、どこで時間を使い、何を先に決めておけばよかったと書いているか。'
  'それを出典つきで残しておけば、次に挑む方は同じところで足を止めずに済みます。'
  '<b>事業が続く数が増えれば、働く場所も、選べる未来も増えていく。</b>'
  'NEWFORはそのために記録します。</p></div></div></div>') % ILL['star']

# ═══════════════════════ 診断ページ（入口＋18問＋結果） ═══════════════════════
NC = len(CASES)
NLIVE = sum(1 for c in CASES if c.get('status_current') == '継続中')
NEQ = sum(1 for c in CASES if c.get('funding_type') == '出資')
NDE = NC - NEQ

JS_CASES = [{
 'id': c['case_id'], 'stage': c.get('stage', ''), 'region': c.get('region', ''),
 'ft': c.get('funding_type', ''), 'ev': [x.strip() for x in (c.get('event_tags') or '').split(',') if x.strip()],
 'ls': [x.strip() for x in (c.get('lesson_tags') or '').split(',') if x.strip()],
 'ttl': say(c.get('event_summary', ''))[:44], 'st': c.get('status_current', ''),
 'pr': c.get('profit_status', ''), 'co': c.get('cofounder', ''), 'rz': c.get('prior_raise', ''),
 'ex': c.get('fit_verdict_then', ''), 'sh': c.get('shareholders', ''),
} for c in CASES]

HERO = '''<div class="hero"><div class="wrap">
 <span class="htag">先に道を通った経営者%d人の記録から</span>
 <h1>その資金調達は、<br>あなたに向いていますか。</h1>
 <p class="dek">向いているかどうか。やるなら、いま何が足りないか。<b>先に道を通った経営者たちが残した記録から、あなたに近いものを探してお返しします。</b>お金を集めることが目的ではなく、事業を続けることが目的です。</p>
 <div class="facts"><span>3分</span><span>全18問</span><span>登録なし</span><span>無料</span><span>途中でやめてもOK</span></div>
 <button class="cta" onclick="start()">診断をはじめる →</button>
 <a class="cta gh sm" href="%s/records/" style="margin-left:10px">先に記録を見る</a>
</div></div>''' % (NC, BASE)

CARDS3 = '''<div class="wrap blk"><div class="shd">%s<h2>3分で、3つわかります</h2>
 <span class="sub">向いているか。足りないものは何か。先人はどうしたか。</span></div>
<div class="g3">
 <a class="c3" href="%s/words/">%s<span class="no">CHECK 1</span><h4>あなたに向いているか</h4>
  <p>株を渡すお金と、返すお金。どちらがいまのあなたに合うかを出します。<b>「まず借りるほうが合っています」と出ることもあります。</b>それも前に進む答えです。</p>
  <span class="go">言葉の意味を見る →</span></a>
 <a class="c3" href="%s/records/">%s<span class="no">CHECK 2・4</span><h4>いま、何が足りないか</h4>
  <p>足りないのはお金ではなく、時間や書類のことがあります。いまの残りから逆算して、埋めるべきものを具体的に出します。</p>
  <span class="go">記録20件を見る →</span></a>
 <a class="c3" href="%s/stories/">%s<span class="no">CHECK 3・7</span><h4>先人は、どうしたか</h4>
  <p>あなたと近い場所を通った経営者が、どこで時間を使い、そのあとどうしたか。出典つきの記録でお返しします。</p>
  <span class="go">読みものを見る →</span></a>
</div></div>''' % (MARK, BASE, ILL['scale'], BASE, ILL['bars'], BASE, ILL['two'])

DIAG_HTML = '''<div id="quiz" class="hide"><div class="rd blk">
 <div class="chapn"><span id="c1n">1. お金の性格</span><span id="c2n">2. いまの会社</span><span id="c3n">3. いまの調達</span></div>
 <div class="chap"><div><i id="b1" style="width:0"></i></div><div><i id="b2" style="width:0"></i></div><div><i id="b3" style="width:0"></i></div></div>
 <div style="display:flex;gap:18px;align-items:flex-start">
  <span id="qill" style="flex:none;width:60px;color:var(--accent)"></span>
  <div style="flex:1;min-width:0">
   <span class="mono" style="font-size:10.5px;letter-spacing:.12em;color:var(--gold);font-weight:800" id="qno"></span>
   <p class="qt" id="qt"></p><div class="qn" id="qn"></div>
  </div></div>
 <div id="qopts"></div>
 <div style="display:flex;justify-content:space-between;margin-top:22px">
  <button class="cta ol sm" onclick="back()">← もどる</button>
  <button class="cta sm hide" id="multinext" onclick="nextQ()">次へ →</button></div>
</div></div>
<div id="result" class="hide"><div class="rd blk" id="rout"></div></div>'''

def diag_js():
    return '''<script>
%s
const CASES=%s, EVENTS=%s, LESSONS=%s;
const CH=[["お金の性格",0,4],["いまの会社",4,11],["いまの調達",11,18]];
const ILLS=%s;
const RB="__B__/records/";
let ix=0, A={};
function $(i){return document.getElementById(i)}
function start(){$("top").classList.add("hide");$("result").classList.add("hide");$("quiz").classList.remove("hide");ix=0;draw();window.scrollTo(0,0)}
function draw(){
 const q=Q[ix];
 $("qno").textContent="QUESTION "+(ix+1)+" / 18";
 $("qt").textContent=q.t;
 $("qn").innerHTML=q.note?q.note:"";$("qn").style.display=q.note?"":"none";
 $("qill").innerHTML=ILLS[ix%%ILLS.length];
 CH.forEach(function(c,k){
  const done=Math.min(Math.max(ix-c[1],0),c[2]-c[1]);
  $("b"+(k+1)).style.width=(done/(c[2]-c[1])*100)+"%%";
  $("c"+(k+1)+"n").innerHTML=(ix>=c[1]&&ix<c[2])?("<b>"+(k+1)+". "+c[0]+"</b> "+(ix-c[1]+1)+"/"+(c[2]-c[1])):((k+1)+". "+c[0]+(ix>=c[2]?" 済":""));
 });
 const cur=A[q.id];
 $("qopts").innerHTML=q.o.map(function(o,i){
  const on=q.multi?((cur||[]).indexOf(o[0])>=0):(cur===o[0]);
  return '<button class="opt'+(on?' sel':'')+'" onclick="pick('+i+')"><span class="rd"></span><span><b>'+o[0]+'</b>'+(o[1]?'<small>'+o[1]+'</small>':'')+'</span></button>';
 }).join("");
 $("multinext").classList.toggle("hide",!q.multi);
}
function pick(i){
 const q=Q[ix], v=q.o[i][0];
 if(q.multi){ A[q.id]=A[q.id]||[]; const p=A[q.id].indexOf(v); if(p>=0)A[q.id].splice(p,1); else A[q.id].push(v); draw(); return; }
 A[q.id]=v; nextQ();
}
function nextQ(){ if(ix<17){ix++;draw();window.scrollTo(0,0);} else show(); }
function back(){ if(ix>0){ix--;draw();window.scrollTo(0,0);} else {$("quiz").classList.add("hide");$("top").classList.remove("hide");window.scrollTo(0,0);} }
/* ── 判定 ── */
const G2=["合わない","今の規模で十分","スモールビジネス"], G1=["条件次第","堅実に伸ばしたい","未定"];
function verdict(){
 let sc=0,hard=false;
 ["fit_control","fit_pivot","fit_horizon","fit_growth","exit_goal"].forEach(function(k){
  const v=A[k]; if(G2.indexOf(v)>=0){sc+=2;hard=true} else if(G1.indexOf(v)>=0){sc+=1}
 });
 let r = (hard||sc>=5)?"loan":(sc>=2?"mix":"equity");
 if(r==="equity"&&A.profit_status==="黒字"&&A.prior_raise==="なし") r="mix";
 return r;
}
const RUN={"3ヶ月未満":1,"3〜6ヶ月":3,"6〜12ヶ月":6,"12〜18ヶ月":12,"18ヶ月以上":18};
function show(){
 $("quiz").classList.add("hide");$("result").classList.remove("hide");
 const v=verdict(), st=A.stage||"シード";
 /* CHECK3：同じ段階の出資の記録から、事象タグを数える */
 const allEq=CASES.filter(function(c){return c.ft==="出資"});
 const same=allEq.filter(function(c){return c.stage===st});
 const pool = same.length>=5 ? same : allEq;          /* 記録が少なすぎる段階は、出資の記録ぜんぶで見ます */
 const scope = same.length>=5 ? (st+"で出資に挑んだ") : "出資に挑んだ";
 const base=pool.length;
 const cnt={}; pool.forEach(function(c){c.ev.forEach(function(e){cnt[e]=(cnt[e]||0)+1})});
 const rows=Object.keys(cnt).map(function(k){return [k,cnt[k]]}).sort(function(a,b){return b[1]-a[1]}).slice(0,6);
 const mx=rows.length?rows[0][1]:1;
 const bars=rows.map(function(r){
  return '<div class="bar"><div class="lb"><b>'+(EVENTS[r[0]]||r[0])+'</b><span class="tg">'+r[0]+'</span></div>'
   +'<div class="tr"><div class="fl" style="width:'+(r[1]/base*100).toFixed(1)+'%%"><u>'+r[1]+'人</u></div></div></div>';
 }).join("");
 /* CHECK2：必要な期間 */
 const need=6+3+2, run=RUN[A.runway_months], loan=3;
 const tot=need;
 const tl='<div class="tl2">'
  +'<div class="row"><span class="nm">出資に必要</span><div class="tr">'
  +'<div class="sg a" style="width:'+(6/tot*100)+'%%">下ごしらえ 6か月</div>'
  +'<div class="sg b" style="width:'+(3/tot*100)+'%%">市況の加算 3</div>'
  +'<div class="sg c" style="width:'+(2/tot*100)+'%%">余裕 2</div></div></div>'
  +(run?('<div class="row"><span class="nm">いまの残り</span><div class="tr"><div class="sg r" style="width:'+Math.min(run/tot*100,100)+'%%">'+run+'か月</div></div></div>'):'')
  +'<div class="row"><span class="nm">融資なら</span><div class="tr"><div class="sg a" style="width:'+(loan/tot*100)+'%%">3か月前</div></div></div>'
  +'</div>';
 /* CHECK7：近い記録 */
 const sim=CASES.map(function(c){
  let s=0;
  if(c.stage===st)s+=5;
  if(c.pr===A.profit_status)s+=2;
  if(c.co===A.cofounder)s+=1;
  if(c.rz===A.prior_raise)s+=2;
  if(c.region==="日本")s+=2;
  if(c.ft===(v==="loan"?"融資":"出資"))s+=3;
  return {c:c,s:s};
 }).sort(function(a,b){return b.s-a.s}).slice(0,3);
 const maxs=15;
 const near=sim.map(function(x){
  return '<a class="rrow" href="'+RB+x.c.id.toLowerCase()+'/"><div class="id">'+x.c.id+'<br>'+x.c.region+'／'+x.c.stage+'<br><span class="mt">近さ '+Math.round(x.s/maxs*100)+'%%</span></div>'
   +'<div><h4>'+x.c.ttl+'…</h4><div class="tags">'+x.c.ev.map(function(e){return '<span>'+e+' '+(EVENTS[e]||"")+'</span>'}).join("")+'</div></div>'
   +'<span class="st '+(x.c.st==="継続中"?"live":(x.c.st==="ピボット"?"pivot":"done"))+'">'+(x.c.st==="継続中"?"続いています":(x.c.st==="ピボット"?"違う道へ":"一度たたんだ"))+'</span></a>';
 }).join("");
 const V={
  equity:["出資に進んでよさそうです。","10年以内の出口を思い描けていて、外の人が決定に加わることも受け入れられる。この2つがそろっている方は、株と引き換えのお金と相性がいいです。次に決めるのは<b>誰から受けるか</b>です。"],
  mix:["まず融資。出資は、そのあとで。","いまの答えを見るかぎり、先に返せるお金を試す順番のほうが合います。<b>先に返せるお金で足場をつくり、足りない分だけを出資で埋める。</b>株はあとからでも渡せますが、渡した株は戻ってきません。"],
  loan:["出資は、いまは急がなくて大丈夫です。","会社の決め方を自分で持っておきたい、いまの規模で続けたい——そう答えた方に、株と引き換えのお金は向きません。<b>これはあきらめではなく、合うほうを選んだということです。</b>返すお金と補助金で伸ばす道が、あなたには開いています。"]
 }[v];
 $("rout").innerHTML =
 '<div class="verdict"><div class="vtop"><span class="vk">CHECK 1 ／ あなたに合うお金</span><div class="vt">'+V[0]+'</div></div>'
 +'<div class="vbody"><p>'+V[1]+'</p></div>'
 +'<div class="vshare"><button onclick="card()">結果を画像で保存</button><button onclick="start()">答えを変えてやり直す</button>'
 +'<a href="__B__/records/">記録を全部見る</a><a href="__B__/words/">言葉の意味</a></div></div>'

 +'<div class="check"><span class="ck">CHECK 2</span><h3>足りないのは、お金より「時間」です</h3>'
 +'<div class="fig"><span class="cap">CHART</span><h4>必要な準備の時間と、いまの残り</h4>'
 +'<div class="sb">上が出資に必要な期間、下がいまの残高でもつ期間。この差が、いま足りていないものです。</div>'+tl
 +'<div class="axis"><span>今日</span><span>6か月後</span><span>11か月後</span></div>'
 +'<div class="den"><b>いまの市況は「選別」です。</b>2026年上半期の国内スタートアップは、調達した社数が前年同期比マイナス28%%、1件あたりの中央値はプラス67%%。社数は減って、1件は大きくなっています。だから下ごしらえに3か月を足しています。（出典：STARTUP DB）</div></div></div>'

 +'<div class="check"><span class="ck">CHECK 3</span><h3>先に行った'+base+'人が、ここで時間を使いました</h3>'
 +'<p class="ld">あなたと同じ「'+scope+'」経営者<b>'+base+'人</b>の記録から。<b>ここを先に手当てしておけば、同じところで足を止めずに済みます。</b></p>'
 +'<div class="fig"><span class="cap">CHART</span><h4>先に行った'+base+'人が、時間を使ったところ</h4>'
 +'<div class="sb">灰色の帯が'+base+'人ぜんぶ。色のついた分が、そこで時間を使った人数です。</div>'
 +'<div class="bars">'+bars+'</div><div class="axis"><span>0人</span><span>'+base+'人</span></div>'
 +'<div class="den"><b>この'+base+'人は、あとから自分で振り返りを書き残してくださった経営者です。</b>世の中の起業家全体の割合ではありません。だから「％」ではなく「何人」で出しています。記録が100人を超えたら、割合でもお出しします。</div></div></div>'

 +'<div class="check"><span class="ck">CHECK 4</span><h3>先に手を打っておきたいこと</h3><div class="warn">'
 +wn("黒字は、出資では強みにならないことがあります","返せる会社と、大きく伸びる会社は、別の物差しで見られます。",A.profit_status==="黒字")
 +wn("最初の株主は、あとから替えられません","1人目に誰を入れるかで、2回目以降の話がしやすくもしにくくもなります。<a href=\\'__B__/stories/04/\\'>読みもの「あとで返すから」</a>を、株を渡す前にお読みください。",true)
 +wn("共同創業者との約束を、先に決めておいてください","辞めたときに株を買い戻せる約束（ベスティング）がないと、次の調達で止まります。<a href=\\'__B__/stories/01/\\'>読みもの「親友だから半々で」</a>にその話があります。",A.cofounder!=="いない（単独）")
 +wn("個人保証のある借入は、会社をたたんでも残ります","<a href=\\'__B__/records/l-0002/\\'>記録 L-0002</a> の方は、事業の形を変えたあとも返済が4年残っています。借りる前に、誰がいくら払うのかを確かめてください。",v!=="equity")
 +'</div></div>'

 +'<div class="check"><span class="ck">CHECK 5</span><h3>あなたの持ち札</h3><div class="tip"><span class="k">STRENGTH</span>'+strengths()+'</div></div>'
 +'<div class="check"><span class="ck">CHECK 6</span><h3>今日からできること</h3><ul class="steps">'+todo(v)+'</ul></div>'
 +'<div class="check"><span class="ck">CHECK 7</span><h3>あなたと近い場所を通った経営者</h3>'+near
 +'<div class="tip" style="margin-top:18px"><span class="k">そのあと</span><p><b>一度うまくいかなかったあと、いま続けている方の記録もあります。</b>ご本人の言葉は「恨まず前を向く」でした。<a href="__B__/records/" style="color:var(--gold);font-weight:800">記録を全部見る →</a></p></div></div>'

 +'<div class="check"><div style="background:var(--gold-w);border:1px solid var(--gold-l);border-radius:16px;padding:22px 26px">'
 +'<p style="font-size:19px;font-weight:850;margin:0 0 8px;letter-spacing:-.02em">あなたにも、あったはず。</p>'
 +'<p style="font-size:14px;color:var(--tx-2);line-height:1.9;margin:0 0 14px">本には書いていないけれど、起きたこと。三行でかまいません。名前も業種も変えて「もしもの話」に書き直します。次の方が、起きる前に読めるように。</p>'
 +'<a class="cta sm" href="/about/">送り先について →</a></div></div>'
 +'<canvas id="cv" width="1200" height="630" style="display:none"></canvas>';
 window.scrollTo(0,0);
}
function wn(t,b,on){ if(!on) return ""; return '<div class="wn"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="16" cy="16" r="12"/><path d="M16 10v8M16 22v.5"/></svg><div><b>'+t+'</b><p>'+b+'</p></div></div>'; }
function strengths(){
 const o=[];
 if(A.profit_status==="黒字")o.push("<b>黒字である</b>　返せる見込みを、数字で説明できます");
 if(A.founder_share==="80%%以上")o.push("<b>株をほとんど渡していない</b>　選べる道が、まだ残っています");
 if(A.cofounder!=="いない（単独）")o.push("<b>一緒に始めた仲間がいる</b>　単独creatorより、投資家の心配がひとつ減ります");
 if(A.founder_type==="連続起業家型")o.push("<b>起業が2回目以上</b>　一度通った道は、二度目のほうが速いです");
 if(A.years_since_founding==="1〜3年"||A.years_since_founding==="3〜5年")o.push("<b>続けてきた年数がある</b>　審査でいちばん見られるところです");
 if(!o.length)o.push("<b>まだ何も渡していない</b>　いちばん選べる場所に、あなたはいます");
 return o.map(function(x){return "<p>・"+x+"</p>"}).join("");
}
function todo(v){
 const o=[];
 if(v!=="equity"){o.push("直近2期の決算書と、今月の試算表を1か所にまとめる");o.push("取引先ごとの売上を、多い順に紙1枚に書き出す");}
 else {o.push("いま話を聞いてもらえる相手を、3人だけ書き出す");o.push("断られた理由を、必ず聞いて記録する");}
 o.push('読みもの「<a href="__B__/stories/04/" style="color:var(--gold);font-weight:800">あとで返すから</a>」を、株を渡す前に読む');
 if(A.cofounder!=="いない（単独）")o.push('<a href="__B__/words/" style="color:var(--gold);font-weight:800">ベスティング</a>の約束を、仲が良いうちに決める');
 return o.map(function(x,i){return "<li><b>0"+(i+1)+"</b><span>"+x+"</span></li>"}).join("");
}
/* ── 共有画像（その場で描いて保存） ── */
function card(){
 const v=verdict(), c=$("cv"), g=c.getContext("2d");
 const T={equity:"出資に進んでよさそうです",mix:"まず融資。出資は、そのあとで。",loan:"出資は、いまは急がなくて大丈夫"}[v];
 const gr=g.createLinearGradient(0,0,1200,630); gr.addColorStop(0,"#2730CE"); gr.addColorStop(1,"#3843E6");
 g.fillStyle=gr; g.fillRect(0,0,1200,630);
 g.fillStyle="rgba(255,138,76,.22)"; g.beginPath(); g.arc(1080,120,190,0,7); g.fill();
 g.fillStyle="#FF8A4C"; g.font="700 26px sans-serif"; g.fillText("NEWFOR ／ スタートアップ調達診断",70,96);
 g.fillStyle="#fff"; g.font="800 62px sans-serif";
 wrapText(g,T,70,230,1000,80);
 g.fillStyle="rgba(255,255,255,.9)"; g.font="500 28px sans-serif";
 g.fillText("18の質問に答えて、先に道を通った経営者"+CASES.length+"人の記録と照らしました。",70,470);
 g.fillStyle="#FFD9C4"; g.font="700 30px sans-serif"; g.fillText("newfor.jp/shindan/",70,545);
 const a=document.createElement("a"); a.download="newfor-shindan.png"; a.href=c.toDataURL("image/png"); a.click();
}
function wrapText(g,t,x,y,w,lh){ let l=""; for(const ch of t){ if(g.measureText(l+ch).width>w){g.fillText(l,x,y);y+=lh;l=ch;} else l+=ch; } g.fillText(l,x,y); }
</script>'''.replace('__B__', BASE) % (Q18, json.dumps(JS_CASES, ensure_ascii=False),
   json.dumps({k: say(v['name'] if isinstance(v, dict) else v) for k, v in EVENTS.items()}, ensure_ascii=False),
   json.dumps({k: say(v['name'] if isinstance(v, dict) else v) for k, v in LESSONS.items()}, ensure_ascii=False),
   json.dumps([ILL['seed'], ILL['scale'], ILL['two'], ILL['runway'], ILL['bars'], ILL['book']], ensure_ascii=False))

def ev_names(c):
    ts = [x.strip() for x in (c.get('event_tags') or '').split(',') if x.strip()]
    ts += [x.strip() for x in (c.get('lesson_tags') or '').split(',') if x.strip()]
    out = []
    for t in ts:
        n = EVENTS.get(t) or LESSONS.get(t) or ''
        if isinstance(n, dict): n = n.get('name', '')
        out.append('<span>%s %s</span>' % (t, esc(n)))
    return ''.join(out)

def case_title(c):
    t = say(c.get('event_summary', '')).split('。')[0]
    return esc(t[:52] + ('…' if len(t) > 52 else ''))

def cid(c): return c['case_id'].lower()

# ═══════════════════════ 先人の記録 ═══════════════════════
def build_records():
    rows = ''
    for c in CASES:
        rows += ('<a class="rrow" href="%s/records/%s/"><div class="id">%s<br>%s<br>%s</div>'
                 '<div><h4>%s</h4><p>%s</p><div class="tags">%s</div></div>%s</a>') % (
            BASE, cid(c), c['case_id'], esc(c.get('region', '')), esc(c.get('stage', '')),
            case_title(c), esc(say(c.get('event_summary', ''))[:96] + '…'), ev_names(c), stat(c))
    body = (nav('/records/', crumb('先人の記録'))
     + '<div class="wrap blk"><div class="shd">%s<h2>先人の記録</h2><span class="sub">%d人／全件に出典</span>'
       '<a class="more" href="%s/">診断をはじめる →</a></div>'
       '<p class="lead">資金調達に時間を使った経営者が、公開の場に残してくださった記録です。'
       'ご本人のnote・ブログ・海外の振り返り記事から、出典つきで要約しました。'
       '<b>出資%d件、融資%d件。いま続けている方が%d人います。</b></p>'
       '<div class="chips"><span class="chip on">すべて %d</span><span class="chip">出資 %d</span>'
       '<span class="chip">融資 %d</span><span class="chip">日本 %d</span><span class="chip">海外 %d</span></div>'
       % (MARK, NC, BASE, NEQ, NDE, NLIVE, NC, NEQ, NDE,
          sum(1 for c in CASES if c.get('region') != '海外'), sum(1 for c in CASES if c.get('region') == '海外'))
     + rows + '</div>' + MISSION)
    w('records/index.html', page('先人の記録 %d件｜スタートアップ調達診断 | NEWFOR' % NC,
      '資金調達に時間を使った経営者%d人の記録を、公開情報から出典つきで要約しました。出資%d件、融資%d件。' % (NC, NEQ, NDE),
      BASE + '/records/', body))

    for i, c in enumerate(CASES):
        prev, nxt = CASES[i - 1] if i else CASES[-1], CASES[(i + 1) % NC]
        src = c.get('source_urls', '')
        srcs = ''.join('<li><a href="%s" rel="noopener nofollow" target="_blank">%s</a></li>' % (u.strip(), u.strip()[:74])
                       for u in src.split(',') if u.strip())
        facts = [('資金の種類', c.get('funding_type')), ('段階', c.get('stage')), ('地域', c.get('region')),
                 ('創業からの年数', c.get('years_since_founding')), ('損益', c.get('profit_status')),
                 ('共同創業者', c.get('cofounder')), ('株主', c.get('shareholders')),
                 ('これまでの調達', c.get('prior_raise')), ('いまの状態', c.get('status_current')),
                 ('確認した日', c.get('status_date'))]
        tb = ''.join('<div class="cd"><div class="l">%s</div><p style="font-size:14.5px;color:var(--tx-1);font-weight:700;margin:5px 0 0">%s</p></div>'
                     % (k, esc(v)) for k, v in facts if v)
        body = (nav('/records/', crumb('<a href="%s/records/">先人の記録</a>' % BASE, c['case_id']))
         + '<div class="hero"><div class="wrap"><span class="htag">%s ／ %s ／ %s</span><h1>%s</h1></div></div>' % (
             c['case_id'], esc(c.get('region', '')), esc(c.get('stage', '')), case_title(c))
         + '<div class="rd blk">'
           '<div class="fig"><span class="cap">WHAT HAPPENED</span><h4>何が起きたか</h4>'
           '<p style="margin:12px 0 0;font-size:15.5px;line-height:2">%s</p></div>' % esc(c.get('event_summary', ''))
         + ('<div class="term"><span class="k">ご本人の言葉（要約）</span><p>%s</p></div>' % esc(c.get('sign_description', '')) if c.get('sign_description') else '')
         + ('<div class="tip"><span class="k">この方が残した学び</span><p>%s</p></div>' % esc(c.get('lesson_text', '')) if c.get('lesson_text') else '')
         + '<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:24px 0">%s</div>' % tb
         + ('<div class="den">いまの状態：<b>%s</b>　%s</div>' % (esc(c.get('status_current', '')), esc(c.get('followup_note', ''))) if c.get('followup_note') else '')
         + '<div class="rel"><span class="k">つけたタグ</span><div class="tags">%s</div></div>' % ev_names(c)
         + ('<div class="rel"><span class="k">出典</span><ul>%s</ul>'
            '<p style="font-size:13px;color:var(--tx-3);margin:12px 0 0">海外の記事は全文を訳さず、日本語の要約に出典を添えています。'
            '記載を直したい・消したいというご連絡には対応します。</p></div>' % srcs)
         + '<div class="nxt"><a href="%s/records/%s/"><div class="k">前の記録</div><div class="t">%s</div></a>'
           '<a href="%s/records/%s/"><div class="k">次の記録</div><div class="t">%s</div></a></div>' % (
             BASE, cid(prev), case_title(prev), BASE, cid(nxt), case_title(nxt))
         + '<div class="rel"><span class="k">この記録の使いかた</span><ul>'
           '<li><a href="%s/">18の質問に答えて</a>、自分に近い記録を探す</li>'
           '<li><a href="%s/words/">言葉の意味</a>で、出てきた用語を確かめる</li>'
           '<li><a href="%s/stories/">読みもの</a>で、同じことが起きる筋を先に知る</li></ul></div>' % (BASE, BASE, BASE)
         + '</div>' + MISSION)
        w('records/%s/index.html' % cid(c), page(
            '%s｜先人の記録 | NEWFOR スタートアップ調達診断' % re.sub('<[^>]+>', '', case_title(c))[:38],
            esc(say(c.get('event_summary', ''))[:110]), '%s/records/%s/' % (BASE, cid(c)), body,
            og='og-shindan-r-%s.png' % cid(c)))

# ═══════════════════════ 読みもの ═══════════════════════
def build_stories():
    cards = ''
    for s in STORIES:
        cards += ('<a class="c3" href="%s/stories/%s/">%s<span class="no">%s #%s</span>'
                  '<h4>%s</h4><p>%s</p><span class="go">読む →</span></a>') % (
            BASE, s['id'], ILL['book'], esc(s['series']), s['id'], esc(s['title']), esc(s['lead']))
    body = (nav('/stories/', crumb('読みもの'))
     + '<div class="wrap blk"><div class="shd">%s<h2>読みもの</h2><span class="sub">物語の形で、最後は「先に決めておくこと」に着地します</span>'
       '<a class="more" href="%s/">診断をはじめる →</a></div>'
       '<p class="lead">実際の記録から見えた筋を、フィクションに書き直したものです。'
       '<b>人の名前も会社の名前も、すべて架空です。</b>起きる前に読めるように、という一点のために書いています。</p>'
       '<div class="g3">%s</div></div>' % (MARK, BASE, cards) + MISSION)
    w('stories/index.html', page('読みもの｜スタートアップ調達診断 | NEWFOR',
      '共同創業者、最初の株主、資本政策。実際の記録から見えた筋を、フィクションの物語として読めるようにしました。',
      BASE + '/stories/', body, og='og-shindan-stories.png'))

    for i, s in enumerate(STORIES):
        others = [x for x in STORIES if x['id'] != s['id']]
        rec = ''.join('<li><a href="%s/records/%s/">%s</a>　%s</li>' % (BASE, r.lower(), r, case_title(c))
                      for r in (s.get('records') or []) for c in CASES if c['case_id'] == r)
        trm = '／'.join(esc(t) for t in (s.get('terms') or []))
        body = (nav('/stories/', crumb('<a href="%s/stories/">読みもの</a>' % BASE, '#' + s['id']))
         + '<div class="hero"><div class="wrap"><span class="htag">%s #%s ／ これはフィクションです</span>'
           '<h1>%s</h1><p class="dek"><b>この話で起きること：</b>%s</p></div></div>' % (
             esc(s['series']), s['id'], esc(s['title']), esc(s['lead']))
         + '<div class="rd blk"><article>%s</article>' % say(s['body'])
         + ('<div class="rel"><span class="k">関係する言葉</span><p style="margin:0;font-size:14.5px">%s'
            '　<a href="%s/words/">意味を見る →</a></p></div>' % (trm, BASE) if trm else '')
         + ('<div class="rel"><span class="k">本当にあった、近い記録</span><ul>%s</ul></div>' % rec if rec else '')
         + '<div class="nxt">' + ''.join(
             '<a href="%s/stories/%s/"><div class="k">%s #%s</div><div class="t">%s</div></a>' % (
                 BASE, o['id'], esc(o['series']), o['id'], esc(o['title'])) for o in others[:2]) + '</div>'
         + '<div class="rel"><span class="k">自分はどうか</span>'
           '<p style="margin:0 0 14px;font-size:14.5px">同じところで足を止めないために、いまの自分の場所を確かめておきませんか。</p>'
           '<a class="cta sm" href="%s/">3分の調達診断へ →</a></div>' % BASE
         + '</div>' + MISSION)
        w('stories/%s/index.html' % s['id'], page(
            '%s｜%s #%s | NEWFOR' % (re.sub('<[^>]+>', '', esc(s['title']))[:40], esc(s['series']), s['id']),
            esc(s['lead'])[:110], '%s/stories/%s/' % (BASE, s['id']), body, og='og-shindan-s-%s.png' % s['id']))

# ═══════════════════════ 言葉の意味 ═══════════════════════
def build_words():
    cats, items = [], ''
    for g in GLOSS:
        if g['cat'] not in cats: cats.append(g['cat'])
    for c in cats:
        items += '<h3 style="font-size:17px;margin:34px 0 14px;letter-spacing:-.02em">%s</h3>' % esc(c)
        for g in [x for x in GLOSS if x['cat'] == c]:
            items += ('<div class="gl"><span class="cat">%s</span><h3>%s</h3><div class="rdg">%s</div>'
                      '<p class="sh">%s</p><p class="lo">%s</p>%s</div>') % (
                esc(c), esc(g['term']), esc(g.get('read', '')), esc(g.get('short', '')), esc(g.get('long', '')),
                ('<p class="cau">よくある勘違い：%s</p>' % esc(g['caution'])) if g.get('caution') else '')
    body = (nav('/words/', crumb('言葉の意味'))
     + '<div class="rd blk"><div class="shd">%s<h2>言葉の意味</h2><span class="sub">%d語／中学生にもわかる言い方で</span>'
       '<a class="more" href="%s/">診断をはじめる →</a></div>'
       '<p class="lead">資金調達の話は、言葉がわからないだけで進めなくなります。'
       '<b>まず一行で、そのあとにもう少し詳しく。</b>よくある勘違いも書き添えました。</p>%s'
       '<div class="rel" style="margin-top:34px"><span class="k">次に</span><ul>'
       '<li><a href="%s/">18の質問に答える</a>　いまの自分に向いているお金がわかります</li>'
       '<li><a href="%s/records/">先人の記録%d件</a>　実際にその言葉が出てくる場面を読めます</li>'
       '<li><a href="%s/stories/">読みもの</a>　言葉が現実になる筋を、物語で先に知る</li></ul></div>'
       '</div>' % (MARK, len(GLOSS), BASE, items, BASE, BASE, NC, BASE) + MISSION)
    w('words/index.html', page('資金調達の言葉 %d語｜スタートアップ調達診断 | NEWFOR' % len(GLOSS),
      '出資、融資、ランウェイ、ベスティング、キャップテーブル。資金調達で出てくる%d語を、中学生にもわかる言い方でまとめました。' % len(GLOSS),
      BASE + '/words/', body, og='og-shindan-words.png'))

# ═══════════════════════ 入口（診断） ═══════════════════════
def build_index():
    body = (nav('', '')
     + '<div id="top">' + HERO + CARDS3
     + '<div class="wrap blk"><div class="shd">%s<h2>3つの約束</h2></div>'
       '<div class="g3">'
       '<div class="c3"><span class="no">01</span><h4>公開情報だけを使います</h4><p>ご本人のnote・ブログ、報道、官報・登記から、出典つきで要約します。取材や個人の相談は入れません。</p></div>'
       '<div class="c3"><span class="no">02</span><h4>否定的な言葉を使いません</h4><p>うまくいかなかったことは、判断ミスとして事実だけを書きます。<b>違う道での再チャレンジも、同じ重さで記録します。</b></p></div>'
       '<div class="c3"><span class="no">03</span><h4>お金は、スポンサー料だけ</h4><p>成果に応じた紹介料は受け取りません。投資家側からのスポンサーもお受けしません。診断の中身に、お金は関与しません。</p></div>'
       '</div></div>' % MARK
     + '<div class="wrap blk"><div class="shd">%s<h2>先人の記録から</h2><span class="sub">%d人ぶん、全件に出典</span>'
       '<a class="more" href="%s/records/">全部見る →</a></div>' % (MARK, NC, BASE)
     + ''.join('<a class="rrow" href="%s/records/%s/"><div class="id">%s<br>%s／%s</div>'
               '<div><h4>%s</h4><p>%s</p><div class="tags">%s</div></div>%s</a>' % (
                   BASE, cid(c), c['case_id'], esc(c.get('region', '')), esc(c.get('stage', '')),
                   case_title(c), esc(say(c.get('event_summary', ''))[:88] + '…'), ev_names(c), stat(c))
               for c in CASES[:4])
     + '</div>' + MISSION + '</div>'
     + DIAG_HTML)
    w('index.html', page('スタートアップ調達診断｜その資金調達は、あなたに向いていますか | NEWFOR',
      '資金調達が自分に向いているか、やるなら何が足りないかを3分18問で。先に道を通った経営者%d人の記録から、あなたに近いものを探してお返しします。' % NC,
      BASE + '/', body, extra_js=diag_js()))

def build_ogspec():
    """OGP画像の材料を書き出す（ogspec.py が読みます）"""
    P = [dict(f='og-shindan.png', eyebrow='スタートアップ調達診断',
              title='その資金調達は、<br>あなたに向いていますか。',
              sub='3分18問。先に道を通った経営者%d人の記録から探します。' % NC),
         dict(f='og-shindan-records.png', eyebrow='先人の記録',
              title='資金調達に時間を使った<br>経営者%d人の記録。' % NC,
              sub='公開情報だけを、出典つきで要約しました。'),
         dict(f='og-shindan-stories.png', eyebrow='読みもの', title='起きる前に、読めるように。',
              sub='実際の記録から見えた筋を、フィクションの物語にしました。'),
         dict(f='og-shindan-words.png', eyebrow='資金調達の言葉', title='わからない言葉で、<br>止まらないために。',
              sub='出資、融資、ランウェイ、ベスティング。中学生にもわかる言い方で。')]
    for c in CASES:
        t = re.sub('<[^>]+>', '', case_title(c))
        P.append(dict(f='og-shindan-r-%s.png' % cid(c), eyebrow='先人の記録 ／ %s' % c['case_id'],
                      title=t, sub='%s ／ %s ／ 出典つきの記録' % (say(c.get('region', '')), say(c.get('stage', '')))))
    for s_ in STORIES:
        P.append(dict(f='og-shindan-s-%s.png' % s_['id'], eyebrow='%s #%s' % (say(s_['series']), s_['id']),
                      title=re.sub('<[^>]+>', '', say(s_['title'])), sub=say(s_['lead'])[:46]))
    io.open('/tmp/shindan_og.json', 'w', encoding='utf-8').write(json.dumps(P, ensure_ascii=False))
    urls = [(BASE + '/', '0.9', 'weekly'), (BASE + '/records/', '0.8', 'weekly'),
            (BASE + '/stories/', '0.7', 'monthly'), (BASE + '/words/', '0.7', 'monthly')]
    urls += [('%s/records/%s/' % (BASE, cid(c)), '0.6', 'yearly') for c in CASES]
    urls += [('%s/stories/%s/' % (BASE, s_['id']), '0.6', 'monthly') for s_ in STORIES]
    io.open('/tmp/shindan_urls.json', 'w', encoding='utf-8').write(json.dumps(urls, ensure_ascii=False))
    return P

if __name__ == '__main__':
    build_index(); build_records(); build_stories(); build_words(); build_ogspec()
    n = sum(len(f) for _, _, f in os.walk(OUT))
    print('-> %s/  %dページ（記録%d・読みもの%d・用語%d語）' % (OUT, n, NC, len(STORIES), len(GLOSS)))
