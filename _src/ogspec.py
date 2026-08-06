# -*- coding: utf-8 -*-
"""全ページぶんのOGP画像の中身を、実データから組み立てる

これまで og.js の中に、12社226事業の時代の文言が手で書いてありました。
そのため、数が古いまま。しかも参照名がズレていて、実在しないファイルを
指しているページが57枚ありました（SNSに貼っても画像が出ない状態）。

ここで作る名前の決まりは1つだけです。

    トップ            og-top.png
    企業DB            og-companies.png
    企業ページ        og-c-<slug>.png
    記事              og-a-<slug>.png
    固定ページ        og-p-<name>.png

出力: /tmp/ogspec.json → og.js がこれを読んで画像にします。
"""
import io,os,sys,glob,json,importlib,re
sys.path.insert(0,'companies'); sys.path.insert(0,'articles')

CO=[]
for f in sorted(glob.glob('companies/*.py')):
    n=os.path.basename(f)[:-3]
    if n.startswith('_'): continue
    c=importlib.import_module(n).C
    tl=c['timeline']; ys=[int(str(y)[:4]) for y,_,_,_ in tl]
    CO.append(dict(slug=c['slug'],name=c['name'],n=len(tl),
                   live=sum(1 for t in tl if t[3]),lo=min(ys),hi=max(ys)))
CO.sort(key=lambda c:-c['n'])

ART=[]
for f in sorted(glob.glob('articles/a0*.py')):
    ART.append(importlib.import_module(os.path.basename(f)[:-3]).A)

TOT=sum(c['n'] for c in CO); LIVE=sum(c['live'] for c in CO); NCO=len(CO)
LO=min(c['lo'] for c in CO); HI=max(c['hi'] for c in CO)


def two(t,n=15):
    """見出しを2〜3行に折る。切れ目は句読点や助詞のうしろを優先する"""
    t=t.replace('<br>','')
    if len(t)<=n: return t
    lines=[]; cur=''
    for ch in t:
        cur+=ch
        if len(cur)>=n:
            lines.append(cur); cur=''
    if cur: lines.append(cur)
    return '<br>'.join(lines[:3])


def first_sentence(t,n=46):
    s=re.split(r'(?<=。)',t)[0]
    return s if len(s)<=n else s[:n-1]+'…'


P=[]

P.append(dict(f='og-top.png', eyebrow='新規事業ヒストリーメディア',
  title='大企業の新規事業を<br>%d社%d件、年表にした。'%(NCO,TOT),
  sub='%d年から%d年まで。開始年・いまの状況・出典つきで1件ずつ。'%(LO,HI)))

P.append(dict(f='og-companies.png', eyebrow='大企業の新規事業データベース',
  title='%d社%d件を<br>公開情報から記録した。'%(NCO,TOT),
  sub='いまも続くのが%d件。企業ごとに年表で見られます。'%LIVE))

P.append(dict(f='og-articles.png', eyebrow='新規事業ヒストリー 記事一覧',
  title='%d本の記事で、<br>大企業の決断を読み解く。'%len(ART),
  sub='年表からは見えない「なぜ」を、公開情報だけで追いました。'))

for c in CO:
    P.append(dict(f='og-c-%s.png'%c['slug'], eyebrow='%s ／ 企業データ'%c['name'],
      title='%sの新規事業、<br>%d件の記録。'%(c['name'],c['n']),
      sub='%d年から%d年まで。継続%d件。全件、出典つき。'%(c['lo'],c['hi'],c['live'])))

for a in ART:
    eb=('特集 #%s'%a['no']) if a.get('genre') else ('企業の決断 #%s'%a['no'])
    P.append(dict(f='og-a-%s.png'%a['slug'], eyebrow=eb,
      title=a['h1'] if '<br>' in a['h1'] else two(a['h1']),
      sub=first_sentence(a.get('dek') or '')))

for name,eye,ttl,sub in [
  ('about','NEWFORについて','公開情報だけで、<br>新規事業を記録する。',
   'どこから引いたかを、1件ずつ示しています。'),
  ('ads','広告・データ利用について','記録の使い方と、<br>広告の扱い。',
   '数字の引用と転載について、まとめています。'),
  ('privacy','プライバシーポリシー','個人情報の<br>取り扱いについて。',
   'アクセス解析と、お問い合わせでいただく情報。'),
  ('404','ページが見つかりません','お探しのページは<br>見つかりませんでした。',
   '企業DBから、%d社の年表をたどれます。'%NCO)]:
    P.append(dict(f='og-p-%s.png'%name,eyebrow=eye,title=ttl,sub=sub))

io.open('/tmp/ogspec.json','w',encoding='utf-8').write(
    json.dumps(P,ensure_ascii=False,indent=1))
print('OGPの中身を %d ページぶん組み立てました'%len(P))
