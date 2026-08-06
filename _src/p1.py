# -*- coding: utf-8 -*-
import re, io

TOPS = ['newfor-top-light.html','newfor-top.html']

# ---------- A. CSS additions (both top pages) ----------
CSS = """
/* ============ 修正・追加（コントラスト／今週の一件／投票） ============ */
/* 選択中のタグが白背景＋白文字で消えていた不具合の修正 */
:root[data-theme="light"] .tagbar .tg.on{background:var(--accent);border-color:var(--accent);color:#fff}
:root[data-theme="light"] .aff-h .n{color:rgba(255,255,255,.78)}

/* 今週の一件：自動で次へ流れる */
.today{position:relative;padding-bottom:15px}
.today .txt{transition:opacity .26s ease,transform .26s ease}
.today .txt.out{opacity:0;transform:translateY(-5px)}
.today .tno{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:var(--tx-3);flex-shrink:0;letter-spacing:.04em}
.tprog{position:absolute;left:0;right:0;bottom:0;height:2px;overflow:hidden}
.tprog i{display:block;height:100%;width:0;background:var(--gold);opacity:.6}
@keyframes tgrow{from{width:0}to{width:100%}}
@media (prefers-reduced-motion:reduce){.tprog{display:none}}

/* 投票：もっと押したくなるように */
.vhead{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:13px}
.vwho{font-size:12px;font-weight:750;color:#fff;background:var(--accent);padding:5px 12px;border-radius:999px;letter-spacing:-.01em}
.vleft{margin-left:auto;font-family:ui-monospace,Menlo,monospace;font-size:11px;color:var(--tx-3);letter-spacing:.04em}
.vask{margin:0 0 15px;font-size:13.5px;color:var(--tx-2);line-height:1.7}
.vask b{color:var(--gold);font-weight:800}
.vask b::after{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--gold);
  margin-left:8px;vertical-align:middle;animation:vpulse 1.5s ease-in-out infinite}
@keyframes vpulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.8);opacity:.4}}
.voted .vask{display:none}
.opt{padding:19px 17px}
.opt .nm{font-size:15.5px}
.opt .arw{position:relative;margin-left:auto;font-size:15px;color:var(--gold);opacity:0;transform:translateX(-4px);transition:.18s}
.opt:hover .arw{opacity:1;transform:translateX(0)}
.voted .opt .arw{display:none}
.opt.chosen{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent-w)}
.opt .you{position:relative;display:none;font-size:11px;font-weight:750;color:#fff;background:var(--accent);
  padding:2px 8px;border-radius:999px;margin-left:8px}
.opt.chosen .you{display:inline-block}
.vthx{display:none;margin-top:15px;padding:13px 15px;border-radius:12px;background:var(--accent-w);
  font-size:13px;line-height:1.7;color:var(--tx-1)}
.vthx b{color:var(--accent);font-weight:800}
.voted .vthx{display:block}
:root[data-theme="light"] .vthx{background:rgba(90,69,224,.09)}
:root[data-theme="light"] .band.vio .vwho{background:#4A2FD6}
@media (max-width:520px){.opt{padding:17px 15px}}
"""

for f in TOPS:
    s = io.open(f, encoding='utf-8').read()
    i = s.rindex('</style>')
    s = s[:i] + CSS + s[i:]
    io.open(f,'w',encoding='utf-8').write(s)
print('A ok')
