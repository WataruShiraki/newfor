# -*- coding: utf-8 -*-
"""手で管理しているページ（トップ・企業DB）の広告枠を、記事と同じ中身にそろえる

事故の記録
- 記事の広告は artgen.py が afflinks.py から作ります。
- ところがトップと企業DBは手書きHTMLで、その中に**自前の広告JSの写し**が
  入っていました。だから afflinks.py を直しても、この2ページだけ
  ビズリーチ・doda X のままタブつきで残り、公開されていました。
- 同じ内容を2か所に持たない。ここで毎回、記事と同じJSに差し替えます。
"""
import io,re,json,glob
import afflinks

# 広告のJSは artgen.py が gh/assets/aff.js に書き出しています。
# ページには、その1行だけを置きます（中身を二重に持たない）。
import artgen

BEGIN = '<!-- ▼ 広告枠（mkaff.py が入れます。手で書かないでください） ▼ -->'
END   = '<!-- ▲ 広告枠 ここまで ▲ -->'

BLOCK = '%s\n<script src="/assets/aff.js" defer></script>\n%s'%(BEGIN,END)

def strip_old(s):
    """古い自前の広告JSを外す。

    目印は「アフィリエイト枠：読者タイプ別に出し分ける」から始まる即時関数。
    すでに mkaff.py が入れたブロックがあれば、それも外す。
    """
    s = re.sub(re.escape(BEGIN)+r'.*?'+re.escape(END)+r'\s*','',s,flags=re.S)
    s = re.sub(r'<script>\s*/\* ▼ 広告枠.*?▲ 広告枠 ここまで ▲ \*/\s*</script>\s*','',s,flags=re.S)
    i = s.find('/* ===== アフィリエイト枠')
    if i < 0: return s, False
    # <script> ごと消してはいけません。同じ <script> の中に、トップの
    # var MONTH / var ALL など別の仕組みが同居しています（実際に壊しました）。
    # 消すのは、この即時関数 (function(){ ... })(); の範囲だけです。
    st = s.find('(function(){', i)
    if st < 0: return s, False
    depth = 0; k = st
    while k < len(s):
        c = s[k]
        if c == '(': depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                k += 1
                if s[k:k+2] == '()': k += 2
                if s[k:k+1] == ';': k += 1
                break
        k += 1
    return s[:i] + s[k:], True

n=0
for f in ['gh/index.html','gh/companies/index.html']:
    s=io.open(f,encoding='utf-8').read()
    s,removed=strip_old(s)
    if 'affslot' not in s and 'affmini-slot' not in s:
        print('  %s に広告の置き場所（affslot）がありません'%f); continue
    # </body> の直前に入れる
    i=s.rfind('</body>')
    s=s[:i]+BLOCK+'\n'+s[i:]
    io.open(f,'w',encoding='utf-8').write(s); n+=1
    print('  %s  古いJSを外した=%s'%(f,removed))
print('広告枠をそろえたページ: %d'%n)
