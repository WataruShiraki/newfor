# -*- coding: utf-8 -*-
"""トップページ（gh/index.html）の中の数を作り直す

このページもレイアウトは手で組んでいます。けれど中の数字と一覧は
companies/*.py と articles/a0*.py から計算できるので、ここで書き換えます。

書き換えるのは次の6つです。

  ページ上部の「N社」「N件」（title, description, OGP, 構造化データ）
  「今日の1問」（var QUIZ）
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

# ── 2. 今日の1問 ──
#
# ここは以前「最新の記録」の5件でした。同じ中身が下の「新規事業NEWS」にも
# 並んでいたので、上は1問のクイズに入れ替えています。
# 問題そのものは quiz.py が作ります。ここでは埋め込むだけです。
QUIZ=json.load(io.open('/tmp/quiz.json',encoding='utf-8'))

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
swap('MONTH',MONTH); swap('ALL',ALL); swap('QUIZ',QUIZ)

# ── 5. 新規事業ヒストリーのカード3枚 ──
#
# 3枚とも、いちばん新しい「新規事業ヒストリー」の記事から毎回作り直します。
# 以前はカードのHTMLが gh/index.html に手で書いてあり、記事を足しても
# #012 のまま止まっていました。ここで作るのは <div class="dgrid"> の中身だけで、
# 見出しやレイアウトは触りません。
#
#   並び順 … pub（公開日）の新しい順。同じ日なら no の大きい順
#   対象  … genre を持たない記事（＝新規事業ヒストリー）だけ
#   数    … 「N件の記録」「N年分」は companies/<slug>.py の年表から数えます
#   帯    … 記事の chart（開始年・終了年つき）から8本を等間隔に選びます。
#           chart のない記事は、会社の年表から作ります。

def _cut(t,n=62):
    """カードの説明文。句読点のうしろで切って「…」をつける"""
    if len(t)<=n: return t
    h=t[:n]; b=max(h.rfind('、'),h.rfind('。'))
    return (h[:b+1] if b>0 else h)+'…'

def _pick(seq,k=8):
    """並びの端から端まで、k本を等間隔に選ぶ"""
    n=len(seq)
    if n<=k: return list(seq)
    return [seq[round(i*(n-1)/(k-1))] for i in range(k)]

def _ym(d):
    """'2013.07' → 2013.5 のような、月まで見た数にする"""
    a,_,b=str(d).partition('.')
    return int(a)+((int(b)-1)/12 if b else 0)

def _bars(A,c):
    rows=[]
    ch=A.get('chart'); sp=A.get('span')
    if ch and sp:
        lo,hi=float(sp[0]),float(sp[1])
        for _n,st,en,live in _pick(ch):
            left=(float(st)-lo)/(hi-lo)*100
            end=float(en) if en else hi
            rows.append((left,max(2.5,(end-float(st))/(hi-lo)*100),live))
    else:
        tl=c['timeline']; ys=[_ym(t[0]) for t in tl]
        lo,hi=min(ys),max(ys)
        for t in _pick(tl):
            left=(_ym(t[0])-lo)/(hi-lo)*100
            rows.append((left,max(2.5,100-left) if t[3] else 2.5,t[3]))
    return ''.join('<span class="mr"><i class="%s" style="left:%.1f%%;width:%.1f%%"></i></span>'
                   %('lv' if lv else 'dn',min(max(l,0.0),100.0),w) for l,w,lv in rows)

HIST=[a for a in ART if not a.get('genre')]
HIST.sort(key=lambda a:(a.get('pub',''),a.get('no','')),reverse=True)

def _card(A,big):
    c=BYNAME.get(A['company'])
    ind=A.get('ind') or (c['ind'] if c else '')
    if c:
        ys=[yr(t[0]) for t in c['timeline']]
        nrec,nyr=len(c['timeline']),max(ys)-min(ys)+1
    else:
        nrec,nyr=len(A.get('timeline') or []),0
    return ('<a class="dc%s" href="/articles/%s/">'
      '<span class="dc-top"><span class="dc-no">新規事業ヒストリー<b>#%s</b></span>'
      '<span class="dc-ind">%s</span></span>'
      '<span class="dc-co">%s</span><h3>%s</h3><p>%s</p>'
      '<span class="dc-ch">%s</span>'
      '<span class="dc-ft"><b>%d</b>件の記録<span class="sep">/</span>'
      '<b>%d</b>年分<span class="sep">/</span>%s分で読める</span></a>')%(
      ' big' if big else '',A['slug'],A['no'],ind,A['company'],
      A['h1'].replace('<br>',''),_cut(A['dek']),_bars(A,c) if c else '',
      nrec,nyr,A['read'])

_i=s.index('<div class="dgrid">',s.index('id="featured"'))
_j=s.index('</div>',s.index('</a></div>',_i))
s=s[:_i]+'<div class="dgrid">'+''.join(_card(a,k==0) for k,a in enumerate(HIST[:3]))+s[_j:]


# ── 6. トップの「記事一覧」（var ARTS）──
#
# ここも index.html に手で書いてあり、15本のまま止まっていました。
# 記事を足しても増えず、しかも #001 から古い順に並ぶので、
# 「上にあるものが古い」という見え方になっていました。毎回作り直します。
#
#   並び順 … pub（公開日）の新しい順。同じ日なら no の大きい順
#   左の列 … 通し番号ではなく公開日（年／月日の2行）。番号は順番と紛らわしいためです
#   タグ  … 絞り込みに使うので、記事ごとに手で決めたものを下の TAGS に置きます

TAGS={
 "docomo-newbusiness": [
  "通信",
  "NTTドコモ",
  "iモード",
  "dポイント",
  "ドコモFG"
 ],
 "kddi-newbusiness": [
  "通信",
  "KDDI",
  "au",
  "ローソン",
  "povo"
 ],
 "sony-newbusiness": [
  "電機",
  "ソニー",
  "SSAP",
  "社内起業",
  "aibo"
 ],
 "fujifilm-newbusiness": [
  "化学",
  "富士フイルム",
  "アスタリフト",
  "バイオCDMO",
  "チェキ"
 ],
 "toyota-newbusiness": [
  "自動車",
  "トヨタ",
  "KINTO",
  "MONET",
  "CJPT"
 ],
 "panasonic-newbusiness": [
  "電機",
  "パナソニック",
  "HomeX",
  "Yohana",
  "カーブアウト"
 ],
 "mitsubishi-newbusiness": [
  "商社",
  "三菱商事",
  "ローソン",
  "KDDI",
  "Eneco"
 ],
 "jreast-newbusiness": [
  "鉄道",
  "JR東日本",
  "Suica",
  "JRE BANK",
  "変革2027"
 ],
 "sevenandi-newbusiness": [
  "小売",
  "セブン&アイ",
  "7NOW",
  "Speedway",
  "そごう西武"
 ],
 "recruit-newbusiness": [
  "人材",
  "リクルート",
  "Indeed",
  "Airレジ",
  "Airペイ"
 ],
 "ajinomoto-newbusiness": [
  "食品",
  "味の素",
  "ABF",
  "半導体材料",
  "アミノサイエンス"
 ],
 "softbank-newbusiness": [
  "通信",
  "孫正義",
  "ビジョンファンド",
  "OpenAI",
  "Arm"
 ],
 "newbusiness-money-ranking": [
  "通信",
  "投資額",
  "M&A",
  "買収金額",
  "ランキング"
 ],
 "newbusiness-partners": [
  "人材",
  "支援会社",
  "コンサルティング",
  "顧問",
  "副業人材"
 ],
 "newbusiness-words": [
  "IT",
  "用語",
  "入門",
  "のれん",
  "カーブアウト"
 ],
 "mhi-newbusiness": [
  "製造",
  "三菱重工",
  "H3ロケット",
  "データセンター",
  "JV・合弁"
 ],
 "canon-newbusiness": [
  "電機",
  "キヤノン",
  "ナノインプリント",
  "半導体",
  "M&A"
 ],
 "mercari-newbusiness": [
  "EC",
  "メルカリ",
  "メルペイ",
  "決済",
  "海外展開"
 ],
 "fastretailing-newbusiness": [
  "アパレル",
  "ユニクロ",
  "ジーユー",
  "JV・合弁",
  "オープンイノベーション"
 ],
 "komatsu-newbusiness": [
  "製造",
  "コマツ",
  "Komtrax",
  "IoT",
  "ロボティクス"
 ]
}

def _arow(A):
    y,m,d=A['pub'].split('-')
    return {"n":"%s<br>%s.%s"%(y,m,d),
            "t":A['h1'].replace('<br>',''),
            "d":A['dek'][:56],
            "tags":TAGS.get(A['slug'],[]),
            "st":"pub",
            "u":"/articles/%s/"%A['slug']}

ARTSJS=[_arow(a) for a in sorted(ART,key=lambda a:(a.get('pub',''),a.get('no','')),reverse=True)]
_i=s.index('var ARTS=')
_j=s.index('];',_i)+2
s=s[:_i]+'var ARTS='+json.dumps(ARTSJS,ensure_ascii=False)+';'+s[_j:]

io.open(P,'w',encoding='utf-8').write(s)
print('-> %s  %d社 / %d件 / 記事%d本 / 出典%d件'%(P,NCO,NBIZ,NART,NSRC))
