# -*- coding: utf-8 -*-
"""/tmp/src/<slug>.json の出典を companies/<slug>.py の evsrc に入れる

キーは "日付|事業名"。timeline にない鍵は入れません（取り違えを防ぐため）。
"""
import io,os,re,sys,json,glob,importlib
sys.path.insert(0,'companies')
tot=(0,0)
for f in sorted(glob.glob('/tmp/src/*.json')):
    slug=os.path.basename(f)[:-5]
    p='companies/%s.py'%slug
    if not os.path.exists(p): print('!! %s に対応するファイルがない'%slug); continue
    C=importlib.import_module(slug).C
    keys={'%s|%s'%(d,ev) for d,ev,_,_ in C['timeline']}
    j=json.load(io.open(f,encoding='utf-8'))
    ok={k:v for k,v in j.items() if k in keys and isinstance(v,list) and str(v[0]).startswith('http')}
    ng=[k for k in j if k not in keys]
    ES=dict(C.get('evsrc') or {}); ES.update(ok)
    q=lambda s:"'"+str(s).replace('\\','\\\\').replace("'","\\'")+"'"
    blk='evsrc={\n'+''.join(' %s: [%s, %s],\n'%(q(k),q(v[0]),q(v[1])) for k,v in sorted(ES.items()))+'},\n'
    s=io.open(p,encoding='utf-8').read()
    if 'evsrc=' in s:
        # evsrc={ … } の閉じ括弧を、括弧の数を数えて探す（1行でも複数行でも効く）
        i=s.index('evsrc='); b=s.index('{',i); d=0
        for jx in range(b,len(s)):
            if s[jx]=='{': d+=1
            elif s[jx]=='}':
                d-=1
                if d==0: break
        while jx<len(s) and s[jx] in '},\n': jx+=1
        s=s[:i]+blk+s[jx:]
    else:
        i=s.index('timeline=['); s=s[:i]+blk+s[i:]
    io.open(p,'w',encoding='utf-8').write(s)
    print('%-14s %2d/%2d件に出典%s'%(slug,len(ES),len(C['timeline']),
          ('  ※キー不一致%d'%len(ng)) if ng else ''))
    for k in ng[:3]: print('        不一致:',k)
