# -*- coding: utf-8 -*-
"""企業データベース（gh/companies/index.html）の中の数を作り直す

このページはレイアウトを手で組んでいます。けれど中の数字は companies/*.py から
計算できるものばかりで、手で直していると必ずどこかが古くなります。
そこで、数字の入っている場所だけをここで書き換えます。レイアウトは触りません。

書き換えるのは次の5つです。

  var C      … 企業の一覧（名前・業種・件数・継続数・リンク）
  var BARS   … 企業ごとの記録の増え方（最大12本の棒）
  var RANGE  … 記録のある年の幅
  var LATEST … 最後に記録した年月
  ページ上部の「N社」「N件」（title, description, OGP, 構造化データ, 見出し下）
"""
import io,os,re,sys,glob,json,importlib
sys.path.insert(0,'companies')
P='gh/companies/index.html'
NB=12   # 棒の本数の上限

CO=[importlib.import_module(os.path.basename(f)[:-3]).C
    for f in sorted(glob.glob('companies/*.py')) if not os.path.basename(f).startswith('_')]
CO.sort(key=lambda c:(-len(c['timeline']),c['slug']))
NCO=len(CO); NBIZ=sum(len(c['timeline']) for c in CO)

def yr(d): return int(str(d)[:4])
def mon(d):
    m=re.match(r'(\d{4})\.(\d{1,2})',str(d))
    return '%d年%d月'%(int(m.group(1)),int(m.group(2))) if m else '%d年'%yr(d)

C=[];BARS={};RANGE={};LATEST={}
for c in CO:
    tl=sorted(c['timeline'],key=lambda t:t[0])
    ys=[yr(t[0]) for t in tl]; lo,hi=min(ys),max(ys)
    C.append([c['name'],c['slug'],'',c['ind'],len(tl),sum(1 for t in tl if t[3]),'/companies/%s/'%c['slug']])
    # 記録のある年を最大12個の区切りに分ける。棒の合計は必ず件数と一致する
    n=min(NB,hi-lo+1); w=(hi-lo+1)/float(n)
    b=[0]*n
    for y in ys: b[min(n-1,int((y-lo)/w))]+=1
    BARS[c['name']]=b; RANGE[c['name']]=[lo,hi]; LATEST[c['name']]=mon(tl[-1][0])
assert sum(sum(v) for v in BARS.values())==NBIZ,'棒の合計が件数と合っていません'

s=io.open(P,encoding='utf-8').read()
def swap(var,val):
    """var X=…; を丸ごと入れ替える。正規表現だと改行や記号で外すので、位置で切る"""
    global s
    i=s.index('var %s='%var); j=s.index(';\n',i)
    s=s[:i]+'var %s=%s;'%(var,json.dumps(val,ensure_ascii=False))+s[j+1:]
for v,d in (('C',C),('BARS',BARS),('RANGE',RANGE),('LATEST',LATEST)): swap(v,d)

# 上部の数字。「10社近く」のような概数は書き換えない
head=s[:s.index('</head>')+7]
body=s[len(head):]
def fix(t):
    """数を書き換える。

    「\\d+社」を片端から置き換えると、著者紹介の「1社を上場企業へ売却」まで
    書き換えてしまいます（実際にやってしまいました）。だから、記録の数を
    指している言い回しだけを名指しで置き換えます。
    """
    for pat,rep in [
      (r'(\d+)社(\d+)件',        '%d社%d件'%(NCO,NBIZ)),
      (r'(\d+)社・(\d+)件',      '%d社・%d件'%(NCO,NBIZ)),
      (r'(\d+)社・(\d+)事業',    '%d社・%d事業'%(NCO,NBIZ)),
      (r'大企業(\d+)社',         '大企業%d社'%NCO),
      (r'(\d+)社を掲載中',       '%d社を掲載中'%NCO),
      (r'新規事業(\d+)件',       '新規事業%d件'%NBIZ),
      (r'新規事業事業(\d+)件',   '新規事業%d件'%NBIZ)]:
        t=re.sub(pat,rep,t)
    return t
lo=min(RANGE[k][0] for k in RANGE); hi=max(RANGE[k][1] for k in RANGE)
head=re.sub(r'"temporalCoverage":"[^"]*"','"temporalCoverage":"%d-01/%d-12"'%(lo,hi),fix(head))
i=body.index('<p class="hsub">'); j=body.index('</p>',i)
body=body[:i]+fix(body[i:j])+body[j:]
io.open(P,'w',encoding='utf-8').write(head+body)
print('-> %s  %d社 / %d件 / %d–%d年'%(P,NCO,NBIZ,lo,hi))
