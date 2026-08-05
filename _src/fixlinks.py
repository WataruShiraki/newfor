# -*- coding: utf-8 -*-
import io,glob,re

REP=[
 ('<a href="#about">運営者について</a><a href="#about">掲載の取り下げ</a>',
  '<a href="/about/">運営者について</a><a href="/ads/">広告について</a><a href="/privacy/">プライバシーポリシー</a><a href="/about/">掲載の取り下げ</a>'),
 ('<a href="#about">運営者について</a>','<a href="/about/">運営者について</a>'),
 ('<a href="#about">掲載の取り下げ</a>','<a href="/about/">掲載の取り下げ</a>'),
]
LEGAL_OLD='公開情報に基づく筆者の見解であり、各社の公式見解ではありません。<br>© 2026 NEWFOR'
LEGAL_NEW=('公開情報に基づく筆者の見解であり、各社の公式見解ではありません。<br>'
 '本サイトはアフィリエイトプログラムによる収益を得ています。詳しくは<a href="/ads/">広告について</a>。<br>'
 '<a href="/about/">運営者情報</a>　<a href="/privacy/">プライバシーポリシー</a>　© 2026 NEWFOR')

for f in glob.glob('dist/**/*.html',recursive=True):
    if '/about/' in f or '/ads/' in f or '/privacy/' in f or f.endswith('404.html') or f=='dist/reports/index.html': continue
    s=io.open(f,encoding='utf-8').read(); b=s
    for o,n in REP: s=s.replace(o,n)
    s=s.replace(LEGAL_OLD,LEGAL_NEW)
    # レポート系のアンカーはトップ内なので、下層ページからはトップへ
    if f!='dist/index.html':
        s=re.sub(r'href="#(featured|monthly|alltime|press|mission|list|vote)"', lambda m:'href="/#'+m.group(1)+'"', s)
    io.open(f,'w',encoding='utf-8').write(s)
    print(f,'changed' if s!=b else '-')
