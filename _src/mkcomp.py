# -*- coding: utf-8 -*-
"""企業ページ（/companies/<slug>/）を、companies/ 以下のデータから生成する

記事の有無とは切り離してある。年表が10件以上ある企業だけを公開する。
"""
import io,re,sys,os,glob,importlib,json
sys.path.insert(0,'companies')
sys.path.insert(0,'articles')
import compgen
from compgen import ym,find_end

MIN=10   # これ未満の企業は、検索エンジンに載せない

# 記事のある企業は、記事のOGP画像を使う
OG={'docomo':'og-docomo','kddi':'og-kddi-newbusiness','sony':'og-sony-newbusiness',
 'fujifilm':'og-fujifilm-newbusiness','toyota':'og-toyota-newbusiness',
 'panasonic':'og-panasonic-newbusiness','mitsubishi':'og-mitsubishi-newbusiness',
 'jreast':'og-jreast-newbusiness','sevenandi':'og-sevenandi-newbusiness',
 'recruit':'og-recruit-newbusiness','ajinomoto':'og-ajinomoto-newbusiness',
 'softbank':'og-softbank-newbusiness'}


def wlen(t):
    """検索結果での見え方に近い幅。全角2・半角1で数える"""
    return sum(1 if ord(c)<0x3000 else 2 for c in t)

def ttl(name,n,lo,hi):
    """企業ページのタイトル。長い会社名でも60幅に収まるよう段階的に短くする"""
    for t in ['%sの新規事業%d件｜%d年からの全記録と出典 | NEWFOR'%(name,n,lo),
              '%sの新規事業%d件｜%d年からの記録 | NEWFOR'%(name,n,lo),
              '%sの新規事業%d件｜%d年から | NEWFOR'%(name,n,lo),
              '%sの新規事業%d件 | NEWFOR'%(name,n)]:
        if wlen(t)<=60: return t
    return '%sの新規事業一覧 | NEWFOR'%name

CO=[]
for f in sorted(glob.glob('companies/*.py')):
    n=os.path.basename(f)[:-3]
    if n.startswith('_'): continue
    CO.append(importlib.import_module(n).C)

ART={}
for f in sorted(glob.glob('articles/a0*.py')):
    A=importlib.import_module(os.path.basename(f)[:-3]).A
    ART[A.get('slug')]=A

made=[]
for C in sorted(CO,key=lambda c:-len(c['timeline'])):
    slug=C['slug']; name=C['name']; tl=C['timeline']
    biz=[(ev,ym(y),None if live else find_end(note,ym(y)),live,note) for y,ev,note,live in tl]
    biz.sort(key=lambda b:b[1])
    nl=sum(1 for b in biz if b[3])
    lo=int(min(b[1] for b in biz)); hi=int(max(b[1] for b in biz))
    A=ART.get(C.get('article'))
    c=dict(slug=slug,name=name,legal=C['legal'],ogslug=OG.get(slug,'og-docomo'),
      rep=('/articles/%s/'%A['slug']) if A else '',
      rept=A['h1'].replace('<br>','') if A else '',
      biz=biz,thin=len(biz)<MIN,srcs=C.get('sources',[]),ind=C['ind'],evsrc=C.get('evsrc') or {},
      # 検索結果で切れないよう、全角30字＝60幅までに収める。
      # 「企業名＋新規事業」で引かれるので、それを先頭に置く。
      title=ttl(name,len(biz),lo,hi),
      # AIに引用されやすいよう、1文目だけで「何が・何件・いつからいつまで」が
      # 完結するように書く。2文目以降で中身を足す。
      desc=('%sの新規事業%d件の一覧です。%d年から%d年までに始まった事業を、'
            '開始年・いまの状況・出典つきで1件ずつ年表にしました。'
            '継続中%d件、終了または他社へ譲渡%d件。%sなどを掲載しています。'
            %(name,len(biz),lo,hi,nl,len(biz)-nl,
              '「%s」'%'」「'.join(b[0] for b in sorted(biz,key=lambda b:-b[1])[:2]))),
      lead='公開情報から拾った%d件を、開始年の古い順に並べています。いま提供が続いているものは青、終了または他社へ譲渡したものは紫で示しています。'%len(biz),
      others=[(x['slug'],x['name']) for x in sorted(CO,key=lambda c:-len(c['timeline']))
              if x['slug']!=slug and len(x['timeline'])>=MIN][:11])
    os.makedirs('gh/companies/%s'%slug,exist_ok=True)
    io.open('gh/companies/%s/index.html'%slug,'w',encoding='utf-8').write(compgen.render(c))
    made.append(dict(slug=slug,name=name,ind=C['ind'],n=len(biz),live=nl,lo=lo,hi=hi,
                     art=A['slug'] if A else None,thin=len(biz)<MIN))
    print('  %-12s %-14s %2d件（継続%2d）%s%s'%(slug,name,len(biz),nl,
          ' 記事あり' if A else '',' ※10件未満' if len(biz)<MIN else ''))
print('\n%d社 / 合計%d件'%(len(made),sum(m['n'] for m in made)))
io.open('/tmp/comps.json','w',encoding='utf-8').write(json.dumps(made,ensure_ascii=False))
