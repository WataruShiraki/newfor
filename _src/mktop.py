# -*- coding: utf-8 -*-
"""トップページ（gh/index.html）の中の数を作り直す

このページもレイアウトは手で組んでいます。けれど中の数字と一覧は
companies/*.py と articles/a0*.py から計算できるので、ここで書き換えます。

書き換えるのは次の6つです。

  ページ上部の「N社」「N件」（title, description, OGP, 構造化データ）
  「最新の記録」の5件
  数字4つ（記録した企業／記録した新規事業／公開している記事／参照した一次情報）
  var NEW    … 新規事業NEWS の24件
  var MONTH  … 2015年以降の発表数ランキング
  var ALL    … 記録した新規事業の総数ランキング
  新規事業ヒストリーのカード3枚の「N件の記録／N年分」

レイアウト、見出し、文章は触りません。
"""
import io,os,re,sys,glob,json,importlib
sys.path.insert(0,'companies'); sys.path.insert(0,'articles')
P='gh/index.html'
NNEW=24   # 新規事業NEWS に出す件数

CO=[importlib.import_module(os.path.basename(f)[:-3]).C
    for f in sorted(glob.glob('companies/*.py')) if not os.path.basename(f).startswith('_')]
ART=[importlib.import_module(os.path.basename(f)[:-3]).A for f in sorted(glob.glob('articles/a0*.py'))]
NCO=len(CO); NBIZ=sum(len(c['timeline']) for c in CO); NART=len(ART)
BYNAME={c['name']:c for c in CO}

def yr(d): return int(str(d)[:4])
def esrc(ES,d,ev):
    if not ES: return None
    return ES.get('%s|%s'%(d,ev)) or ES.get(d) or ES.get(str(d)[:4])

# 出典（一次情報）の数。同じURLを2回数えないよう、URLで重複を取り除く
_u=set()
for c in CO:
    for v in (c.get('evsrc') or {}).values(): _u.add(v[0])
    for t,u in (c.get('sources') or []): _u.add(u)
NSRC=len(_u)

# ── 全社の出来事を新しい順に ──
#
# 日付と行き先は newsdata.py が決めています。ここで別に計算すると、
# トップとNEWSページで日付が食い違います（同じ中身を2か所に持たない）。
#
#   日付   … 発表日が分かっていれば 2026.08.05、分からなければ 2026.08
#   行き先 … その1件のNEWSページ。企業ページの先頭ではありません
import newsdata
EV=[(i['date'].replace('-','.'),i['co'],i['title'],i['note'],i['ind'],
     1 if i['live'] else 0,newsdata.path(i),i['src'],i['srclabel']) for i in newsdata.build()]
def cut(t,n):
    """途中で切れて意味が壊れないよう、句点か読点で切る"""
    if len(t)<=n: return t
    h=t[:n]
    for p in ('。','、'):
        if p in h: return h[:h.rindex(p)]
    return h
NEW=[[d,co,ev,cut(note,34),ind,lv,url,su,sn] for d,co,ev,note,ind,lv,url,su,sn in EV[:NNEW]]

# ── ランキング ──
def rank(pred,k=15):
    R=[]
    for c in CO:
        n=sum(1 for t in c['timeline'] if pred(t))
        if n: R.append([c['name'],c['ind'],n])
    R.sort(key=lambda r:(-r[2],r[0])); return R[:k]
MONTH={"recent":{"note":"2015年以降に発表された新規事業の件数。記録を公開している%d社が対象です。"%NCO,
  "unit":"件","rows":rank(lambda t:yr(t[0])>=2015)}}
ALLY=min(yr(t[0]) for c in CO for t in c['timeline'])
OLD=[c['name'] for c in CO if min(yr(t[0]) for t in c['timeline'])==ALLY][0]
ALL={"challenge":{"note":"記録した新規事業の総件数。最も古いものは%d年の%sです。"%(ALLY,OLD),
  "unit":"件","rows":rank(lambda t:True)}}

s=io.open(P,encoding='utf-8').read()

# ── 1. 上部の数 ──
def fix(t):
    for pat,rep in [(r'(\d+)社(\d+)件','%d社%d件'%(NCO,NBIZ)),
                    (r'(\d+)社・(\d+)件','%d社・%d件'%(NCO,NBIZ)),
                    (r'(\d+)社・(\d+)事業','%d社・%d事業'%(NCO,NBIZ)),
                    (r'大企業(\d+)社','大企業%d社'%NCO),
                    (r'新規事業(\d+)件','新規事業%d件'%NBIZ)]:
        t=re.sub(pat,rep,t)
    return t
h=s.index('</head>')+7
s=fix(s[:h])+s[h:]

# ── 2. 最新の記録（5件） ──
rows=''.join('<a class="hrk nw" href="%s"><span class="nd mono">%s</span>'
  '<span class="t">%s<em>%s</em></span></a>'%(e[6],e[0],cut(e[2],22),e[1]) for e in EV[:5])
i=s.index('<a class="hrk nw"'); j=s.index('</div>',i)
s=s[:i]+rows+'\n      '+s[j:]

# ── 3. 数字4つ ──
def stat(key,val):
    global s
    i=s.index('<span class="ex-k">%s</span>'%key)
    j=s.index('<span class="ex-n">',i); k=s.index('<em>',j)
    s=s[:j]+'<span class="ex-n">%d'%val+s[k:]
for k,v in [('記録した企業',NCO),('記録した新規事業',NBIZ),
            ('公開している記事',NART),('参照した一次情報',NSRC)]: stat(k,v)
s=re.sub(r'(<span class="ex-s">)\d+年からの発表を',r'\g<1>%d年からの発表を'%ALLY,s)

# ── 4. var NEW / MONTH / ALL ──
def swap(var,val,tail=';'):
    global s
    i=s.index('var %s='%var); j=s.index(tail,s.index('=',i))
    s=s[:i]+'var %s=%s'%(var,json.dumps(val,ensure_ascii=False))+s[j:]
swap('NEW',NEW,tail=', nIx=')
swap('MONTH',MONTH); swap('ALL',ALL)

# ── 5. 新規事業ヒストリーのカード3枚 ──
def card_fix(m):
    co=m.group(1)
    c=BYNAME.get(co)
    if not c: return m.group(0)
    ys=[yr(t[0]) for t in c['timeline']]
    return (m.group(0).replace(m.group(2),'%d'%len(c['timeline']))
                      .replace(m.group(3),'%d'%(max(ys)-min(ys)+1)))
s=re.sub(r'<span class="dc-co">([^<]+)</span>.*?<b>(\d+)</b>件の記録.*?<b>(\d+)</b>年分',
         card_fix,s,flags=re.S)

io.open(P,'w',encoding='utf-8').write(s)
print('-> %s  %d社 / %d件 / 記事%d本 / 出典%d件'%(P,NCO,NBIZ,NART,NSRC))
