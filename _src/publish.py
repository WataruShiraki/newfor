# -*- coding: utf-8 -*-
import io,os,re,shutil,json
from seohead import PAGES,LINKMAP,head_block,SITE,DESC_SITE

DIST='dist'
if os.path.exists(DIST): shutil.rmtree(DIST)
os.makedirs(DIST+'/assets',exist_ok=True)

def rewrite_links(s):
    for old,new in LINKMAP.items():
        s=s.replace('href="'+old+'"','href="'+new+'"')
        s=s.replace("'"+old+"'","'"+new+"'")   # JS PAGES map
        s=s.replace('"'+old+'"','"'+new+'"')
    return s

for src,p in PAGES.items():
    s=io.open(src,encoding='utf-8').read()
    s=rewrite_links(s)
    # replace title / description
    s=re.sub(r'<title>.*?</title>','<title>%s</title>'%p['title'],s,count=1,flags=re.S)
    if '<meta name="description"' in s:
        s=re.sub(r'<meta name="description" content=".*?">','<meta name="description" content="%s">'%p['desc'],s,count=1,flags=re.S)
    else:
        s=s.replace('</title>','</title>\n<meta name="description" content="%s">'%p['desc'],1)
    # drop old inline favicon
    s=re.sub(r'<link rel="icon" href="data:image/svg\+xml[^>]*>\n?','',s)
    # inject head block before </head> ... actually before <style>
    s=s.replace('<style>', head_block(src,p)+'<style>',1)
    out=os.path.join(DIST,p['out'])
    os.makedirs(os.path.dirname(out),exist_ok=True)
    io.open(out,'w',encoding='utf-8').write(s)
    print('->',p['out'],len(s))
