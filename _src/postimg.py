# -*- coding: utf-8 -*-
"""InstagramとTikTokに出す画像を、実データから作る

brand.py のテンプレは「型」だけでした。これは中身の入った実物を作ります。
数はすべて companies/ の年表から数えるので、画像と年表がズレません。

出力: posts/img/*.svg → postimg.js が PNG にします
"""
import io,os,sys,glob,importlib,re
sys.path.insert(0,'companies'); sys.path.insert(0,'articles')
import brand
from brand import BLUE,BLUE_D,ORANGE,INK,PAPER,WHITE,FONT,scaled_mark,wordmark,svg

OUT='posts/img'
os.makedirs(OUT,exist_ok=True)

def esc(t):
    return (t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'))

def wrap(t,n):
    """全角n文字で折り返す。

    数字や英字の途中では切らない（「2026年」が「20／26年」に割れました）。
    行頭に句読点や閉じ括弧も置かない。
    """
    if '\n' in t:                                # 改行を書いたら、そこで必ず切る
        out=[]
        for part in t.split('\n'): out+=wrap(part,n)
        return out
    toks=re.findall(r'[0-9A-Za-z.,%&\-]+|.',t)   # 数字と英字はひとかたまり
    out=[]; cur=''
    for tk in toks:
        if cur and len(cur)+len(tk)>n and tk not in '。、）」':
            out.append(cur); cur=''
        cur+=tk
    if cur: out.append(cur)
    return out

# ── データを読む ──
CO=[]
for f in sorted(glob.glob('companies/*.py')):
    n=os.path.basename(f)[:-3]
    if n.startswith('_'): continue
    c=importlib.import_module(n).C
    tl=c['timeline']
    ys=[int(str(y)[:4]) for y,_,_,_ in tl]
    CO.append(dict(slug=c['slug'],name=c['name'],n=len(tl),
                   live=sum(1 for t in tl if t[3]),lo=min(ys),hi=max(ys)))
CO.sort(key=lambda c:-c['n'])

ART=[]
for f in sorted(glob.glob('articles/a0*.py')):
    A=importlib.import_module(os.path.basename(f)[:-3]).A
    ART.append((A['slug'],A['h1'].replace('<br>','')))

TOT=sum(c['n'] for c in CO); LIVE=sum(c['live'] for c in CO)
LO=min(c['lo'] for c in CO); HI=max(c['hi'] for c in CO)


# ══ 正方形（Instagram 1080×1080） ══
def square(head,sub,stat,statlabel,foot='newfor.jp で見る'):
    b='<rect width="1080" height="1080" fill="%s"/>'%PAPER
    b+='<rect x="0" y="0" width="1080" height="16" fill="%s"/>'%BLUE
    b+=scaled_mark(72,86,76,BLUE)
    b+=wordmark(168,164,56,INK,ORANGE)
    y=330
    for ln in wrap(head,11):
        b+=('<text x="74" y="%d" font-family="%s" font-size="62" font-weight="900" '
            'fill="%s">%s</text>'%(y,FONT,INK,esc(ln))); y+=84
    b+='<rect x="74" y="%d" width="932" height="5" rx="2" fill="%s" fill-opacity=".2"/>'%(y+6,BLUE)
    for x,w,c in [(74,260,BLUE),(360,140,ORANGE),(530,240,BLUE),(800,206,ORANGE)]:
        b+='<rect x="%d" y="%d" width="%d" height="5" rx="2" fill="%s"/>'%(x,y+6,w,c)
    y+=90
    for ln in wrap(sub,26):
        b+=('<text x="74" y="%d" font-family="%s" font-size="31" font-weight="600" '
            'fill="#403C55">%s</text>'%(y,FONT,esc(ln))); y+=48
    # 大きな数字
    b+=('<text x="74" y="880" font-family="%s" font-size="132" font-weight="900" '
        'fill="%s">%s</text>'%(FONT,BLUE,esc(stat)))
    b+=('<text x="74" y="928" font-family="%s" font-size="28" font-weight="700" '
        'fill="#57536D" letter-spacing="1.2">%s</text>'%(FONT,esc(statlabel)))
    b+='<rect x="74" y="972" width="360" height="68" rx="34" fill="%s"/>'%BLUE
    b+=('<text x="254" y="1017" text-anchor="middle" font-family="%s" font-size="26" '
        'font-weight="800" fill="#fff">%s</text>'%(FONT,esc(foot)))
    b+=('<text x="1006" y="1017" text-anchor="end" font-family="%s" font-size="21" '
        'font-weight="700" fill="#57536D" letter-spacing="1.2">新規事業ヒストリーメディア</text>'%FONT)
    return svg(1080,1080,b)


# ══ 縦長（TikTok 1080×1920） ══
def vertical(head,sub,stat,statlabel):
    b=('<defs><linearGradient id="v" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>'%(BLUE,BLUE_D))
    b+='<rect width="1080" height="1920" fill="url(#v)"/>'
    b+=scaled_mark(80,150,88,WHITE)
    b+=wordmark(192,222,62,'#FFFFFF','#FFB08A')
    # TikTokは下400pxほどがキャプションとUIで隠れる。右端もアイコンが乗る。
    # だから中身は y=560〜1430、x=84〜860 に収める。
    y=700
    for ln in wrap(head,11):
        b+=('<text x="84" y="%d" font-family="%s" font-size="78" font-weight="900" '
            'fill="#fff">%s</text>'%(y,FONT,esc(ln))); y+=100
    b+='<rect x="84" y="%d" width="912" height="6" rx="3" fill="#fff" fill-opacity=".25"/>'%(y+10)
    for x,w in [(84,240),(360,180),(580,280),(900,96)]:
        b+='<rect x="%d" y="%d" width="%d" height="6" rx="3" fill="#fff" fill-opacity=".9"/>'%(x,y+10,w)
    y+=110
    for ln in wrap(sub,22):
        b+=('<text x="84" y="%d" font-family="%s" font-size="38" font-weight="600" '
            'fill="#fff" fill-opacity=".88">%s</text>'%(y,FONT,esc(ln))); y+=58
    b+=('<text x="84" y="%d" font-family="%s" font-size="190" font-weight="900" '
        'fill="#FFB08A">%s</text>'%(y+190,FONT,esc(stat)))
    b+=('<text x="84" y="%d" font-family="%s" font-size="36" font-weight="700" '
        'fill="#fff" fill-opacity=".8" letter-spacing="1.4">%s</text>'%(y+250,FONT,esc(statlabel)))
    # 行数によって下がるので、CTAは数字の下に必ず余白を取って置く
    cy=max(1300,y+330)
    b+='<rect x="84" y="%d" width="640" height="86" rx="43" fill="#fff" fill-opacity=".16"/>'%cy
    b+=('<text x="404" y="%d" text-anchor="middle" font-family="%s" font-size="34" '
        'font-weight="800" fill="#fff" letter-spacing="1.4">'
        'プロフィールのリンクから</text>'%(cy+55,FONT))
    return svg(1080,1920,b)


def put(name,s):
    io.open('%s/%s.svg'%(OUT,name),'w',encoding='utf-8').write(s)

JOBS=[]   # (svg名, 幅, 高さ)

# ── 1. 導入用（全体の数） ──
# 大きく出す数は「挑戦の数」。続いた数を驚きとして見せない（_src/KOTOBA.md）。
put('ig-00-intro', square('大企業の新規事業\n45年ぶんの挑戦',
    '%d社%d件を1件ずつ並べました。%d年から%d年まで、全件出典つき。'%(len(CO),TOT,LO,HI),
    '%d'%TOT,'件の挑戦を記録しています'))
JOBS.append(('ig-00-intro',1080,1080))
put('tt-00-intro', vertical('大企業の新規事業\n45年ぶんの挑戦',
    '%d社%d件を1件ずつ並べました'%(len(CO),TOT),'%d'%TOT,'件を記録'))
JOBS.append(('tt-00-intro',1080,1920))

# ── 2. 企業ごと（Instagram用・上位12社） ──
for i,c in enumerate(CO[:12]):
    put('ig-co%02d-%s'%(i+1,c['slug']), square(
        '%sの新規事業'%c['name'],
        '%d年から%d年まで。継続%d件。開始年と出典つきで1件ずつ年表にしました。'
        %(c['lo'],c['hi'],c['live']),
        '%d'%c['n'],'件を記録しています'))
    JOBS.append(('ig-co%02d-%s'%(i+1,c['slug']),1080,1080))

# ── 3. 企業ごと（TikTok用・上位8社） ──
for i,c in enumerate(CO[:8]):
    put('tt-co%02d-%s'%(i+1,c['slug']), vertical(
        '%sの新規事業'%c['name'],
        '%d年から%d年まで。継続%d件'%(c['lo'],c['hi'],c['live']),
        '%d'%c['n'],'件'))
    JOBS.append(('tt-co%02d-%s'%(i+1,c['slug']),1080,1920))

io.open('%s/jobs.json'%OUT,'w',encoding='utf-8').write(
    '[%s]'%','.join('["%s",%d,%d]'%j for j in JOBS))
print('SVGを%d本 書き出しました → %s/'%(len(JOBS),OUT))
