# -*- coding: utf-8 -*-
"""トップページの「今日の1問」に出す問題を作る

問題は companies/*.py の年表と、money.py が抜き出した金額から作ります。
数字を勝手に作ることはしません。すべて、記録済みの1件が出どころです。

出す問題は4種類あります。

  払った額   … 「この買収にいくら払ったでしょう？」
  始まった年 … 「この事業が始まったのは何年でしょう？」
  記録の件数 … 「この会社の新規事業を、NEWFORは何件記録しているでしょう？」
  つづいた年 … 「この事業は何年つづいたでしょう？」

はずれの選択肢は、正解の桁をずらして作ります。10倍・10分の1のように
ひと桁ちがう数を並べると、「そんなに大きいのか」という驚きが出ます。

出来上がりは /tmp/quiz.json です。mktop.py がトップページへ埋め込みます。
"""
import io,os,re,sys,glob,json,importlib
sys.path.insert(0,'companies'); sys.path.insert(0,'articles')
import newsdata
from compgen import ym,find_end

CO=[]
for p in sorted(glob.glob('companies/*.py')):
    n=os.path.basename(p)[:-3]
    if n.startswith('_'): continue
    CO.append(importlib.import_module(n).C)

# ── その1件のページの住所 ──
# 住所の作り方は newsdata.py だけが知っています。ここでは借りるだけです。
NEWS={}
for i in newsdata.build():
    NEWS[(i['coslug'],i['ym'],i['title'])]=newsdata.path(i)
    if len(i['ym'])==4: NEWS[(i['coslug'],i['ym']+'.01',i['title'])]=newsdata.path(i)

# 年表の説明文。金額の問題で、一文だけでは短すぎるときに使います
NOTE={}
for C in CO:
    for d,ev,note,live in C['timeline']: NOTE[(C['slug'],d,ev)]=note

def link(slug,d,ev):
    return NEWS.get((slug,d,ev)) or NEWS.get((slug,str(d)[:4],ev)) or ''

def jp(v):
    """金額を、読める形の日本語にする"""
    if v>=1e12:
        t=int(v//1e12); o=int(round((v-t*1e12)/1e8))
        return '{}兆{:,}億円'.format(t,o) if o else '{}兆円'.format(t)
    if v>=1e8: return '{:,}億円'.format(int(round(v/1e8)))
    return '{:,}万円'.format(int(round(v/1e4)))

def key(s):
    """同じ問題がいつも同じ並びになるよう、文字列から数を作る"""
    h=0
    for ch in s: h=(h*131+ord(ch))%1000003
    return h

def mk(q,vals,ai,why,url,co,kind):
    """選択肢を、いつも同じ順で混ぜてから問題にする"""
    ans=vals[ai]
    order=sorted(range(len(vals)),key=lambda i:key(q+str(i)))
    ch=[vals[i] for i in order]
    return dict(q=q,ch=ch,a=ch.index(ans),why=why,url=url,co=co,k=kind)

Q=[]

# 答えが問題文にそのまま書いてあると、クイズになりません。
# 「約84億円の資金調達を実施」のように、事業名に数字が入っているものは外します。
LEAK_YEN=re.compile(r'\d[\d,]*(?:\.\d+)?\s*(?:兆|億|万)円')
LEAK_YEAR=re.compile(r'(?:19|20)\d\d\s*年')

# ── 1. 払った額 ──
if not os.path.exists('/tmp/money.json'):
    os.system('python3 money.py >/dev/null 2>&1')
MONEY=json.load(open('/tmp/money.json')) if os.path.exists('/tmp/money.json') else []
for r in MONEY:
    v=r['yen']
    if v<1e8: continue
    vals=[jp(v/100),jp(v/10),jp(v),jp(v*10)]
    if len(set(vals))<4: continue
    if LEAK_YEN.search(r['ev']): continue
    u=r.get('url2') or link(r['slug'],r['date'],r['ev'])
    # 説明文は年表の一文をそのまま使います。文の途中で切れていると
    # 「約1,000億円で。」のように尻切れになるので、末尾の助詞を落とします
    w=re.sub(r'[でをにはがともへや]$','',r['clause'].strip())
    # 「約3.3兆円。」だけでは、答えを言い直しただけで何も分かりません。
    # 短いときは、年表の説明文の頭から出します
    if len(w)<14:
        full=NOTE.get((r['slug'],r['date'],r['ev']),'')
        if len(full)>len(w): w=full[:78]+('…' if len(full)>78 else '')
    Q.append(mk('%sが「%s」に払った額は？'%(r['co'],r['ev']),vals,2,
                w+'。',u,r['co'],'money'))

# ── 2. 始まった年 ──
#
# 年の問題は数を絞ります。1,000件ぜんぶを問題にすると、
# 「思ったより古い」という驚きが薄まって、ただの暗記になってしまうためです。
# 会社ごとに、いちばん古い2件だけを選びます。
for C in CO:
    tl=sorted(C['timeline'],key=lambda t:str(t[0]))[:2]
    for d,ev,note,live in tl:
        if LEAK_YEAR.search(ev): continue
        y=int(str(d)[:4])
        vals=[str(y-9)+'年',str(y-4)+'年',str(y)+'年',str(y+4)+'年']
        if y+4>2026: vals=[str(y-12)+'年',str(y-8)+'年',str(y)+'年',str(y-4)+'年']
        if len(set(vals))<4: continue
        Q.append(mk('%sが「%s」を始めたのは何年？'%(C['name'],ev),vals,2,
                    note[:70]+('…' if len(note)>70 else ''),
                    link(C['slug'],d,ev),C['name'],'year'))

# ── 3. 記録の件数 ──
for C in CO:
    n=len(C['timeline'])
    vals=sorted({max(2,n//4),max(3,n//2),n,n*2})
    if len(vals)<4: continue
    vals=[str(x)+'件' for x in vals]
    ai=vals.index(str(n)+'件')
    lo=min(int(str(t[0])[:4]) for t in C['timeline'])
    Q.append(mk('NEWFORが記録している%sの新規事業は何件？'%C['name'],vals,ai,
                '%d年から%d件を、公開情報から1件ずつ確認して並べています。'%(lo,n),
                '/companies/%s/'%C['slug'],C['name'],'count'))

# ── 4. つづいた年 ──
for C in CO:
    for d,ev,note,live in C['timeline']:
        if live: continue
        s=ym(d); e=find_end(note,s)
        if not e: continue
        n=int(round(e-s))
        if n<2: continue
        if LEAK_YEAR.search(ev): continue
        vals=sorted({max(1,n//4),max(2,n//2),n,n*2})
        if len(vals)<4: continue
        vals=[str(x)+'年' for x in vals]
        ai=vals.index(str(n)+'年')
        Q.append(mk('%sの「%s」は何年つづいた？'%(C['name'],ev),vals,ai,
                    '%d年に始まり、%d年に役目を終えて次へ渡しました。'%(int(s),int(e)),
                    link(C['slug'],d,ev),C['name'],'span'))

# 行き先のない問題は出しません。答えを見たら、その1件を読めることが大事です
Q=[q for q in Q if q['url']]
Q.sort(key=lambda q:key(q['q']))

json.dump(Q,open('/tmp/quiz.json','w'),ensure_ascii=False)
c={}
for q in Q: c[q['k']]=c.get(q['k'],0)+1
print('-> /tmp/quiz.json  %d問（払った額%d／始まった年%d／件数%d／つづいた年%d）'
      %(len(Q),c.get('money',0),c.get('year',0),c.get('count',0),c.get('span',0)))
