# -*- coding: utf-8 -*-
import io

def ins(f, anchor, block, before=True, count=1):
    s=io.open(f,encoding='utf-8').read()
    assert anchor in s, f+' :: '+anchor[:50]
    rep = (block+anchor) if before else (anchor+block)
    s=s.replace(anchor, rep, count)
    io.open(f,'w',encoding='utf-8').write(s)

MINI = '\n    <div class="affmini-slot" data-aff="%s"></div>\n'

# --- 記事ページ：本文の途中に1枠、末尾に総合枠 ---
ins('newfor-site.html',
    '<p>この年表から取り出せる、明日から使える教訓は一つだと思う。',
    '<div class="affmini-slot" data-aff="pro"></div>\n    ')

# 記事末（著者ボックス手前 or 出典手前）に転職枠
s=io.open('newfor-site.html',encoding='utf-8').read()
if 'data-aff="pro"></div>' in s and s.count('affslot')==1:
    pass
print('site ok')

# --- 企業DB：グリッドの後ろに枠 ---
ins('newfor-companies.html',
    '    <details class="method">',
    '    <div class="affslot" data-aff="pro" style="margin:30px 0"></div>\n')

# --- KDDIページ：チャートの後にミニ枠 ---
ins('newfor-company-kddi.html',
    '<section class="blk" id="list">',
    '<div class="wrap"><div class="affmini-slot" data-aff="pro"></div></div>\n')

# --- TOP（両方）：レポート一覧の前にミニ枠 ---
for f in ['newfor-top-light.html','newfor-top.html']:
    ins(f, '<section class="blk" id="reports">',
        '<div class="wrap"><div class="affmini-slot" data-aff="learn"></div></div>\n')
print('done')
