# -*- coding: utf-8 -*-
"""生成物と生成元の対応を洗う

dist/ に作り直したものと、公開している gh/ の中身を1ファイルずつ突き合わせる。
- 中身が同じ  → 生成元とズレていない
- 中身が違う  → 生成元とズレている（llms.txt の事故と同じ形）
- 生成元なし  → 手で管理している（壊れやすいので記録に残す）
"""
import io,os,glob,hashlib,re
def rd(p):
    try: return io.open(p,'rb').read()
    except: return None
def norm(b):
    if b is None: return None
    s=b.decode('utf-8','replace')
    s=re.sub(r'<lastmod>[^<]*</lastmod>','',s)
    return re.sub(r'\s+','',s)

GH=sorted(p for p in glob.glob('gh/**/*',recursive=True)
          if os.path.isfile(p) and not p.startswith('gh/_src/'))
same=[];diff=[];only_gh=[];only_dist=[]
for p in GH:
    d='dist/'+p[3:]
    if not os.path.exists(d): only_gh.append(p); continue
    (same if norm(rd(p))==norm(rd(d)) else diff).append(p)
for d in sorted(glob.glob('dist/**/*',recursive=True)):
    if not os.path.isfile(d): continue
    if not os.path.exists('gh/'+d[5:]): only_dist.append(d)

print('== 生成元とズレている（要注意） %d件'%len(diff))
for p in diff: print('   ',p)
print('\n== 生成元と一致 %d件'%len(same))
for p in same: print('   ',p)
print('\n== 生成元がない＝手で管理 %d件'%len(only_gh))
for p in only_gh: print('   ',p)
print('\n== dist にあるが公開していない %d件'%len(only_dist))
for p in only_dist: print('   ',p)
