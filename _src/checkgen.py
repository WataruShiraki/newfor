# -*- coding: utf-8 -*-
"""生成物と生成元がズレていないか見る

llms.txt で起きた事故（古い内容を持ったスクリプトが、公開中のページを
そのまま上書きしていた）と同じことが他にないかを、毎回のビルドで確かめます。

見ているのは3つです。

1. 同じ場所を2つのスクリプトが作っていないか
   dist/ と gh/ の両方に同じ道のファイルがあって中身が違うなら、
   どちらかが古い生成元です。

2. ページに書いてある数が、いまのデータと合っているか
   タイトルや説明文の「N社」「N件」を、companies/ の中身と突き合わせます。

3. 生成元のないファイルはどれか
   手で直すしかないファイルは、忘れると古くなります。一覧に出します。
"""
import io,os,re,sys,glob,importlib
sys.path.insert(0,'companies'); sys.path.insert(0,'articles')

CO=[importlib.import_module(os.path.basename(f)[:-3]).C
    for f in sorted(glob.glob('companies/*.py')) if not os.path.basename(f).startswith('_')]
ART=[importlib.import_module(os.path.basename(f)[:-3]).A for f in sorted(glob.glob('articles/a0*.py'))]
NCO=len(CO); NBIZ=sum(len(c['timeline']) for c in CO); NART=len(ART)
BYSLUG={c['slug']:c for c in CO}

# 生成元のあるファイル（道 -> どのスクリプトが作るか）
OWNER=[(r'^gh/articles/index\.html$','mklist.py'),
       (r'^gh/articles/[^/]+/index\.html$','buildarticles.py'),
       (r'^gh/companies/[^/]+/index\.html$','mkcomp.py'),
       (r'^gh/(about|ads|privacy)/index\.html$','mkpages.py'),
       (r'^gh/(llms\.txt|sitemap\.xml|robots\.txt)$','extras.py'),
       (r'^gh/index\.html$','レイアウトは手／数は mktop.py'),
       (r'^gh/companies/index\.html$','レイアウトは手／数は mkcompidx.py'),
       (r'^gh/news/index\.html$','newsgen.py'),
       (r'^gh/news/\d{4}/index\.html$','newsgen.py'),
       (r'^gh/news/[^/]+/index\.html$','newsgen.py'),
       (r'^gh/supabase/','schema は手／poll.sql は pollgen.py'),
       (r'^gh/assets/','assets.py / png.js / og.js / newsgen.py / pollgen.py')]
def owner(p):
    for r,g in OWNER:
        if re.match(r,p): return g
    return None

bad=[]; hand=[]

# ── 1. 同じ場所を2つが作っていないか ──
def norm(p):
    s=io.open(p,'rb').read().decode('utf-8','replace')
    return re.sub(r'\s+','',re.sub(r'<lastmod>[^<]*</lastmod>','',s))
for p in sorted(glob.glob('gh/**/*',recursive=True)):
    if not os.path.isfile(p) or p.startswith('gh/_src/'): continue
    d='dist/'+p[3:]
    if os.path.exists(d) and owner(p) is None and norm(p)!=norm(d):
        bad.append('%s を dist にも作っているのに中身が違う（生成元が2つある疑い）'%p)

# ── 2. ページの数が、いまのデータと合っているか ──
def txt(p):
    return io.open(p,encoding='utf-8').read() if os.path.exists(p) else ''
for p,label in [('gh/index.html','トップ'),('gh/companies/index.html','企業DB'),
                ('gh/llms.txt','llms.txt'),('gh/articles/index.html','記事一覧')]:
    s=txt(p)
    if not s: bad.append('%s が見あたらない'%p); continue
    # 見るのは、サイト全体の数を名乗っている場所だけ。
    # 本文の中には「認定事業者88社」のような、記録の数ではない数が出てきます。
    if p.endswith('.txt'):
        head=s.split('## ')[0]                       # llms.txt は冒頭の要約だけ
    else:
        head=re.sub(r'<style.*?</style>','',s[:s.index('</head>')+7],flags=re.S)
        m=re.search(r'<p class="hsub">.*?</p>',s,re.S)  # 企業DBの見出し下
        if m: head+=m.group(0)
        for m in re.finditer(r'<span class="ex-k">.*?</span>\s*<span class="ex-n">\d+',s,re.S):
            head+=m.group(0)                            # トップの数字4つ
    # 「10社近く」のような概数は、記録の数ではないので見ない
    for n in set(int(x) for x in re.findall(r'(\d{2,4})社(?!近く|ほど|程度|以上|未満|前後|余り)',head)):
        if n!=NCO: bad.append('%s（%s）に「%d社」とあるが、いまは%d社'%(p,label,n,NCO))
    for n in set(int(x) for x in re.findall(r'(\d{3,5})件',head)):
        if n!=NBIZ: bad.append('%s（%s）に「%d件」とあるが、いまは%d件'%(p,label,n,NBIZ))

# ── Search Console の所有権確認タグが全ページに入っているか ──
# ページを作り直したあとに analytics.py を走らせないと消えます。実際に一度消えました。
for p in sorted(glob.glob('gh/**/*.html',recursive=True)):
    if p.startswith('gh/_src/'): continue
    s=txt(p)
    if '</head>' in s and 'google-site-verification' not in s.split('</head>')[0]:
        bad.append('%s に Search Console の所有権確認タグがない'%p)

for p in sorted(glob.glob('gh/companies/*/index.html')):
    slug=p.split('/')[2]; C=BYSLUG.get(slug)
    if not C: bad.append('%s に対応する companies/%s.py がない'%(p,slug)); continue
    t=re.search(r'<title>(.*?)</title>',txt(p),re.S)
    if t:
        m=re.search(r'(\d+)件',t.group(1))
        if m and int(m.group(1))!=len(C['timeline']):
            bad.append('%s のタイトルは「%s件」だが、年表は%d件'%(p,m.group(1),len(C['timeline'])))

# ── 記事タイトルの「N件」が、その企業の年表と合っているか ──
#
# 年表に1件足したときに、記事のタイトルだけが古いまま残ります。
# 実際にKDDIが「18件」のまま残っていて、年表は19件になっていました。
for f in sorted(glob.glob('articles/a0*.py')):
    A=importlib.import_module(os.path.basename(f)[:-3]).A
    cs=A['slug'].replace('-newbusiness','')
    C=BYSLUG.get(cs)
    if not C: continue
    m=re.search(r'(\d+)件',A.get('title') or '')
    if m and int(m.group(1))!=len(C['timeline']):
        bad.append('%s のタイトルは「%s件」だが、%s の年表は%d件'
                   %(f,m.group(1),cs,len(C['timeline'])))

# ── 広告リンクが、記事に入っているか ──
#
# afflinks.py の mat を空にすると広告は静かに消えます。消えたことに
# 気づけないと、そのぶん売上が落ちます。だから毎回数えます。
import afflinks as _af
_empty=[i['n'] for g in _af.G.values() for i in g['items'] if not i.get('mat')]
if _empty: bad.append('広告リンクが空のまま: %s'%('・'.join(_empty)))
# リンクは gh/assets/aff.js の中にあります。ページ側は枠と読み込みだけ。
for p2 in sorted(glob.glob('gh/articles/*/index.html')):
    if p2.endswith('articles/index.html'): continue
    s2=txt(p2)
    if 'affslot' not in s2 and 'affmini-slot' not in s2:
        bad.append('%s に広告枠が1つもない'%p2)

# ── 広告が、古い見本のまま残っていないか ──
#
# トップと企業DBは手書きHTMLで、その中に広告JSの写しを持っていました。
# afflinks.py を直しても、この2ページだけビズリーチ・doda X のまま
# 公開されていました。同じ中身を2か所に持たない、が答えです。
# 本文で「ビザスク」「サーキュレーション」に触れるのは記事として正しい。
# 見るのは広告データの中の名前（"n":"…"）だけにする。
# 広告のJSとデータは gh/assets/aff.js の1本だけ。ページはそれを読むだけにする。
SAMPLE=re.compile(r'"n":"(ビズリーチ|フォースタートアップス|doda X|グロービス学び放題|'
                  r'ラクスルバンク|GMOオフィスサポート|サーキュレーション|ビザスク|HiPro Biz|officee|freee会計|flier[^"]*)"')
OKNAMES={i['n'] for g in _af.G.values() for i in g['items']}
AFFJS=txt('gh/assets/aff.js')
if not AFFJS: bad.append('gh/assets/aff.js がない')
else:
    m=SAMPLE.search(AFFJS)
    if m: bad.append('gh/assets/aff.js に古い見本「%s」が残っている'%m.group(1))
    for nm in set(re.findall(r'"n":"([^"]+)"',AFFJS)):
        if nm not in OKNAMES:
            bad.append('gh/assets/aff.js に afflinks.py にない名前「%s」がある'%nm)
    for i in _af.G['job']['items']:
        if i['mat'] not in AFFJS: bad.append('gh/assets/aff.js に %s のリンクがない'%i['n'])
for p2 in sorted(glob.glob('gh/**/*.html',recursive=True)):
    if p2.startswith('gh/_src/'): continue
    s2=txt(p2)
    if '"mat":' in s2:
        bad.append('%s に広告データが焼き込まれている（aff.js を読む形にする）'%p2)
    if 'affslot' in s2 and '/assets/aff.js' not in s2:
        bad.append('%s が広告のJS（/assets/aff.js）を読んでいない'%p2)
    if re.search(r'<button data-af=',s2): bad.append('%s に古いタブ式の広告が残っている'%p2)

# ── OGP画像（SNSに貼ったときの絵）が、実在するか ──
#
# 参照名がズレていて、57ページぜんぶが存在しないファイルを指していたことがあります。
# ページを見ても気づけません。SNSに貼ったときだけ絵が出ない、という壊れ方をします。
seen={}
for p in sorted(glob.glob('gh/**/*.html',recursive=True)):
    if p.startswith('gh/_src/'): continue
    s=txt(p)
    if '</head>' not in s: continue
    m=re.search(r'<meta property="og:image" content="(.*?)"',s)
    if not m: bad.append('%s に og:image がない'%p); continue
    url=m.group(1); f='gh'+url.replace('https://newfor.jp','')
    if not os.path.exists(f): bad.append('%s の og:image %s が存在しない'%(p,url))
    seen.setdefault(url,[]).append(p)
    t=re.search(r'<meta name="twitter:image" content="(.*?)"',s)
    if t and t.group(1)!=url: bad.append('%s の twitter:image が og:image と違う'%p)
for url,ps in seen.items():
    # NEWSの1件ずつは、企業ごとの1枚を共有します。1076枚を専用にすると
    # 75MBになり、GitHubへの反映ができなくなるためです。ここは意図した設計。
    ps2=[p for p in ps if not p.startswith('gh/news/')]
    if len(ps2)>3: bad.append('OGP画像 %s を %d ページで使い回している'%(url,len(ps2)))

# ── ピックアップの帯が全ページに入っているか ──
for p in sorted(glob.glob('gh/**/*.html',recursive=True)):
    if p.startswith('gh/_src/'): continue
    s=txt(p)
    # 帯そのものは assets/pickup.js が作ります。ページ側は読み込み2行だけ。
    if '</header>' in s and '/assets/pickup.js' not in s:
        bad.append('%s がピックアップのJSを読んでいない（pickup.py を流し直す）'%p)

# ── NEWS ページ ──
#
# ここで見ているのは3つです。
#   ・件数が年表と合っているか（1件に1ページ）
#   ・日付をでっちあげていないか（月しか分からない記録に日を出していないか）
#   ・行き先が生きているか（企業ページの先頭へ戻していないか）
import newsdata as _nd
_NEWS=_nd.build()
_dirs={os.path.dirname(p)[len('gh/news/'):] for p in glob.glob('gh/news/*/index.html')}
_dirs={d for d in _dirs if not re.fullmatch(r'\d{4}',d)}
_want={i['slug'] for i in _NEWS}
if _dirs!=_want:
    miss=_want-_dirs; extra=_dirs-_want
    if miss: bad.append('NEWSページが足りない %d件（例 %s）'%(len(miss),list(miss)[:3]))
    if extra: bad.append('もう無い記録のNEWSページが残っている %d件（例 %s）'%(len(extra),list(extra)[:3]))
for i in _NEWS:
    p='gh/news/%s/index.html'%i['slug']
    s=txt(p)
    if not s: continue
    d=i['date'].replace('-','.')
    # 見出しの下に出している日付だけを見る。ページの中の「この前後」の一覧には
    # 同じ月の別の記録（日まで分かっているもの）が並ぶので、ページ全体を
    # 探すと必ず引っかかります（実際に全件で誤検知しました）。
    m=re.search(r'<span class="ndate">([^<]*)<em>([^<]*)</em>',s)
    if not m:
        bad.append('%s に日付が出ていない'%p)
    else:
        if m.group(1)!=d:
            bad.append('%s の日付が %s ではなく %s になっている'%(p,d,m.group(1)))
        if i['prec']!='day' and m.group(2)=='発表日':
            bad.append('%s は月までしか分かっていないのに「発表日」と書いている'%p)
    if i['src'] and i['src'] not in s:
        bad.append('%s に出典リンクがない'%p)
# トップと企業ページが、NEWSページへ向いているか
_top=txt('gh/index.html')
if '/companies/denso/"' in _top and '"/news/' not in _top:
    bad.append('トップの新規事業NEWSが、まだ企業ページの先頭へ飛ばしている')
for p in sorted(glob.glob('gh/companies/*/index.html')):
    s=txt(p)
    if 'class="clist"' in s and '/news/' not in s:
        bad.append('%s の新規事業の一覧が、NEWSページへ向いていない'%p)

# ── 読者の投票（今日の1件） ──
if not txt('gh/assets/poll.js'): bad.append('gh/assets/poll.js がない（pollgen.py を流す）')
if not txt('gh/assets/vote.js'): bad.append('gh/assets/vote.js がない（mkvote.py を流す）')
if 'weekly-2026-08-05' in _top:
    bad.append('トップの投票が、古い1問（weekly-2026-08-05）のまま')

# ── 3. 生成元のないファイル ──
for p in sorted(glob.glob('gh/**/*',recursive=True)):
    if not os.path.isfile(p) or p.startswith('gh/_src/'): continue
    if p.endswith(('.json','.md','.sql','.webmanifest','.js')) or p=='gh/vercel.json': continue
    if owner(p) is None: hand.append(p)

print('データ: %d社 / %d件 / 記事%d本'%(NCO,NBIZ,NART))
print('\n手で管理しているファイル（生成元なし・数字は手で直す）')
for p in hand: print('   ',p)
if bad:
    print('\n【ズレ %d件】'%len(bad))
    for b in bad: print('   ',b)
    sys.exit(1)
print('\n生成物と生成元のズレ: なし')
