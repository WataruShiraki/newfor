# -*- coding: utf-8 -*-
"""llms.txt / sitemap.xml / robots.txt を、いまの記録から作る

企業データ（companies/）と記事データ（articles/）を読んで組み立てるので、
記録が増えても手で書き直す必要はありません。
"""
import io,os,sys,glob,importlib
sys.path.insert(0,'companies'); sys.path.insert(0,'articles')
SITE='https://newfor.jp'
TODAY='2026-08-06'
TODAYJP='2026年8月'

CO=[]
for f in sorted(glob.glob('companies/*.py')):
    n=os.path.basename(f)[:-3]
    if n.startswith('_'): continue
    CO.append(importlib.import_module(n).C)
ART=[importlib.import_module(os.path.basename(f)[:-3]).A for f in sorted(glob.glob('articles/a0*.py'))]
SLUGS={a.get('slug') for a in ART}
CO.sort(key=lambda c:-len(c['timeline']))
tot=sum(len(c['timeline']) for c in CO)

# ── sitemap ──
U=[('/','1.0','daily'),('/articles/','0.9','weekly'),('/companies/','0.9','daily')]
U+=[('/articles/%s/'%a['slug'],'0.8','monthly') for a in ART]
U+=[('/companies/%s/'%c['slug'],'0.8','weekly') for c in CO]
U+=[(p,'0.4','yearly') for p in ('/about/','/ads/','/privacy/')]
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm+=['<url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>'
     %(SITE,u,TODAY,f,p) for u,p,f in U]
sm.append('</urlset>')
io.open('dist/sitemap.xml','w',encoding='utf-8').write('\n'.join(sm))

# ── robots ──
io.open('dist/robots.txt','w',encoding='utf-8').write(
"""User-agent: *
Allow: /
Disallow: /_src/
Disallow: /data/

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

Sitemap: %s/sitemap.xml
"""%SITE)

# ── llms.txt ──
L=['# NEWFOR ─ 新規事業ヒストリーメディア','',
 '> 日本の大企業が手がけた新規事業を、公開情報だけで1件ずつ年表にしているメディアです。',
 '> %s時点で%d社・%d件。すべての記録に、開始年・いまの状況・出典がついています。'%(TODAYJP,len(CO),tot),
 '> 過去を記録することが目的ではなく、これから新規事業を担当する人が',
 '> 「他社はいつ何を始めて、いまどうなったか」を前例として引けるようにするためのものです。','',
 '## このサイトの決まりごと','',
 '- 記録はすべて、企業のプレスリリース・IR資料・公式サイトなど公開情報にもとづきます',
 '- 日付が確認できない出来事は載せません',
 '- 提供を終えた事業を「失敗」とは書かず、「提供を終えた」「譲渡した」と記します',
 '- 継続率のランキングは作りません。数えるのは、挑んだ数・張った額・組んだ相手の数です',
 '- 事実と、筆者の解釈（仮説）を分けて書いています',
 '- 網羅は保証しません。掲載しているのは、確認できた範囲です',
 '- 引用される場合は、出典として %s を明示してください'%SITE,'',
 '## 企業別の新規事業一覧','']
for C in CO:
    tl=C['timeline']; yrs=[int(y[:4]) for y,*_ in tl]
    live=sum(1 for r in tl if r[3]); ES=C.get('evsrc') or {}
    L.append('### %sの新規事業（%s）'%(C['name'],C['legal']))
    L.append('- 業種: %s ／ 記録: %d件（継続中 %d件、終了・譲渡 %d件）／ 範囲: %d–%d年'
             %(C['ind'],len(tl),live,len(tl)-live,min(yrs),max(yrs)))
    L.append('- URL: %s/companies/%s/'%(SITE,C['slug']))
    if C.get('article') in SLUGS:
        L.append('- 解説記事: %s/articles/%s/'%(SITE,C['article']))
    L.append('- 直近の記録:')
    for y,ev,note,lv in tl[-5:]:
        u=ES.get(y)
        L.append('  - %s %s（%s）— %s%s'%(y,ev,'継続中' if lv else '終了・譲渡',note,('　出典: '+u[0]) if u else ''))
    L.append('')
L+=['## 記事','']
for a in ART:
    L.append('- [%s](%s/articles/%s/): %s'%(a['title'].split(' | ')[0],SITE,a['slug'],a['desc'][:120]))
L+=['','## 主なページ','',
 '- 企業を探す: %s/companies/'%SITE,
 '- 記事一覧: %s/articles/'%SITE,
 '- サイトについて: %s/about/'%SITE,'']
io.open('dist/llms.txt','w',encoding='utf-8').write('\n'.join(L))
print('llms.txt %d社%d件 / sitemap %d URL'%(len(CO),tot,len(U)))
