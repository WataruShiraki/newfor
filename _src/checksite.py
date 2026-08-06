# -*- coding: utf-8 -*-
"""サイト全体の点検"""
import io,os,re,glob
NG=['レポート','失敗','撤退','寿命','いま続いている','次へ渡した','今週','今日の','毎週',
    'undefined','NaN','${','DECISIONS','企業の決断','準備中']
EMO=re.compile('[\U0001F300-\U0001FAFF☀-➿]')
bad=[]
FILES=[p for p in glob.glob('gh/**/*.html',recursive=True) if not p.startswith('gh/_src/')]
FILES+= ['gh/llms.txt']
for p in FILES:
    s=io.open(p,encoding='utf-8').read()
    body=re.sub(r'<script.*?</script>','',s,flags=re.S) if p.endswith('.html') else s
    body=re.sub(r'<style.*?</style>','',body,flags=re.S)
    txt=re.sub(r'<[^>]+>','',body)
    for w in NG:
        if w in txt: bad.append('%s に「%s」'%(p,w))
    if EMO.search(txt): bad.append('%s に絵文字'%p)
    if p.endswith('.html'):
        if '<title>' not in s: bad.append('%s に title がない'%p)
        if 'name="description"' not in s: bad.append('%s に description がない'%p)
# 内部リンク切れ
links=set()
for p in FILES:
    if not p.endswith('.html'): continue
    for m in re.finditer(r'href="(/[^"#?]*)"',io.open(p,encoding='utf-8').read()):
        links.add((p,m.group(1)))
for p,u in sorted(links):
    t='gh'+u
    if u.endswith('/'): t+='index.html'
    if not os.path.exists(t) and not u.startswith('/assets'): bad.append('%s のリンク切れ %s'%(p,u))
print('点検 %d ファイル'%len(FILES))
if bad:
    print('【%d件】'%len(bad))
    for b in sorted(set(bad)): print('  ',b)
else: print('問題なし')
