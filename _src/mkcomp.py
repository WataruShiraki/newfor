# -*- coding: utf-8 -*-
"""企業ページ（/companies/<slug>/）を、記事データから生成する"""
import io,re,sys,os,importlib
sys.path.insert(0,'articles')
import compgen
from compgen import ym,find_end

# (企業ページのslug, 表示名, 正式名, 記事モジュール, OGP画像のslug)
MAP=[
 ('docomo','NTTドコモ','株式会社NTTドコモ','a001_docomo','og-docomo'),
 ('kddi','KDDI','KDDI株式会社','a002_kddi','og-kddi-newbusiness'),
 ('sony','ソニーグループ','ソニーグループ株式会社','a003_sony','og-sony-newbusiness'),
 ('fujifilm','富士フイルム','富士フイルムホールディングス株式会社','a004_fujifilm','og-fujifilm-newbusiness'),
 ('toyota','トヨタ自動車','トヨタ自動車株式会社','a005_toyota','og-toyota-newbusiness'),
 ('panasonic','パナソニック','パナソニック ホールディングス株式会社','a006_panasonic','og-panasonic-newbusiness'),
 ('mitsubishi','三菱商事','三菱商事株式会社','a007_mitsubishi','og-mitsubishi-newbusiness'),
 ('jreast','JR東日本','東日本旅客鉄道株式会社','a008_jreast','og-jreast-newbusiness'),
 ('sevenandi','セブン&アイ','株式会社セブン&アイ・ホールディングス','a009_sevenandi','og-sevenandi-newbusiness'),
 ('recruit','リクルート','株式会社リクルートホールディングス','a010_recruit','og-recruit-newbusiness'),
 ('ajinomoto','味の素','味の素株式会社','a011_ajinomoto','og-ajinomoto-newbusiness'),
 ('softbank','ソフトバンクグループ','ソフトバンクグループ株式会社','a012_softbank','og-softbank-newbusiness'),
]

made=[]
for slug,name,legal,mod,ogslug in MAP:
    A=importlib.import_module(mod).A
    biz=[(ev,ym(y),None if live else find_end(note,ym(y)),live,note) for y,ev,note,live in A['timeline']]
    biz.sort(key=lambda b:b[1])
    nl=sum(1 for b in biz if b[3])
    c=dict(slug=slug,name=name,legal=legal,ogslug=ogslug,
      rep='/articles/%s/'%A['slug'],rept=A['h1'].replace('<br>',''),biz=biz,
      title='%sの新規事業 一覧｜%d件を開始年から記録 ｜ NEWFOR'%(name,len(biz)),
      desc='%sが手がけた新規事業%d件を、公開情報から開始年つきで一覧にしました。いつ始まって、いまどうなっているかを、稼働チャートと年表で確認できます。'%(name,len(biz)),
      lead='公開情報から拾った%d件を、開始年の古い順に並べています。いま提供が続いているものは青、終了または他社へ譲渡したものは紫で示しています。'%len(biz),
      others=[(s,n) for s,n,_,_,_ in MAP if s!=slug])
    os.makedirs('gh/companies/%s'%slug,exist_ok=True)
    io.open('gh/companies/%s/index.html'%slug,'w',encoding='utf-8').write(compgen.render(c))
    made.append((slug,name,len(biz),nl))
    print('  OK %-12s %-14s %2d件（継続%d）'%(slug,name,len(biz),nl))
print('\n%dページ生成'%len(made))
io.open('/tmp/comps.json','w',encoding='utf-8').write(repr(made))
