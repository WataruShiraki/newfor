# -*- coding: utf-8 -*-
import io,os
os.makedirs('dist/assets',exist_ok=True)

UFO = ('<path d="M10.6 16.4 L21.4 16.4 L25.8 31 L6.2 31 Z" fill="{c}" opacity=".16"/>'
 '<path d="M12.5 16.4 L19.5 16.4 L21.9 26.5 L10.1 26.5 Z" fill="{c}" opacity=".24"/>'
 '<ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="{c}"/>'
 '<path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="{c}" stroke-width="2.3" stroke-linecap="round" fill="none"/>')

# favicon.svg : 角丸の青地に白抜きUFO
fav = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">'
 '<rect width="32" height="32" rx="7" fill="#2F3BD6"/>'
 '<g transform="translate(16 16.6) scale(.80) translate(-16 -16)">'+UFO.format(c='#ffffff')+'</g>'
 '</svg>')
io.open('dist/assets/favicon.svg','w',encoding='utf-8').write(fav)

# maskable / apple touch 用の大きめ SVG（余白多め）
apple = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180" width="180" height="180">'
 '<rect width="180" height="180" rx="0" fill="#2F3BD6"/>'
 '<g transform="translate(90 94) scale(4.1) translate(-16 -16)">'+UFO.format(c='#ffffff')+'</g>'
 '</svg>')
io.open('dist/assets/apple.svg','w',encoding='utf-8').write(apple)
print('svg ok')
