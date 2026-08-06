# -*- coding: utf-8 -*-
import io,re

FILES=['newfor-top-light.html','newfor-top.html','newfor-companies.html','newfor-company-kddi.html','newfor-site.html']

# ---- 1) 既存の .aff ブロックを slot に置換 -------------------------------
def strip_aff(s, default):
    i=s.find('<div class="aff">')
    if i<0: return s,False
    # find matching close: count divs
    depth=0; j=i
    while j < len(s):
        m=re.compile(r'<div\b|</div>').search(s,j)
        if not m: break
        if m.group(0)=='</div>': 
            depth-=1
            j=m.end()
            if depth==0: break
        else:
            depth+=1; j=m.end()
    return s[:i]+'<div class="affslot" data-aff="%s"></div>'%default + s[j:], True

DEF={'newfor-top-light.html':'job','newfor-top.html':'job',
     'newfor-company-kddi.html':'job','newfor-site.html':'pro'}

for f in FILES:
    s=io.open(f,encoding='utf-8').read()
    if '<div class="aff">' in s:
        s,ok=strip_aff(s,DEF.get(f,'job'))
        io.open(f,'w',encoding='utf-8').write(s)
        print(f,'aff -> slot',ok)
    else:
        print(f,'no aff block')
