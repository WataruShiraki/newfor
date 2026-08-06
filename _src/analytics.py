# -*- coding: utf-8 -*-
"""計測タグと所有権確認タグを、全ページの <head> に入れる

何度実行しても二重には入りません（すでに入っていれば中身だけ差し替えます）。

- Search Console: 所有権確認の meta タグ
- Googleアナリティクス: GA4 の測定ID。下の GA4 に 'G-…' を書くと全ページに入ります
"""
import io,re,glob

GSC='ILi3j4478KpGhXmwH0D77jZKrsfjs0yBBHuS9ZnjljE'   # Search Console 所有権確認コード
GA4='G-Y9N8CYZE61'   # Googleアナリティクス（GA4）の測定ID

VERIFY='<meta name="google-site-verification" content="%s">'%GSC
GTAG=(('<!-- Googleアナリティクス -->\n'
 '<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>\n'
 '<script>\n'
 '  window.dataLayer=window.dataLayer||[];\n'
 '  function gtag(){dataLayer.push(arguments);}\n'
 "  gtag('js',new Date());\n"
 "  gtag('config','%s');\n"
 '</script>\n')%(GA4,GA4)) if GA4 else ''

nv=ng=0
for f in sorted(set(glob.glob('dist/**/*.html',recursive=True)+glob.glob('gh/**/*.html',recursive=True))):
    if '/_src/' in f: continue
    s=io.open(f,encoding='utf-8').read()
    if '</head>' not in s: continue
    orig=s

    # ── 古い置き場所を片づける ──
    s=re.sub(r'<!-- ▼ 計測タグ.*?<!-- ▲ 計測タグ ここまで ▲ -->\n?','',s,flags=re.S)
    s=re.sub(r'<!-- Search Console はドメイン単位.*?-->\n?','',s,flags=re.S)

    # ── 所有権確認タグ ──
    if 'google-site-verification' in s:
        s=re.sub(r'<meta name="google-site-verification"[^>]*>',VERIFY,s)
    else:
        i=s.find('</head>'); s=s[:i]+VERIFY+'\n'+s[i:]; nv+=1

    # ── 計測タグ ──
    if GA4:
        if 'googletagmanager' in s:
            s=re.sub(r'id=G-[A-Z0-9]+','id=%s'%GA4,s)
            s=re.sub(r"'G-[A-Z0-9]+'","'%s'"%GA4,s)
        else:
            i=s.find('</head>'); s=s[:i]+GTAG+s[i:]; ng+=1

    if s!=orig: io.open(f,'w',encoding='utf-8').write(s)
print('所有権確認タグ: 新たに%dページへ / 計測タグ: %s'
      %(nv,'%dページへ'%ng if GA4 else '測定IDが未設定のため入れていません'))
