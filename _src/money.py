# -*- coding: utf-8 -*-
"""年表の説明文から、新規事業に「払った」金額だけを抜き出す

売上高・流通総額・預金残高・純利益・目標額などは投資額ではないので外す。
金額のすぐ近くに「取得」「買収」「出資」「投じ」などの言葉があるものだけを拾う。
"""
import re,os,sys,glob,importlib,json
sys.path.insert(0,'companies')

NUM=r'(?:\d[\d,]*(?:\.\d+)?)'
PAT=re.compile(r'(?:約)?(%s)\s*兆\s*(?:(%s)\s*億)?円|(?:約)?(%s)\s*億円|(?:約)?(%s)\s*万円'%(NUM,NUM,NUM,NUM))
PAY=re.compile(r'取得|買収|買い取|買付|出資|投資|投じ|引き受け|引受|払っ|支払|拠出|増資|子会社化|完全子会社|TOB|公開買付')
NOT=re.compile(r'売上|収益|流通総額|取扱高|預り資産|預金|純利益|営業利益|経常利益|時価総額|市場規模|評価損|減損|目指|目標|見込|計画|想定|規模となる|売却益|特別利益|統合後|企業価値|資産規模|運用総額|残高|時価|市場|成長|規模の|超規模')

def f(x): return float(str(x).replace(',',''))

def clauses(t):
    out=[];cur=''
    for ch in t:
        cur+=ch
        if ch in '。、': out.append(cur); cur=''
    if cur: out.append(cur)
    return out

CO=[]
for p in sorted(glob.glob('companies/*.py')):
    n=os.path.basename(p)[:-3]
    if n.startswith('_'): continue
    CO.append(importlib.import_module(n).C)

rows=[]
for C in CO:
    ES=C.get('evsrc') or {}
    for d,ev,note,live in C['timeline']:
        best=None;bestc=''
        for c in clauses(note):
            if not PAT.search(c): continue
            if NOT.search(c): continue
            if not (PAY.search(c) or PAY.search(ev)): continue
            for m in PAT.finditer(c):
                if m.group(1): v=f(m.group(1))*1e12+(f(m.group(2))*1e8 if m.group(2) else 0)
                elif m.group(3): v=f(m.group(3))*1e8
                else: v=f(m.group(4))*1e4
                if best is None or v>best: best=v; bestc=c.strip('。、')
        if best and best>=1e8:
            u=ES.get('%s|%s'%(d,ev)) or ES.get(d)
            rows.append(dict(co=C['name'],slug=C['slug'],ind=C['ind'],date=d,ev=ev,
                             clause=bestc,yen=best,live=live,
                             url=u[0] if u else '',src=u[1] if u else ''))
rows.sort(key=lambda r:-r['yen'])

def jp(v):
    if v>=1e12:
        t=int(v//1e12); o=int(round((v-t*1e12)/1e8))
        return '{}兆{:,}億円'.format(t,o) if o else '{}兆円'.format(t)
    return '{:,}億円'.format(int(round(v/1e8)))
for r in rows: r['disp']=jp(r['yen'])

json.dump(rows,open('/tmp/money.json','w'),ensure_ascii=False)
tot=sum(len(c['timeline']) for c in CO)
print('払った金額を拾えた案件: %d件 / 全%d件 / %d社'%(len(rows),tot,len({r['co'] for r in rows})))
print()
for i,r in enumerate(rows[:35],1):
    print('%2d. %-12s %-32s %12s %s'%(i,r['co'],r['ev'][:30],r['disp'],r['date']))
