# -*- coding: utf-8 -*-
"""NEWFOR のロゴとSNS用画像を、SVGとして書き出す

書き出したSVGは brandpng.js が PNG に変換します。
色や形を直したいときは、このファイルだけ触れば全部そろい直します。
"""
import io,os

OUT='brand'
os.makedirs(OUT,exist_ok=True)

# ── ブランドの色 ──
BLUE='#2F3BD6'      # 基本の青
BLUE_D='#212DBE'    # 濃い青
ORANGE='#E04A0C'    # 差し色のオレンジ
INK='#0C0A16'       # 文字の黒
PAPER='#F6F5F2'     # 背景の生成り
WHITE='#FFFFFF'

# ── UFOのマーク（32×32の座標系） ──
UFO = ('<path d="M10.6 16.4 L21.4 16.4 L25.8 31 L6.2 31 Z" fill="%(c)s" opacity=".16"/>'
 '<path d="M12.5 16.4 L19.5 16.4 L21.9 26.5 L10.1 26.5 Z" fill="%(c)s" opacity=".24"/>'
 '<ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="%(c)s"/>'
 '<path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="%(c)s" '
 'stroke-width="2.3" stroke-linecap="round" fill="none"/>')

def mark(color): return UFO%{'c':color}

FONT=("-apple-system,'Hiragino Kaku Gothic ProN','Yu Gothic',"
      "'Helvetica Neue',Helvetica,Arial,sans-serif")

def wordmark(x,y,size,c1,c2,anchor='start'):
    """NEW を c1、FOR を c2 で書く"""
    return ('<text x="%g" y="%g" text-anchor="%s" font-family="%s" font-weight="900" '
            'font-size="%g" letter-spacing="%g">'
            '<tspan fill="%s">NEW</tspan><tspan fill="%s">FOR</tspan></text>'
            %(x,y,anchor,FONT,size,-size*0.022,c1,c2))

def svg(w,h,body,bg=None):
    b=('<rect width="%d" height="%d" fill="%s"/>'%(w,h,bg)) if bg else ''
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d">%s%s</svg>'%(w,h,w,h,b,body))

def put(name,s):
    io.open('%s/%s.svg'%(OUT,name),'w',encoding='utf-8').write(s)

def scaled_mark(cx,cy,size,color):
    """32座標系のUFOを、好きな位置と大きさに置く"""
    k=size/32.0
    return '<g transform="translate(%g %g) scale(%g)">%s</g>'%(cx,cy,k,mark(color))

# ══ 1. ロゴ（マークのみ） ══
for nm,c,bg in [('mark-blue',BLUE,None),('mark-white',WHITE,None),
                ('mark-ink',INK,None),('mark-orange',ORANGE,None)]:
    put('logo-%s'%nm, svg(32,32,mark(c),bg))

# ══ 2. ロゴ（マーク＋文字／横組み） ══
def lockup(c_mark,c_new,c_for,bg=None):
    return svg(320,80,
      scaled_mark(8,20,44,c_mark)+wordmark(64,54,38,c_new,c_for), bg)
put('logo-lockup-light', lockup(BLUE,INK,ORANGE))
put('logo-lockup-dark',  lockup(WHITE,WHITE,ORANGE))
put('logo-lockup-mono',  lockup(INK,INK,INK))
put('logo-lockup-onblue',lockup(WHITE,WHITE,'#FFB08A'))

# ══ 3. ロゴ（マーク＋文字／縦組み） ══
def stack(c_mark,c_new,c_for,bg=None):
    """マークの真下に文字を置く。間が空きすぎないよう、絵の下端に合わせる"""
    return svg(320,196,
      scaled_mark(112,12,96,c_mark)+wordmark(160,152,44,c_new,c_for,'middle')+
      '<text x="160" y="178" text-anchor="middle" font-family="%s" font-size="12.5" '
      'font-weight="700" letter-spacing="3.2" fill="%s" opacity=".78">新規事業ヒストリー</text>'
      %(FONT,c_new), bg)
put('logo-stack-light', stack(BLUE,INK,ORANGE))
put('logo-stack-dark',  stack(WHITE,WHITE,ORANGE))

# ══ 4. SNSのアイコン（正方形） ══
def icon(size,bg,c_mark,ring=None):
    """マークの中心を、正方形の中心にきちんと合わせる

    UFOの絵は32座標系で x=3.4〜28.6 / y=6.5〜31 を使う。
    見た目の中心は (16, 18.75) なので、そこが正方形の真ん中に来るよう置く。
    円形に切り抜かれるSNS（X・Instagram）でも欠けない大きさにしてある。
    """
    k=0.66
    cx=size*0.5-16*k*size/32.0
    cy=size*0.5-18.75*k*size/32.0
    b=''
    if ring: b+='<circle cx="%g" cy="%g" r="%g" fill="none" stroke="%s" stroke-width="%g"/>'%(
        size/2,size/2,size*0.44,ring,size*0.012)
    b+=scaled_mark(cx,cy,size*k,c_mark)
    return svg(size,size,b,bg)
put('icon-blue',   icon(1000,BLUE,WHITE))
put('icon-white',  icon(1000,WHITE,BLUE))
put('icon-paper',  icon(1000,PAPER,BLUE))
put('icon-ink',    icon(1000,INK,WHITE))
put('icon-orange', icon(1000,ORANGE,WHITE))

# ══ 5. X（旧Twitter）のヘッダー 1500×500 ══
def header_x():
    b=('<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
       '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>'%(BLUE,BLUE_D))
    b+='<rect width="1500" height="500" fill="url(#g)"/>'
    # うっすら年表の線を敷く
    for i in range(9):
        x=170+i*150
        b+='<line x1="%d" y1="330" x2="%d" y2="400" stroke="#fff" stroke-opacity=".13" stroke-width="2"/>'%(x,x)
    b+='<rect x="170" y="362" width="1160" height="6" rx="3" fill="#fff" fill-opacity=".16"/>'
    for i,(x,w,c) in enumerate([(170,240,'#fff'),(430,180,'#fff'),(640,300,ORANGE),(970,120,'#fff'),(1120,210,ORANGE)]):
        b+='<rect x="%d" y="362" width="%d" height="6" rx="3" fill="%s" fill-opacity="%s"/>'%(x,w,c,'.85' if c=='#fff' else '1')
    b+=scaled_mark(170,92,96,WHITE)
    b+=wordmark(292,190,76,'#FFFFFF','#FFB08A')
    b+=('<text x="172" y="258" font-family="%s" font-size="30" font-weight="700" '
        'fill="#fff" fill-opacity=".92">新規事業ヒストリーメディア</text>'%FONT)
    b+=('<text x="172" y="306" font-family="%s" font-size="21" font-weight="500" '
        'fill="#fff" fill-opacity=".72">大企業が何を始めて、いまどうなっているか。'
        '開始年・継続状況・出典つきの年表で記録しています。</text>'%FONT)
    b+=('<text x="1330" y="440" text-anchor="end" font-family="%s" font-size="20" '
        'font-weight="700" fill="#fff" fill-opacity=".6" letter-spacing="1.5">newfor.jp</text>'%FONT)
    return svg(1500,500,b)
put('header-x', header_x())

# ══ 6. note のヘッダー 1280×670 ══
def header_note(W=1280,H=670):
    k=W/1280.0
    b='<rect width="%d" height="%d" fill="%s"/>'%(W,H,PAPER)
    b+='<rect x="0" y="0" width="1280" height="14" fill="%s"/>'%BLUE
    b+=scaled_mark(96,150,110,BLUE)
    b+=wordmark(230,262,84,INK,ORANGE)
    b+=('<text x="98" y="340" font-family="%s" font-size="34" font-weight="800" '
        'fill="%s">新規事業ヒストリーメディア</text>'%(FONT,BLUE))
    b+=('<text x="98" y="400" font-family="%s" font-size="23" font-weight="500" '
        'fill="#403C55">うまくいかなかったように見える挑戦にも、次の事業へ渡されたバトンがある。</text>'%FONT)
    b+=('<text x="98" y="438" font-family="%s" font-size="23" font-weight="500" '
        'fill="#403C55">それを一件ずつ掘り起こして年表にし、この国の新規事業の成功率を上げていく。</text>'%FONT)
    b+='<rect x="98" y="490" width="1084" height="4" rx="2" fill="%s" fill-opacity=".22"/>'%BLUE
    for x,w,c in [(98,300,BLUE),(430,160,ORANGE),(620,280,BLUE),(930,120,ORANGE),(1080,102,BLUE)]:
        b+='<rect x="%d" y="490" width="%d" height="4" rx="2" fill="%s"/>'%(x,w,c)
    b+=('<text x="98" y="560" font-family="%s" font-size="19" font-weight="700" '
        'fill="#57536D" letter-spacing="1.2">公開情報だけを使って記録しています　／　newfor.jp</text>'%FONT)
    return svg(1280,670,b)
put('header-note', header_note())

# ══ 6b. note のヘッダー 1920×1006（実機で切れない版） ══
def header_note_wide(W=1920,H=1006):
    """noteのクリエイターページは、ヘッダーの入れ物が横に細長い。
    パソコンで見ると 1202×203（＝横5.9倍）の枠に object-fit:cover で入るため、
    1920×1006 の画像は「まん中の32%だけ」しか映らない（実際に上下が切れた）。
    そこで、文字と絵は必ず y=340〜666 の帯の中に収める。
    外側は背景だけにしておけば、スマホの少し縦長な切り抜きでも破綻しない。
    """
    Y0,Y1=340,666            # 見せたいものを置ける帯
    L,R=200,1720             # 左右の余白
    b='<rect width="%d" height="%d" fill="%s"/>'%(W,H,PAPER)
    # 帯の外は「どこで切られても同じ」に見えるよう、色を変えない
    b+=scaled_mark(L,382,104,BLUE)
    b+=wordmark(L+136,478,88,INK,ORANGE)
    b+=('<text x="%d" y="478" text-anchor="end" font-family="%s" font-size="26" '
        'font-weight="700" fill="#57536D" letter-spacing="1.4">newfor.jp</text>'%(R,FONT))
    b+=('<text x="%d" y="542" font-family="%s" font-size="33" font-weight="800" '
        'fill="%s">新規事業ヒストリーメディア</text>'%(L+2,FONT,BLUE))
    b+=('<text x="%d" y="588" font-family="%s" font-size="24" font-weight="500" '
        'fill="#403C55">大企業が何を始めて、いまどうなっているか。'
        '開始年・継続状況・出典つきの年表で記録しています。</text>'%(L+2,FONT))
    b+='<rect x="%d" y="622" width="%d" height="5" rx="2" fill="%s" fill-opacity=".2"/>'%(L+2,R-L-2,BLUE)
    for x,w,c in [(0,430,BLUE),(480,220,ORANGE),(760,400,BLUE),(1210,170,ORANGE),(1430,88,BLUE)]:
        b+='<rect x="%d" y="622" width="%d" height="5" rx="2" fill="%s"/>'%(L+2+x,w,c)
    return svg(W,H,b)
put('header-note-wide', header_note_wide())

# ══ 7. 正方形の投稿用テンプレ 1080×1080（Instagram） ══
def post_square():
    b='<rect width="1080" height="1080" fill="%s"/>'%PAPER
    b+='<rect x="0" y="0" width="1080" height="16" fill="%s"/>'%BLUE
    b+=scaled_mark(72,96,84,BLUE)
    b+=wordmark(176,184,62,INK,ORANGE)
    b+=('<text x="74" y="330" font-family="%s" font-size="56" font-weight="900" '
        'fill="%s">ここに見出しを</text>'%(FONT,INK))
    b+=('<text x="74" y="410" font-family="%s" font-size="56" font-weight="900" '
        'fill="%s">2行まで入ります</text>'%(FONT,INK))
    b+='<rect x="74" y="470" width="932" height="5" rx="2" fill="%s" fill-opacity=".2"/>'%BLUE
    for x,w,c in [(74,260,BLUE),(360,140,ORANGE),(530,240,BLUE),(800,206,ORANGE)]:
        b+='<rect x="%d" y="470" width="%d" height="5" rx="2" fill="%s"/>'%(x,w,c)
    b+=('<text x="74" y="560" font-family="%s" font-size="30" font-weight="600" '
        'fill="#403C55">説明文がここに入ります。3行くらいまでが読みやすいです。</text>'%FONT)
    b+='<rect x="74" y="880" width="380" height="72" rx="36" fill="%s"/>'%BLUE
    b+=('<text x="264" y="927" text-anchor="middle" font-family="%s" font-size="27" '
        'font-weight="800" fill="#fff">newfor.jp で見る</text>'%FONT)
    b+=('<text x="1006" y="1010" text-anchor="end" font-family="%s" font-size="22" '
        'font-weight="700" fill="#57536D" letter-spacing="1.4">新規事業ヒストリーメディア</text>'%FONT)
    return svg(1080,1080,b)
put('post-square', post_square())

# ══ 8. 縦長の投稿用テンプレ 1080×1920（TikTok・ストーリーズ） ══
def post_vertical():
    b=('<defs><linearGradient id="v" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>'%(BLUE,BLUE_D))
    b+='<rect width="1080" height="1920" fill="url(#v)"/>'
    b+=scaled_mark(80,150,96,WHITE)
    b+=wordmark(200,232,68,'#FFFFFF','#FFB08A')
    b+=('<text x="84" y="700" font-family="%s" font-size="76" font-weight="900" '
        'fill="#fff">ここに見出しを</text>'%FONT)
    b+=('<text x="84" y="800" font-family="%s" font-size="76" font-weight="900" '
        'fill="#FFB08A">大きく入れます</text>'%FONT)
    b+='<rect x="84" y="880" width="912" height="6" rx="3" fill="#fff" fill-opacity=".25"/>'
    for x,w in [(84,240),(360,180),(580,280),(900,96)]:
        b+='<rect x="%d" y="880" width="%d" height="6" rx="3" fill="#fff" fill-opacity=".9"/>'%(x,w)
    b+=('<text x="84" y="990" font-family="%s" font-size="36" font-weight="600" '
        'fill="#fff" fill-opacity=".85">説明文がここに入ります。</text>'%FONT)
    b+=('<text x="540" y="1800" text-anchor="middle" font-family="%s" font-size="30" '
        'font-weight="800" fill="#fff" fill-opacity=".75" letter-spacing="2">newfor.jp</text>'%FONT)
    return svg(1080,1920,b)
put('post-vertical', post_vertical())

print('SVGを %d 本 書き出しました → %s/'%(len(os.listdir(OUT)),OUT))
for f in sorted(os.listdir(OUT)): print('  ',f)
