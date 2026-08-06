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
       (r'^gh/assets/','assets.py / png.js / og.js')]
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
