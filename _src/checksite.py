# -*- coding: utf-8 -*-
"""サイト全体の点検"""
import io,os,re,glob
# 挑戦を否定する言葉は、サイトのどこにも出さない（_src/KOTOBA.md が最上位のルール）
KOTOBA=['どうせ続かない','まだ生きて','生き残','生存率','失敗','しくじり','爆死',
        '終わってる','終わっている','消滅','淘汰','敗者','勝ち組','負け組',
        '撤退','頓挫','挫折','寿命','打ち切り','お蔵入り','黒歴史',
        '意外にも','思ったより']
# 「いま続いている」「次へ渡した」は、KOTOBA.md が勧める言い方に変わったので外しました
NG=KOTOBA+['レポート','今週','今日の','毎週',
    'undefined','NaN','${','DECISIONS','企業の決断','準備中']
# 決まりそのものを説明している文。ここだけは禁止語が出てよい
ALLOW=['提供を終えた事業を「失敗」とは書かず',
       '提供を終えた事業を「失敗」「撤退」とは書きません',
       # 一次情報の正式な題名。会社が出している資料の名前は変えられません
       'ソフトバンクグループレポート2026',
       # 絞り込みで0件になったときだけ出る文。ふだんは表示されません
       'このジャンルは準備中です',
       # 「企業の決断」は昔のサイト名の名残として見ていましたが、
       # 本文の言い回しとしては自然なので、この形だけ通します
       'NEWFORが記録した実際の企業の決断と金額に結びつけて説明します',
       '実際の企業の決断と金額にひもづけて説明する']
EMO=re.compile('[\U0001F300-\U0001FAFF☀-➿]')
bad=[]
FILES=[p for p in glob.glob('gh/**/*.html',recursive=True) if not p.startswith('gh/_src/')]
FILES+= ['gh/llms.txt']
for p in FILES:
    s=io.open(p,encoding='utf-8').read()
    body=re.sub(r'<script.*?</script>','',s,flags=re.S) if p.endswith('.html') else s
    body=re.sub(r'<style.*?</style>','',body,flags=re.S)
    txt=re.sub(r'<[^>]+>','',body)
    for a in ALLOW: txt=txt.replace(a,'')
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
