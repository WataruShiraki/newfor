# -*- coding: utf-8 -*-
import io,glob
TAG = '''<!-- ▼ 計測タグ：G-XXXXXXXXXX を実際の測定IDに置き換えてください（Googleアナリティクス）▼ -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer=window.dataLayer||[];
  function gtag(){dataLayer.push(arguments);}
  gtag('js',new Date());
  gtag('config','G-XXXXXXXXXX');
</script>
<!-- ▲ 計測タグ ここまで ▲ -->
<!-- Search Console はドメイン単位で登録する場合、この meta は不要です。
     HTMLタグで所有権を確認する場合だけ、下の行のコメントを外して content を差し替えてください。
<meta name="google-site-verification" content="ここに確認コード"> -->
'''
n=0
for f in glob.glob('dist/**/*.html',recursive=True)+glob.glob('gh/**/*.html',recursive=True):
    s=io.open(f,encoding='utf-8').read()
    if 'googletagmanager' in s: continue
    i=s.find('</head>')
    if i<0: continue
    s=s[:i]+TAG+s[i:]
    io.open(f,'w',encoding='utf-8').write(s); n+=1
print('analytics injected:',n)
