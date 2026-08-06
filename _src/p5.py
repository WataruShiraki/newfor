# -*- coding: utf-8 -*-
import io
ALL=['newfor-top-light.html','newfor-top.html','newfor-companies.html','newfor-company-kddi.html','newfor-site.html']

FIX = '''
/* ============ コントラスト是正（ライト／ダーク両方） ============ */
/* 補助テキストと数値をもう少し濃く（薄く）する */
:root[data-theme="light"]{--tx-3:#5E5A76; --gold:#D2440B; --live:#177A24; --ended:#A63B32}
:root[data-theme="dark"]{--tx-3:#95959F}

/* ダーク：淡い紫の面に白文字は読みにくいので、面の上は濃い文字にする */
:root[data-theme="dark"] .mini,
:root[data-theme="dark"] .btn,
:root[data-theme="dark"] .btn-a,
:root[data-theme="dark"] .vwho,
:root[data-theme="dark"] .opt .you,
:root[data-theme="dark"] .tg.on{color:#140E28}
:root[data-theme="dark"] .mini svg,
:root[data-theme="dark"] .btn svg,
:root[data-theme="dark"] .btn-a svg{color:#140E28}
:root[data-theme="dark"] .btn.ghost{color:var(--tx-1)}

/* 広告枠のヘッダーは全ページで紫に統一（白文字が浮くのを防ぐ） */
:root[data-theme="light"] .aff{border-color:rgba(74,47,214,.22)}
:root[data-theme="light"] .aff-h{background:#4A2FD6;border-bottom-color:transparent}
:root[data-theme="light"] .aff-h .t{color:#fff}
:root[data-theme="light"] .aff-h .pr{color:#fff;border-color:rgba(255,255,255,.45)}
:root[data-theme="light"] .aff-h .n{color:rgba(255,255,255,.8)}
:root[data-theme="light"] .aff-h .aff-tab{background:rgba(255,255,255,.2)}
:root[data-theme="light"] .aff-h .aff-tab button{color:#fff}
:root[data-theme="light"] .aff-h .aff-tab button.on{background:#fff;color:#3A21BE;box-shadow:none}

/* 細かい文字の色 */
.aff .best{color:#fff;background:var(--gold)}
:root[data-theme="dark"] .aff .best{color:#1A0C04}
.sample{color:var(--tx-2)}
.st.live,.badge.live{color:var(--live)}
.ds{color:var(--tx-2)}
.cap,.rk-note,.legal,.aff-f,.note{color:var(--tx-2)}
'''
for f in ALL:
    s=io.open(f,encoding='utf-8').read()
    i=s.rindex('</style>'); s=s[:i]+FIX+s[i:]
    io.open(f,'w',encoding='utf-8').write(s)
print('fix ok')
