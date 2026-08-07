# -*- coding: utf-8 -*-
"""新規事業NEWS ─ 1件に1ページを作る

これまで、トップの「新規事業NEWS」で見出しを押すと、その企業ページの
いちばん上に飛んでいました。読みたいのはその1件なのに、探し直しになる。
ここで、1件ずつのページを用意します。

■ 1枚を軽くしてある理由

企業ページは1枚98KBあります。CSSを全ページに焼き込んでいるためです。
同じ作りで1076枚つくると43MBになり、GitHubへの反映（ブラウザ経由）が
できなくなります。そこでNEWSのページだけは、CSSを /assets/news.css に
外へ出して、1枚7KB前後に抑えます。

■ 1ページに載せるもの

  1. 何があったか（年表の記録そのまま）
  2. 発表と開始で月がズレていれば、その事実
  3. Soichiroの一言（書けているものだけ。無いときは枠ごと出さない）
  4. 出典へ行くボタン（このページのいちばん大事な出口）
  5. この会社の、この前後の動き
  6. 同じころ、ほかの会社では
  7. この会社の年表へ
  8. 広告（読み終えたあとに1つだけ）

3が無いページでも、1・2・5・6・7があるので中身は薄くなりません。
"""
import io, os, re, sys, json, glob, importlib

sys.path.insert(0, 'companies')
sys.path.insert(0, 'articles')

import artgen
from artgen import CSS, UFO, SITE
import newsdata

try:
    import newscom                       # Soichiro の一言（無くても動く）
    COM = newscom.C
except Exception:
    COM = {}

PUB = '2026-08-07'      # このページ群をNEWFORが公開した日

# ─────────────────────────────────────────────
# 見た目（NEWS のページだけで使う分）
# ─────────────────────────────────────────────
NEWS_CSS = '''
.nwrap{max-width:760px;margin:0 auto;padding:0 22px}
@media(max-width:640px){.nwrap{padding:0 17px}}
.nhero{background:linear-gradient(172deg,#2730CE 0%,#2F3BD6 52%,#3843E6 100%);color:#fff;padding:34px 0 38px;position:relative;overflow:hidden}
:root[data-theme="dark"] .nhero{background:var(--band);color:var(--tx-1);border-bottom:1px solid var(--border)}
.nhero .bg{position:absolute;right:10px;bottom:6px;width:170px;color:#fff;opacity:.12;pointer-events:none}
:root[data-theme="dark"] .nhero .bg{color:var(--accent);opacity:.07}
@media(max-width:760px){.nhero .bg{width:104px;right:-8px}}
.nhero h1{margin:12px 0 0;font-size:clamp(22px,4.4vw,33px);line-height:1.5;letter-spacing:-.032em;font-weight:850}
.nchips{display:flex;gap:7px;flex-wrap:wrap;align-items:center;margin-top:15px}
.nchips a,.nchips span{font-size:12px;font-weight:700;padding:5px 11px;border-radius:20px;
 background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.26);color:#fff;white-space:nowrap}
:root[data-theme="dark"] .nchips a,:root[data-theme="dark"] .nchips span{background:var(--surface);border-color:var(--border);color:var(--tx-2)}
.nchips a:hover{background:rgba(255,255,255,.3)}
.nchips .st.live{background:rgba(255,255,255,.95);color:#116B1D;border-color:transparent}
.nchips .st.done{background:rgba(255,255,255,.95);color:#6B46C1;border-color:transparent}
.ndate{font-family:ui-monospace,Menlo,monospace;font-size:13px;letter-spacing:.06em;color:rgba(255,255,255,.92);
 display:inline-flex;align-items:baseline;gap:8px}
:root[data-theme="dark"] .ndate{color:var(--tx-2)}
.ndate em{font-style:normal;font-family:inherit;font-size:10.5px;letter-spacing:.1em;opacity:.8}
.nsec{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:24px 26px;margin:26px 0;box-shadow:var(--sh)}
@media(max-width:640px){.nsec{padding:19px 16px;border-radius:13px}}
.nsec h2{font-size:15.5px;font-weight:800;letter-spacing:-.01em;margin:0 0 12px;display:flex;align-items:center;gap:9px}
.nsec h2::before{content:"";width:3px;height:15px;background:var(--accent);border-radius:2px}
.nlede{font-size:17px;line-height:2.05;margin:0;color:var(--tx-1)}
@media(max-width:640px){.nlede{font-size:16px;line-height:1.98}}
.ngap{margin:14px 0 0;padding:11px 14px;background:var(--surface-2);border-left:3px solid var(--gold);
 border-radius:0 9px 9px 0;font-size:13px;line-height:1.9;color:var(--tx-2)}
.nsoi{background:var(--accent-w);border:1px solid var(--accent-l);border-radius:16px;padding:22px 24px;margin:26px 0}
@media(max-width:640px){.nsoi{padding:18px 16px}}
.nsoi .who{display:flex;align-items:center;gap:10px;margin-bottom:11px}
.nsoi .av{width:30px;height:30px;border-radius:50%;background:var(--accent);color:#fff;display:grid;place-items:center;flex-shrink:0}
.nsoi .av svg{width:19px;height:19px}
.nsoi .nm{font-size:12.5px;font-weight:800;letter-spacing:-.01em}
.nsoi .nm em{display:block;font-style:normal;font-size:10.5px;font-weight:600;color:var(--tx-3);letter-spacing:.03em;margin-top:1px}
.nsoi p{margin:0;font-size:15px;line-height:2.05;color:var(--tx-1)}
.nsrc{display:flex;align-items:center;justify-content:center;gap:9px;width:100%;background:var(--accent);color:#fff;
 font-size:15px;font-weight:800;border-radius:13px;padding:17px 22px;margin:6px 0 0;line-height:1.5;text-align:center}
.nsrc:hover{background:var(--accent-2)}
.nsrc svg{width:15px;height:15px;flex-shrink:0}
.nsrcn{font-size:12px;color:var(--tx-3);line-height:1.85;margin:11px 0 0;text-align:center}
.nlist{list-style:none;margin:0;padding:0}
.nlist li{border-top:1px solid var(--border)}
.nlist li:first-child{border-top:0}
.nlist a{display:grid;grid-template-columns:84px 1fr;gap:13px;padding:13px 0;align-items:baseline}
@media(max-width:640px){.nlist a{grid-template-columns:72px 1fr;gap:10px}}
.nlist a:hover .t{color:var(--accent);text-decoration:underline}
.nlist .d{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;color:var(--tx-3)}
.nlist .t{font-size:14.5px;font-weight:700;line-height:1.7}
.nlist .t em{font-style:normal;font-weight:600;font-size:12px;color:var(--tx-3);margin-left:8px}
.nlist li.here{background:var(--surface-2)}
.nlist li.here .t{color:var(--tx-3)}
.nlist li.here a{cursor:default}
.nback{display:block;background:var(--surface);border:1px solid var(--accent-l);border-radius:15px;padding:20px 23px;margin:26px 0}
.nback .k{display:block;font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.13em;color:var(--accent);font-weight:700}
.nback .t{display:block;font-size:16.5px;font-weight:800;letter-spacing:-.02em;margin-top:6px;line-height:1.6}
.nback .d{display:block;font-size:12.5px;color:var(--tx-3);margin-top:7px;line-height:1.85}
.nback:hover{border-color:var(--accent)}
.nnav{display:grid;grid-template-columns:1fr 1fr;gap:11px;margin:26px 0}
@media(max-width:640px){.nnav{grid-template-columns:1fr}}
.nnav a{background:var(--surface);border:1px solid var(--border);border-radius:13px;padding:14px 16px}
.nnav a:hover{border-color:var(--accent)}
.nnav .k{display:block;font-size:10.5px;color:var(--tx-3);font-weight:700;letter-spacing:.05em}
.nnav .t{display:block;font-size:13.5px;font-weight:700;line-height:1.65;margin-top:5px}
.nnav .nx{text-align:right}
.nyears{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
.nyears a{font-family:ui-monospace,Menlo,monospace;font-size:12px;font-weight:700;padding:6px 11px;border-radius:8px;
 border:1px solid var(--border);background:var(--surface);color:var(--tx-2)}
.nyears a:hover,.nyears a.on{border-color:var(--accent);color:var(--accent);background:var(--accent-w)}
.nnote{font-size:12px;color:var(--tx-3);line-height:1.9;margin:26px 0 0}
footer{border-top:1px solid var(--border);padding:30px 0;margin-top:44px;background:var(--band)}
.fnav{display:flex;gap:16px;flex-wrap:wrap;font-size:13px;justify-content:center}
.fnav a{color:var(--tx-2)}.fnav a:hover{color:var(--accent)}
.cp{text-align:center;font-size:11.5px;color:var(--tx-3);margin:14px 0 0}
'''

ARROWSVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
            'stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>'
            '<path d="M15 3h6v6"/><path d="M10 14L21 3"/></svg>')

HEAD = '''<!DOCTYPE html>
<html lang="ja" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#2F3BD6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#08080B" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="article">
<meta property="og:site_name" content="NEWFOR">
<meta property="og:locale" content="ja_JP">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://newfor.jp/assets/og-{og}.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://newfor.jp/assets/og-{og}.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-96.png" sizes="96x96" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="/assets/news.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<header><div class="wrap hd">
  <a class="brand" href="/"><svg class="mark" viewBox="0 0 32 32" fill="none" aria-hidden="true">{ufo}</svg><span class="wm">NEW<b>FOR</b></span></a>
  <nav class="main"><a href="/news/">新規事業NEWS</a><a href="/articles/">記事一覧</a><a href="/companies/">企業を探す</a><a href="/about/">About</a></nav>
  <button class="tgl" id="tgl" aria-label="配色を切り替える">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <path d="M12 3v2m0 14v2M5.6 5.6l1.4 1.4m10 10l1.4 1.4M3 12h2m14 0h2M5.6 18.4l1.4-1.4m10-10l1.4-1.4M12 8a4 4 0 100 8 4 4 0 000-8z"/></svg>
  </button>
</div></header>
'''

FOOT = '''
<footer><div class="wrap">
  <div class="fnav"><a href="/">トップ</a><a href="/news/">新規事業NEWS</a><a href="/companies/">企業を探す</a><a href="/articles/">記事一覧</a><a href="/about/">About</a><a href="/ads/">広告について</a><a href="/privacy/">プライバシー</a></div>
  <p class="cp">© 2026 NEWFOR</p>
</div></footer>
<script>
(function(){var t=document.getElementById("tgl"),r=document.documentElement;
 t&&t.addEventListener("click",function(){r.setAttribute("data-theme",r.getAttribute("data-theme")==="dark"?"light":"dark");});})();
</script>
<script src="/assets/aff.js" defer></script>
</body></html>
'''


def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def wlen(t):
    return sum(1 if ord(c) < 0x3000 else 2 for c in t)


def dline(it):
    """画面に出す日付。何の日付なのかを必ず添える。"""
    if it['prec'] == 'day':
        return it['date'].replace('-', '.'), '発表日'
    if it['prec'] == 'month':
        return it['date'].replace('-', '.'), 'この月の出来事'
    return it['date'], 'この年の出来事'


# ─────────────────────────────────────────────
# 広告は、そのニュースの種類で出し分ける
# ─────────────────────────────────────────────
def affkind(it):
    t = it['title'] + it['note']
    if re.search(r'設立|新設|子会社化|合弁|分社|法人化|完全子会社|会社を設立', t):
        return 'biz'
    if re.search(r'提携|協業|連携|出資|参画|共同|パートナー|協定|合意', t):
        return 'pro'
    if re.search(r'開始|参入|提供|開発|実証|発売|リリース|立ち上げ', t):
        return 'learn'
    return 'job'


# ─────────────────────────────────────────────
# 1枚を組み立てる
# ─────────────────────────────────────────────
def render(it, same_co, same_time, prev_it, next_it, coinfo):
    d, dkind = dline(it)
    h1 = '%s、%s' % (it['co'], it['title'])
    url = SITE + newsdata.path(it)

    # ── 検索結果のタイトル。60幅に収める ──
    for t in ['%s、%s｜%sの新規事業NEWS | NEWFOR' % (it['co'], it['title'], d),
              '%s、%s｜新規事業NEWS | NEWFOR' % (it['co'], it['title']),
              '%s、%s | NEWFOR' % (it['co'], it['title']),
              '%s、%s' % (it['co'], it['title'])]:
        if wlen(t) <= 62:
            title = t
            break
    else:
        title = '%s、%s' % (it['co'], it['title'])

    note = it['note'] or ''
    desc = ('%s（%s）が%s。%s' % (it['co'], d, it['title'], note))[:118]

    # ── わかっていること ──
    body = ['<div class="nsec"><h2>何があったか</h2>',
            '<p class="nlede">%s</p>' % esc(note or (it['title'] + 'ことが、公開情報から確認できます。'))]
    if it['gap']:
        g = it['gap']
        body.append('<div class="ngap">この記録の年月（%s）は、事業が動きはじめた時期です。'
                    '発表そのものは%s年%d月%d日で、ひと月以上ずれています。'
                    'NEWFORでは、発表の日ではなく、事業が動いた時期で年表に並べています。</div>'
                    % (it['ym'].replace('.', '年') + '月' if len(it['ym']) > 4 else it['ym'] + '年',
                       g[:4], int(g[5:7]), int(g[8:10])))
    body.append('</div>')

    # ── Soichiro の一言（あるときだけ） ──
    com = COM.get(it['slug'])
    if com:
        body.append(
            '<div class="nsoi"><div class="who"><span class="av">%s</span>'
            '<span class="nm">Soichiro<em>NEWFOR 編集</em></span></div><p>%s</p></div>'
            % (artgen.AV_SVG, esc(com).replace('\n', '<br>')))

    # ── 出典（このページのいちばん大事な出口） ──
    if it['src']:
        body.append('<div class="nsec"><h2>一次情報で確かめる</h2>'
                    '<a class="nsrc" href="%s" target="_blank" rel="noopener">%s%s</a>'
                    '<p class="nsrcn">%s</p></div>'
                    % (esc(it['src']), esc(it['srclabel'] or '発表を読む'), ARROWSVG,
                       'この記録は、上の一次情報だけを根拠に書いています。'
                       'NEWFORは公開情報しか使いません。'))
    else:
        body.append('<div class="nsec"><h2>一次情報で確かめる</h2>'
                    '<p class="nsrcn">この記録は、まだ出典を明示できていません。'
                    '確認できしだい、ここに一次情報のリンクを載せます。</p></div>')

    # ── 前後の1件 ──
    if prev_it or next_it:
        nav = ['<div class="nnav">']
        if prev_it:
            nav.append('<a href="%s"><span class="k">← ひとつ前の記録</span>'
                       '<span class="t">%s、%s</span></a>'
                       % (newsdata.path(prev_it), esc(prev_it['co']), esc(prev_it['title'])))
        else:
            nav.append('<span></span>')
        if next_it:
            nav.append('<a class="nx" href="%s"><span class="k">つぎの記録 →</span>'
                       '<span class="t">%s、%s</span></a>'
                       % (newsdata.path(next_it), esc(next_it['co']), esc(next_it['title'])))
        nav.append('</div>')
        body.append(''.join(nav))

    # ── この会社の、この前後 ──
    if same_co:
        rows = []
        for x in same_co:
            here = ' class="here"' if x['slug'] == it['slug'] else ''
            dd = dline(x)[0]
            rows.append('<li%s><a href="%s"><span class="d">%s</span>'
                        '<span class="t">%s</span></a></li>'
                        % (here, newsdata.path(x), dd, esc(x['title'])))
        body.append('<div class="nsec"><h2>%sの、この前後</h2><ul class="nlist">%s</ul></div>'
                    % (esc(it['co']), ''.join(rows)))

    # ── 同じころ、ほかの会社では ──
    if same_time:
        rows = ''.join('<li><a href="%s"><span class="d">%s</span>'
                       '<span class="t">%s<em>%s</em></span></a></li>'
                       % (newsdata.path(x), dline(x)[0], esc(x['title']), esc(x['co']))
                       for x in same_time)
        body.append('<div class="nsec"><h2>同じころ、ほかの会社では</h2><ul class="nlist">%s</ul></div>'
                    % rows)

    # ── 企業ページへ ──
    body.append('<a class="nback" href="/companies/%s/"><span class="k">企業の年表</span>'
                '<span class="t">%sの新規事業%d件を、年表で見る</span>'
                '<span class="d">%d年から%d年まで、開始年・いまの状況・出典つきで1件ずつ並べています。</span></a>'
                % (it['coslug'], esc(it['co']), coinfo['n'], coinfo['lo'], coinfo['hi']))

    # ── 広告は、読み終えたあとに1つだけ ──
    body.append('<div class="affslot" data-aff="%s"></div>' % affkind(it))

    body.append('<p class="nnote">この記録は、企業のプレスリリース・IR資料・公式サイトなど、'
                '公開されている情報だけを元に作成しています。網羅や最新性を保証するものではありません。'
                '誤りを見つけられた場合は <a href="/about/">About</a> のフォームからお知らせください。</p>')

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "@id": url + "#a", "headline": h1, "url": url,
         "description": desc, "inLanguage": "ja",
         "datePublished": PUB, "dateModified": PUB,
         "temporalCoverage": it['date'],
         "author": {"@type": "Organization", "name": "NEWFOR", "url": SITE},
         "publisher": {"@type": "Organization", "name": "NEWFOR", "url": SITE},
         "about": {"@type": "Organization", "name": it['colegal'], "alternateName": it['co']},
         "isPartOf": {"@type": "WebSite", "name": "NEWFOR", "url": SITE},
         "mainEntityOfPage": url},
        {"@type": "BreadcrumbList", "@id": url + "#b", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "NEWFOR", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "新規事業NEWS", "item": SITE + "/news/"},
            {"@type": "ListItem", "position": 3, "name": "%sの新規事業" % it['co'],
             "item": SITE + "/companies/%s/" % it['coslug']},
            {"@type": "ListItem", "position": 4, "name": h1, "item": url}]}]}
    if it['src']:
        ld["@graph"][0]["isBasedOn"] = it['src']
    if it['prec'] == 'day':
        ld["@graph"][0]["temporalCoverage"] = it['date']

    st = ('<span class="st live">継続中</span>' if it['live']
          else '<span class="st done">終了・譲渡</span>')
    hero = ('<div class="nhero"><svg class="bg" viewBox="0 0 32 32" fill="none" aria-hidden="true">%s</svg>'
            '<div class="nwrap">'
            '<div class="crumb"><a href="/">NEWFOR</a> ／ <a href="/news/">新規事業NEWS</a> ／ '
            '<a href="/news/%d/">%d年</a></div>'
            '<span class="ndate">%s<em>%s</em></span>'
            '<h1>%s</h1>'
            '<div class="nchips"><a href="/companies/%s/">%s</a><span>%s</span>%s</div>'
            '</div></div>') % (UFO, it['year'], it['year'], d, dkind, esc(h1),
                               it['coslug'], esc(it['co']), esc(it['ind']), st)

    return (HEAD.format(title=esc(title), desc=esc(desc), url=url,
                        og='c-%s' % it['coslug'], ld=json.dumps(ld, ensure_ascii=False), ufo=UFO)
            + hero + '<main class="nwrap">' + ''.join(body) + '</main>' + FOOT)


# ─────────────────────────────────────────────
# 一覧（/news/ と /news/<年>/）
# ─────────────────────────────────────────────
def render_list(items, years, year=None, latest=None):
    if year:
        url = SITE + '/news/%d/' % year
        title = '%d年の新規事業NEWS %d件｜大企業の発表を日付順に | NEWFOR' % (year, len(items))
        desc = ('%d年に大企業が発表した新規事業%d件を、日付の新しい順に並べています。'
                '1件ずつ出典つきで記録しています。' % (year, len(items)))
        h1 = '%d年の新規事業NEWS' % year
        lead = '%d年の記録%d件を、日付の新しい順に並べています。' % (year, len(items))
    else:
        url = SITE + '/news/'
        title = '新規事業NEWS｜大企業の新規事業を日付順に%d件 | NEWFOR' % latest
        desc = ('大企業が発表した新規事業を、日付の新しい順に記録しています。'
                '全%d件。1件ずつ出典つきで、いま続いているかどうかまで残しています。' % latest)
        h1 = '新規事業NEWS'
        lead = '大企業の新規事業を、日付の新しい順に。直近の%d件を出しています。' % len(items)

    rows = ''.join('<li><a href="%s"><span class="d">%s</span>'
                   '<span class="t">%s<em>%s</em></span></a></li>'
                   % (newsdata.path(x), dline(x)[0], esc(x['title']), esc(x['co']))
                   for x in items)
    ynav = ''.join('<a href="/news/%d/"%s>%d</a>' % (y, ' class="on"' if y == year else '', y)
                   for y in years)

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url + "#p", "name": h1, "url": url,
         "description": desc, "inLanguage": "ja",
         "isPartOf": {"@type": "WebSite", "name": "NEWFOR", "url": SITE}},
        {"@type": "BreadcrumbList", "@id": url + "#b", "itemListElement":
            ([{"@type": "ListItem", "position": 1, "name": "NEWFOR", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "新規事業NEWS", "item": SITE + "/news/"}]
             + ([{"@type": "ListItem", "position": 3, "name": h1, "item": url}] if year else []))}]}

    hero = ('<div class="nhero"><svg class="bg" viewBox="0 0 32 32" fill="none" aria-hidden="true">%s</svg>'
            '<div class="nwrap"><div class="crumb"><a href="/">NEWFOR</a> ／ '
            + ('<a href="/news/">新規事業NEWS</a> ／ %d年' % year if year else '新規事業NEWS')
            + '</div><h1>%s</h1><p class="dek" style="margin-top:12px;font-size:14.5px;line-height:1.9">%s</p>'
            '</div></div>') % (UFO, esc(h1), esc(lead))

    main = ('<main class="nwrap"><div class="nsec"><h2>年で選ぶ</h2><div class="nyears">%s</div></div>'
            '<div class="nsec"><h2>%s</h2><ul class="nlist">%s</ul></div>'
            '<div class="affslot" data-aff="job"></div>'
            '<p class="nnote">この一覧は、企業のプレスリリース・IR資料・公式サイトなど、'
            '公開されている情報だけを元に作成しています。網羅を保証するものではありません。</p></main>'
            % (ynav, '記録' if year else '新しい順', rows))

    return (HEAD.format(title=esc(title), desc=esc(desc), url=url, og='news',
                        ld=json.dumps(ld, ensure_ascii=False), ufo=UFO)
            + hero + main + FOOT)


# ─────────────────────────────────────────────
# 実行
# ─────────────────────────────────────────────
def main():
    IT = newsdata.build()
    BY = {}
    for it in IT:
        BY.setdefault(it['coslug'], []).append(it)

    coinfo = {}
    for slug, lst in BY.items():
        ys = [x['year'] for x in lst]
        coinfo[slug] = dict(n=len(lst), lo=min(ys), hi=max(ys))

    # CSS は1本にまとめて外へ出す
    os.makedirs('gh/assets', exist_ok=True)
    io.open('gh/assets/news.css', 'w', encoding='utf-8').write(CSS + NEWS_CSS)

    # 年ごと
    BYYEAR = {}
    for it in IT:
        BYYEAR.setdefault(it['year'], []).append(it)
    years = sorted(BYYEAR.keys(), reverse=True)

    n = 0
    for it in IT:
        co = BY[it['coslug']]                    # その会社の記録（新しい順）
        k = co.index(it)
        window = co[max(0, k - 3):k + 4]         # 前後3件ずつ
        # 同じころ、ほかの会社（同じ年で、いちばん近い月から）
        same_time = [x for x in BYYEAR[it['year']] if x['coslug'] != it['coslug']]
        same_time.sort(key=lambda x: (abs(x['month'] - it['month']), x['co']))
        same_time = same_time[:4]
        prev_it = IT[it['i'] + 1] if it['i'] + 1 < len(IT) else None   # 1つ古い
        next_it = IT[it['i'] - 1] if it['i'] > 0 else None             # 1つ新しい
        d = 'gh/news/%s' % it['slug']
        os.makedirs(d, exist_ok=True)
        io.open(d + '/index.html', 'w', encoding='utf-8').write(
            render(it, window, same_time, prev_it, next_it, coinfo[it['coslug']]))
        n += 1

    os.makedirs('gh/news', exist_ok=True)
    io.open('gh/news/index.html', 'w', encoding='utf-8').write(
        render_list(IT[:150], years, None, len(IT)))
    for y in years:
        os.makedirs('gh/news/%d' % y, exist_ok=True)
        io.open('gh/news/%d/index.html' % y, 'w', encoding='utf-8').write(
            render_list(BYYEAR[y], years, y, len(IT)))

    size = sum(os.path.getsize(p) for p in glob.glob('gh/news/**/index.html', recursive=True))
    print('-> gh/news/  %d件 + 一覧%d枚  合計 %.1fMB（1枚あたり %.1fKB）'
          % (n, len(years) + 1, size / 1048576.0, size / 1024.0 / (n + len(years) + 1)))
    print('   一言つき %d件 / 日まで確定 %d件'
          % (sum(1 for x in IT if COM.get(x['slug'])),
             sum(1 for x in IT if x['prec'] == 'day')))


if __name__ == '__main__':
    main()
