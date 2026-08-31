# -*- coding: utf-8 -*-
import sys,os,io,importlib
sys.path.insert(0,'articles')
import artgen
MODS=['a001_docomo','a002_kddi','a003_sony','a004_fujifilm','a005_toyota','a006_panasonic',
      'a007_mitsubishi','a008_jreast','a009_sevenandi','a010_recruit','a011_ajinomoto','a012_softbank',
      'a013_money','a014_partners','a015_words','a016_mhi','a017_canon','a018_mercari','a019_komatsu','a020_fastretailing','a021_dena','a022_lycorp','a023_mufg','a024_rakuten','a025_takeda']
ARTS=[]
for m in MODS:
    mod=importlib.import_module(m)
    a=mod.A
    out='dist/articles/%s/index.html'%a['slug']
    os.makedirs(os.path.dirname(out),exist_ok=True)
    io.open(out,'w',encoding='utf-8').write(artgen.render(a))
    ARTS.append(a)
    print('->',out)
io.open('/tmp/arts.json','w',encoding='utf-8').write(repr([{k:a[k] for k in ('slug','no','company','h1','desc','dek','datejp','read','kw')} for a in ARTS]))
print('articles built:',len(ARTS))
