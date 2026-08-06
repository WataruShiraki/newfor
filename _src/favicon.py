# -*- coding: utf-8 -*-
"""検索結果に出るファビコンを作り直す

Googleは「48×48、またはその倍数の正方形」を求めます。32×32だと拾われません。
実際、検索結果にNEWFORのマークが出ず、地球儀の代替アイコンになっていました。

作るもの:
  favicon.svg        … 対応ブラウザ用（いちばん綺麗）
  favicon-48.png     … Googleの最小サイズ
  favicon-96.png     … 倍数
  favicon-192.png    … Android
  favicon-512.png    … PWA
  apple-touch-icon   … iOS
  favicon.ico        … 古い環境とクローラの保険。サイトの直下に置く
"""
import io,os

BLUE='#2F3BD6'
UFO=('<path d="M10.6 16.4 L21.4 16.4 L25.8 31 L6.2 31 Z" fill="#fff" opacity=".18"/>'
 '<path d="M12.5 16.4 L19.5 16.4 L21.9 26.5 L10.1 26.5 Z" fill="#fff" opacity=".26"/>'
 '<ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="#fff"/>'
 '<path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="#fff" '
 'stroke-width="2.3" stroke-linecap="round" fill="none"/>')

# 小さく表示されるので、余白を詰めてマークを大きく見せる。
# UFOの見た目の中心は (16, 18.75)。それを正方形の中心に合わせる。
K=0.82
CX=16-16*K
CY=16-18.75*K
SVG=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">'
 '<rect width="32" height="32" rx="7" fill="%s"/>'
 '<g transform="translate(%.3f %.3f) scale(%.3f)">%s</g></svg>'%(BLUE,CX,CY,K,UFO))

os.makedirs('dist/assets',exist_ok=True)
io.open('dist/assets/favicon.svg','w',encoding='utf-8').write(SVG)

# iOS は角丸を自前で付けるので、四角いまま渡す
APPLE=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">'
 '<rect width="32" height="32" fill="%s"/>'
 '<g transform="translate(%.3f %.3f) scale(%.3f)">%s</g></svg>'%(BLUE,CX,CY,K,UFO))
io.open('dist/assets/apple.svg','w',encoding='utf-8').write(APPLE)
print('favicon.svg / apple.svg を書き出しました')
