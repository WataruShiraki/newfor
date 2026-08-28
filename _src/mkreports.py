# -*- coding: utf-8 -*-
"""記事一覧のカードを、記事データから生成する"""
import io,os,re,sys,json,importlib
sys.path.insert(0,'articles')
import artgen
from artgen import CSS,UFO,AFF_JS,SITE


# ── ジャンル定義 ──
GENRES=[
 ('decisions','新規事業ヒストリー','HISTORY','1社の新規事業を、始まりから今日まで並べた記録。NEWFORの背骨になるジャンルです。'),
 ('ranking','ランキング','RANKING','数字と読者の投票で順位をつけます。投資額、書籍、新規事業オブザイヤーなど。'),
 ('partners','新規事業のお供','PARTNERS','社内に足りない力を、外から借りるための選択肢。コンサル、顧問、ツールを比べます。'),
 ('handbook','入門','HANDBOOK','新規事業のやり方と言葉。担当になったばかりの方が、最初に読む場所です。'),
]

# ── お悩みの型 ──
#
# 記事ごとの「こんな方におすすめ」は45個すべて違う文で、そのままでは
# 絞り込みに使えませんでした。10種類に束ねて、記事側（articles/a0*.py の
# topics）で2〜3個ずつ選びます。記事の中の文はそのまま残しています。
TOPICS=[
 ('approval','社内を通す'),
 ('seed','ネタを見つける'),
 ('strength','自社の強みを見極める'),
 ('partner','他社と組む'),
 ('buildbuy','買うか、作るか'),
 ('money','お金の話'),
 ('handoff','次へ渡す判断'),
 ('explain','成果を説明する'),
 ('longrun','長い時間と戦う'),
 ('starter','担当になったばかり'),
]
TOPIC_JA=dict(TOPICS)

MODS=['a001_docomo','a002_kddi','a003_sony','a004_fujifilm','a005_toyota','a006_panasonic',
      'a007_mitsubishi','a008_jreast','a009_sevenandi','a010_recruit','a011_ajinomoto','a012_softbank',
      'a013_money','a014_partners','a015_words','a016_mhi','a017_canon','a018_mercari','a019_komatsu','a020_fastretailing','a021_dena','a022_lycorp']

# 業種ごとの色（ライト/ダークで別指定）
HUE={
 '通信':   ('#2F3BD6','#1E2599','rgba(47,59,214,.10)','#7C8CFF'),
 '電機':   ('#6D3BD6','#4E2699','rgba(109,59,214,.10)','#A98CFF'),
 '化学':   ('#0E8478','#0A5E55','rgba(14,132,120,.11)','#3FC9B8'),
 '自動車': ('#C63E08','#8F2C05','rgba(198,62,8,.10)','#FF8A4C'),
 '商社':   ('#9A6800','#6E4A00','rgba(154,104,0,.12)','#E5A93A'),
 '鉄道':   ('#166B34','#0F4A24','rgba(22,107,52,.11)','#46B872'),
 '小売':   ('#B02060','#7C1743','rgba(176,32,96,.10)','#F272A8'),
 '人材':   ('#2A4BAE','#1C3480','rgba(42,75,174,.11)','#7EA0FF'),
 '食品':   ('#B5480E','#7F320A','rgba(181,72,14,.11)','#FF9A5C'),
 '輸送機器': ('#1F5FA8','#153F73','rgba(31,95,168,.11)','#68A8F0'),
 'EC':     ('#0B7285','#08505E','rgba(11,114,133,.11)','#3FBCD4'),
 'アパレル': ('#8A2E5E','#611F42','rgba(138,46,94,.11)','#E07AAE'),
}
IND={'NTTドコモ':'通信','KDDI':'通信','ソニーグループ':'電機','富士フイルム':'化学',
     'トヨタ自動車':'自動車','パナソニック':'電機','パナソニックHD':'電機','三菱商事':'商社','JR東日本':'鉄道',
     'セブン&アイ':'小売','リクルート':'人材','リクルートHD':'人材','味の素':'食品',
     'ソフトバンクグループ':'通信','三菱重工業':'輸送機器','キヤノン':'電機','メルカリ':'EC','コマツ':'輸送機器','ファーストリテイリング':'アパレル'}

def tag_of(fw):
    """forwho の <strong>…方へ。</strong> から短いタグを作る"""
    m=re.search(r'<strong>(.*?)</strong>',fw)
    t=m.group(1) if m else fw
    t=re.sub(r'^(新規事業の|新規事業を|自社の|社内の)','',t)
    t=t.replace('方へ。','方').replace('方へ！','方').replace('へ。','').rstrip('。！')
    return t

def learn_of(A):
    """summary から「分かること」を2つ"""
    out=[]
    for s in A['summary'][:2]:
        t=re.sub('<[^>]+>','',s)
        t=re.split(r'。',t)[0]
        out.append(t[:52]+('…' if len(t)>52 else ''))
    return out

CARDS=[]
for m in MODS:
    A=importlib.import_module(m).A
    ind=A.get('ind') or IND.get(A['company'],'通信')
    c1,c2,cw,cd=HUE.get(ind,HUE['通信'])
    k=A['kpis'][0]
    hero=(k[0],k[1],k[2])
    # いちばん数字が目を引くKPIを選ぶ
    for kk in A['kpis']:
        if any(u in kk[2] for u in ['兆円','億円']) and len(kk[1])<=6:
            hero=(kk[0],kk[1],kk[2]); break
    CARDS.append(dict(
      genre=A.get('genre','decisions'), meta=A.get('cardmeta'),
      gname=A.get('section') or '新規事業ヒストリー',
      no=A['no'], slug=A['slug'], company=A['company'], ind=ind,
      c1=c1,c2=c2,cw=cw,cd=cd,
      h1=A['h1'].replace('<br>',''), read=A['read'],
      hero=hero, tags=[tag_of(x) for x in A.get('forwho',[])][:3],
      learn=learn_of(A), nbiz=len(A.get('timeline') or []),
      nlive=sum(1 for r in (A.get('timeline') or []) if r[3]),
      pub=A.get('pub') or '', topics=[t for t in (A.get('topics') or []) if t in TOPIC_JA],
      # 業種は「1社を追った記録」だけに付けます。ランキングや入門は1社の話では
      # ないので、業種の札を出すと（ランキングが「通信」に見えて）誤解を生みます。
      # 色は ind から取るので、ind そのものは残しておきます。
      indshow=(ind if A.get('genre','decisions')=='decisions' else ''),
    ))

# ── 並び順は新着順 ──
#
# これまでは MODS の並び（番号順）でした。毎日1本ずつ増えていくので、
# 新しいものが先頭に来ないと、増えたことに気づけません。
# 公開日が同じ日なら、番号の大きいほうを先にします。
CARDS.sort(key=lambda c:(c['pub'], c['no']), reverse=True)

for c in CARDS:
    if not c['topics']:
        print('   ！ 記事 #%s に topics がありません（絞り込みに出てきません）'%c['no'])

def card(c):
    tags=''.join('<span class="rt">%s</span>'%t for t in c['tags'])
    learn=''.join('<li>%s</li>'%x for x in c['learn'])
    return '''<a class="rcard" data-g="%(genre)s" data-ind="%(indshow)s" data-t="%(tp)s" data-read="%(read)s" data-no="%(no)s" href="/articles/%(slug)s/" style="--c1:%(c1)s;--c2:%(c2)s;--cw:%(cw)s;--cd:%(cd)s">
  <span class="rc-hd">
    <span class="rc-no">%(gname)s <b>#%(no)s</b></span>
    <span class="rc-co">%(company)s%(indtag)s</span>
  </span>
  <span class="rc-body">
    <span class="rc-ttl">%(h1)s</span>
    <span class="rc-hero"><b>%(hv)s</b><i>%(hu)s</i><span class="rc-hk">%(hk)s</span></span>
    <span class="rc-learn"><span class="rc-lk">この記録で分かること</span><ul>%(learn)s</ul></span>
    <span class="rc-tags"><span class="rc-lk">こんな方におすすめ</span>%(tags)s</span>
    <span class="rc-tp">%(tplabel)s</span>
  </span>
  <span class="rc-foot">
    <span class="rc-meta">%(meta)s</span>
    <span class="rc-go">読む<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>
  </span>
</a>'''%dict(c,hv=c['hero'][1],hu=c['hero'][2],hk=c['hero'][0],tags=tags,learn=learn,
       gname=c.get('gname') or '新規事業ヒストリー',
       tp=' '.join(c['topics']),
       indtag=('<em>%s</em>'%c['indshow'] if c['indshow'] else ''),
       tplabel=''.join('<span class="tpx">%s</span>'%TOPIC_JA[t] for t in c['topics']),
       meta=c.get('meta') or ('記録した新規事業 <b>%d</b>件　じっくり読んで <b>約%s分</b>'%(c['nbiz'],c['read'])))

EXTRA='''

/* ── 絞り込み（3つの軸）── */
.fgrp{margin:20px 0 0}
/* 携帯のときだけ出る、開け閉めのボタン */
.ftoggle{display:none;font:inherit;font-size:14px;font-weight:800;width:100%;
 align-items:center;justify-content:center;gap:8px;margin:20px 0 0;
 padding:14px 18px;border-radius:14px;border:1.5px solid var(--border);
 background:var(--surface);color:var(--tx-2);cursor:pointer}
.ftoggle svg{transition:transform .18s ease}
.ftoggle[aria-expanded="true"] svg{transform:rotate(180deg)}
.ftoggle .fnum{font-family:ui-monospace,Menlo,monospace;font-size:11px;background:var(--blue);
 color:#fff;border-radius:11px;padding:2px 8px}
@media(max-width:700px){
  .ftoggle{display:flex}
  .ffilters{display:none}
  .ffilters.open{display:block}
  .gtab{font-size:12.5px;padding:9px 14px;gap:6px}
  .gtab .en{display:none}
  .fbar{margin-top:16px}
}
.flab{font-size:11.5px;font-weight:800;letter-spacing:.14em;color:var(--tx-3);margin-bottom:9px}
.fbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;
 border-top:1px solid var(--border);margin-top:22px;padding-top:16px}
.fhit{font-size:14px;font-weight:800;color:var(--tx-2)}
.fhit b{color:var(--blue);font-size:21px;font-family:ui-monospace,Menlo,monospace;margin-right:3px}
.fright{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.fsorts{display:flex;gap:6px}
.fsort{font:inherit;font-size:12.5px;font-weight:700;padding:8px 14px;border-radius:9px;
 border:1.5px solid var(--border);background:var(--page);color:var(--tx-3);cursor:pointer;
 transition:all .13s ease}
.fsort:hover{border-color:var(--blue);color:var(--blue)}
.fsort.on{background:var(--tx-1);border-color:var(--tx-1);color:var(--page)}
.fclr{font:inherit;font-size:12.5px;font-weight:800;color:var(--orange);background:none;
 border:0;cursor:pointer;text-decoration:underline;padding:6px 2px}
/* カードの中の、お悩みの型 */
.rc-tp{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.rc-tp .tpx{font-size:11px;font-weight:700;background:var(--surface-2);color:var(--tx-3);
 border-radius:8px;padding:3px 9px}
.gtabs{display:flex;gap:9px;flex-wrap:wrap;margin:0 0 8px}
.gtab{font:inherit;font-size:13.5px;font-weight:800;padding:11px 18px;border-radius:24px;
 border:1.5px solid var(--border);background:var(--page);color:var(--tx-3);cursor:pointer;
 display:inline-flex;align-items:center;gap:8px;transition:all .14s ease}
.gtab:hover{border-color:var(--blue);color:var(--blue)}
.gtab.on{background:var(--blue);border-color:var(--blue);color:#fff}
.gtab .en{font-family:ui-monospace,Menlo,monospace;font-size:9px;letter-spacing:.13em;opacity:.72}
.gtab .cnt{font-family:ui-monospace,Menlo,monospace;font-size:11px;background:var(--surface-2);
 color:var(--tx-3);border-radius:11px;padding:2px 8px}
.gtab.on .cnt{background:rgba(255,255,255,.24);color:#fff}
.gtab.empty{opacity:.62}
.gdesc{font-size:13.5px;line-height:1.9;color:var(--tx-3);background:var(--surface-2);
 border-radius:13px;padding:14px 18px;margin:14px 0 4px}
.gempty{text-align:center;padding:56px 22px;background:var(--surface-2);border-radius:18px;
 border:1.5px dashed var(--border);margin:24px 0}
.gempty b{display:block;font-size:17px;font-weight:800;color:var(--tx-1);margin-bottom:9px}
.gempty span{font-size:13.5px;line-height:1.9;color:var(--tx-3)}
.rgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:22px;margin:34px 0 10px}
@media(max-width:900px){.rgrid{grid-template-columns:1fr;gap:17px}}
.rcard{display:flex;flex-direction:column;background:var(--surface);border:1px solid var(--border);
 border-radius:20px;overflow:hidden;text-decoration:none;color:inherit;box-shadow:var(--sh);
 transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease}
.rcard:hover{transform:translateY(-4px);border-color:var(--c1);box-shadow:0 16px 42px -20px rgba(20,16,40,.5)}
.rc-hd{background:linear-gradient(112deg,var(--c1),var(--c2));padding:16px 22px;display:flex;
 flex-direction:column;gap:5px;position:relative;overflow:hidden}
.rc-hd::after{content:"";position:absolute;right:-40px;top:-46px;width:150px;height:150px;
 border-radius:50%;background:rgba(255,255,255,.09)}
.rc-no{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.18em;
 color:rgba(255,255,255,.78);font-weight:700;position:relative;z-index:1}
.rc-co{font-size:19px;font-weight:800;letter-spacing:-.02em;color:#fff;position:relative;z-index:1}
.rc-co em{font-style:normal;font-size:11.5px;font-weight:600;background:rgba(255,255,255,.2);
 border-radius:10px;padding:3px 9px;margin-left:9px;vertical-align:middle}
.rc-body{padding:20px 22px 6px;flex:1 1 auto;display:flex;flex-direction:column}
.rc-ttl{font-size:18px;font-weight:800;letter-spacing:-.025em;line-height:1.6;margin-bottom:15px}
@media(max-width:640px){.rc-ttl{font-size:16.5px}}
.rc-hero{display:flex;align-items:baseline;gap:3px;background:var(--cw);border-radius:13px;
 padding:13px 16px;margin-bottom:15px;flex-wrap:wrap}
:root[data-theme="dark"] .rc-hero{background:rgba(255,255,255,.06)}
.rc-hero b{font-size:30px;font-weight:800;letter-spacing:-.04em;color:var(--c1);
 font-family:ui-monospace,Menlo,monospace;line-height:1}
:root[data-theme="dark"] .rc-hero b{color:var(--c1)}
.rc-hero i{font-style:normal;font-size:13px;font-weight:800;color:var(--c1);margin-right:9px}
:root[data-theme="dark"] .rc-hero i{color:var(--c1)}
.rc-hk{font-size:12px;color:var(--tx-3);font-weight:600;line-height:1.5}
.rc-lk{display:block;font-family:ui-monospace,Menlo,monospace;font-size:9.5px;letter-spacing:.13em;
 color:var(--tx-3);font-weight:700;margin-bottom:8px}
.rc-learn{margin-bottom:15px}
.rc-learn ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:7px}
.rc-learn li{font-size:13.5px;line-height:1.75;padding-left:19px;position:relative;color:var(--tx-2)}
.rc-learn li::before{content:"";position:absolute;left:2px;top:.6em;width:7px;height:7px;
 border-radius:2px;background:var(--c1)}
:root[data-theme="dark"] .rc-learn li::before{background:var(--c1)}
.rc-tags{display:block;margin-bottom:6px}
.rt{display:inline-block;font-size:11.5px;font-weight:700;background:var(--cw);color:var(--c1);
 border-radius:20px;padding:5px 12px;margin:0 6px 6px 0;line-height:1.5}
:root[data-theme="dark"] .rt{background:rgba(255,255,255,.08);color:var(--c1)}
.rc-foot{border-top:1px solid var(--border);padding:13px 22px;display:flex;align-items:center;
 justify-content:space-between;gap:12px;flex-wrap:wrap}
.rc-meta{font-size:11.5px;color:var(--tx-3);line-height:1.7}
.rc-meta b{color:var(--tx-1);font-weight:800}
.rc-go{font-size:13px;font-weight:800;color:var(--c1);display:inline-flex;align-items:center;gap:5px;white-space:nowrap}
:root[data-theme="dark"] .rc-go{color:var(--c1)}
.rcard:hover .rc-go svg{transform:translateX(3px)}
.rc-go svg{transition:transform .16s ease}
.rlead{font-size:15px;line-height:1.95;color:var(--tx-2);max-width:720px;margin:0 0 4px}
'''
