# -*- coding: utf-8 -*-
import re,colorsys,io,sys,glob

SHIFT = float(sys.argv[1]) if len(sys.argv)>1 else 14.0   # degrees toward blue
LO,HI = 238.0, 300.0      # hue range treated as "violet"
FLOOR = 232.0             # don't go bluer than this

def shift_rgb(r,g,b):
    h,l,s = colorsys.rgb_to_hls(r/255,g/255,b/255)
    hd = h*360
    if not (LO <= hd <= HI): return None
    if s < 0.25 or l < 0.15 or l > 0.985: return None
    nh = max(FLOOR, hd - SHIFT)
    nr,ng,nb = colorsys.hls_to_rgb(nh/360,l,s)
    return (round(nr*255),round(ng*255),round(nb*255))

def hexrep(m):
    v=m.group(1)
    if len(v)==3: v=''.join(c*2 for c in v)
    r,g,b=int(v[0:2],16),int(v[2:4],16),int(v[4:6],16)
    n=shift_rgb(r,g,b)
    if not n: return m.group(0)
    return '#%02X%02X%02X'%n

def rgbrep(m):
    parts=[p.strip() for p in m.group(2).split(',')]
    try: r,g,b=int(parts[0]),int(parts[1]),int(parts[2])
    except: return m.group(0)
    n=shift_rgb(r,g,b)
    if not n: return m.group(0)
    rest=(','+','.join(parts[3:])) if len(parts)>3 else ''
    return '%s(%d,%d,%d%s)'%(m.group(1),n[0],n[1],n[2],rest)

files=sys.argv[2:]
for f in files:
    s=io.open(f,encoding='utf-8').read()
    before=s
    s=re.sub(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b',hexrep,s)
    s=re.sub(r'\b(rgba?)\(([^)]+)\)',rgbrep,s)
    io.open(f,'w',encoding='utf-8').write(s)
    print(f,'changed' if s!=before else 'nochange')
