# -*- coding: utf-8 -*-
"""ヘッダーの下に「ピックアップ」（直近の投票が流れる帯）を入れる

福利厚生JPで効果があった仕掛けを、NEWFORにも入れます。

置き方の決まり
- ページに入れるのは <script> 2行だけ。CSSも帯のHTMLも assets/pickup.js の中にあります
- 以前は全ページにCSSとHTMLを焼き込んでいたため、見た目を1文字直すだけで
  58ファイルを上げ直す必要がありました。触る場所は1本にします
- 何度実行しても二重には入りません

出すもの
- Supabase の newfor_recent_votes ビュー（3日ぶん・1時間単位に丸め済み）
- 投票がまだ無いとき、通信できないときは、帯ごと出しません。空の帯は出しません
"""
import io,os,re,glob,json,sys,importlib,hashlib

sys.path.insert(0,'articles')

# ── 記事スラッグ → 表示名の対応表を作る ──
MAP={}
for f in sorted(glob.glob('articles/a0*.py')):
    A=importlib.import_module(os.path.basename(f)[:-3]).A
    MAP[A['slug']]=dict(name=A.get('company') or 'NEWFOR',
                        url='/articles/%s/'%A['slug'])

# ── 今週の投票（weekly）には記事がない ──
#
# 「NEWFOR の記事に」と出てしまい、掲載企業の名前が消えていました。
# 投票の問い（question）の中から企業名を拾って、その企業ページへ送ります。
# 「NTTドコモ」は問いの中では「ドコモ」と書かれるので、短い呼び名も持ちます。
sys.path.insert(0,'companies')
CO=[]
for f in sorted(glob.glob('companies/*.py')):
    n=os.path.basename(f)[:-3]
    if n.startswith('_'): continue
    c=importlib.import_module(n).C
    keys=[c['name']]
    for cut in ('NTT','株式会社'):
        if c['name'].startswith(cut) and len(c['name'])>len(cut)+1:
            keys.append(c['name'][len(cut):])
    for cut in ('グループ','ホールディングス','自動車','工業','商事','重工業'):
        if c['name'].endswith(cut) and len(c['name'])>len(cut)+1:
            keys.append(c['name'][:-len(cut)])
    # 長い呼び名から先に照合する（「三菱商事」より先に「三菱」を当てない）
    CO.append(dict(name=c['name'],url='/companies/%s/'%c['slug'],
                   keys=sorted(set(keys),key=len,reverse=True)))

io.open('gh/assets/pickup-map.js','w',encoding='utf-8').write(
    '/* pickup.py が articles/ と companies/ から作ります。手で書かないでください */\n'
    'window.NF_PICKUP_MAP=%s;\n'
    'window.NF_PICKUP_CO=%s;\n'
    %(json.dumps(MAP,ensure_ascii=False,separators=(',',':')),
      json.dumps(CO,ensure_ascii=False,separators=(',',':'))))

# ── 帯のCSS。JSの中に持たせて、ページには入れない ──
CSSTEXT = "/* ピックアップの帯。ヘッダーのすぐ下に置きます。\n   ここは「人の気配」を出す場所なので、青ではなく差し色のオレンジで拾わせます。 */\n/* 帯の色は画面いっぱい。中身はそのページの .wrap と同じ幅にそろえる。\n   （ページごとに 1240px / 1180px / 760px と違うので、.wrap をそのまま借ります） */\n#nf-pickup{position:relative;overflow:hidden;\n background:linear-gradient(90deg,#FFF1E4 0%,#FFF7F0 60%,#FFF1E4 100%);\n border-bottom:1px solid rgba(224,74,12,.22);font-size:12.5px;line-height:1}\n#nf-pickup .nf-pk-in{display:flex;align-items:center;gap:12px;height:40px;\n flex-wrap:nowrap;min-height:0}\n#nf-pickup .nf-pk-tag{flex:0 0 auto;display:inline-flex;align-items:center;gap:6px;\n background:#E04A0C;color:#fff;font-weight:800;font-size:10.5px;\n letter-spacing:.12em;padding:6px 10px;border-radius:6px;box-shadow:0 1px 0 rgba(0,0,0,.06)}\n#nf-pickup .nf-pk-tag i{width:6px;height:6px;border-radius:50%;background:#fff;\n animation:nf-pk-blink 1.6s ease-in-out infinite}\n@keyframes nf-pk-blink{0%,100%{opacity:1}50%{opacity:.25}}\n#nf-pickup .nf-pk-win{position:relative;flex:1 1 auto;overflow:hidden;height:100%;\n -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 24px,#000 calc(100% - 44px),transparent 100%);\n mask-image:linear-gradient(90deg,transparent 0,#000 24px,#000 calc(100% - 44px),transparent 100%)}\n#nf-pickup .nf-pk-track{display:flex;align-items:center;height:100%;width:max-content;\n animation:nf-pk-flow 40s linear infinite}\n#nf-pickup:hover .nf-pk-track{animation-play-state:paused}\n#nf-pickup .nf-pk-item{display:inline-flex;align-items:center;gap:8px;padding:0 20px;\n white-space:nowrap;text-decoration:none;color:#5A5368;border-radius:6px}\n/* カーソルを乗せたら、その1件まるごとに線を引く */\n#nf-pickup .nf-pk-item:hover{text-decoration:underline;text-decoration-color:rgba(224,74,12,.5);\n text-underline-offset:4px;text-decoration-thickness:1.5px;color:#2A2439}\n#nf-pickup .nf-pk-d{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#B0A79E;\n border:1px solid rgba(224,74,12,.2);border-radius:4px;padding:2px 5px}\n#nf-pickup .nf-pk-w{color:#E04A0C;font-weight:800}\n#nf-pickup .nf-pk-t b{font-weight:700;color:#2A2439}\n#nf-pickup .nf-pk-n{background:#E04A0C;color:#fff;font-weight:800;font-size:10px;\n border-radius:9px;padding:2px 7px}\n/* 左から右へ流す。うしろに同じ並びをもう一組置いてあるので、\n   -w から 0 へ動かすと、切れ目なく右へ流れ続けます */\n@keyframes nf-pk-flow{from{transform:translateX(calc(var(--nf-pk-w,1000px) * -1))}to{transform:translateX(0)}}\n@media (prefers-reduced-motion:reduce){\n  #nf-pickup .nf-pk-track{animation:none}\n  #nf-pickup .nf-pk-tag i{animation:none}\n  #nf-pickup .nf-pk-win{overflow-x:auto}\n}\nhtml[data-theme=\"dark\"] #nf-pickup,\n[data-theme=\"dark\"] #nf-pickup{background:#1B1526;border-bottom-color:rgba(255,138,69,.22)}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-item{color:#B6ADBF}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-item:hover{color:#F2ECF7}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-w{color:#FF8A45}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-t b{color:#EDE7F2}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-d{color:#8C8397;border-color:rgba(255,138,69,.24)}\n@media (max-width:640px){#nf-pickup{font-size:11.5px}\n  #nf-pickup .nf-pk-in{height:36px;gap:8px}\n  #nf-pickup .nf-pk-tag{font-size:9.5px;padding:5px 8px}\n  #nf-pickup .nf-pk-item{padding:0 14px;gap:6px}}"

JS = "/* ============================================================\n   NEWFOR ピックアップ（ヘッダー下を流れる、直近3日の投票）\n\n   読むのは newfor_recent_votes ビューだけです。\n   投票が無いとき・通信できないときは、帯ごと消します（空の帯は出さない）。\n   ============================================================ */\n(function () {\n  \"use strict\";\n  var NF_CSS = __NFCSS__;\n  var URL_ = \"https://jakwntemjkwqwaqujffh.supabase.co/rest/v1\";\n  var KEY  = \"sb_publishable_bQ84WCmRiFUbpPemMcO9xQ_Dj9Mh1mQ\";\n  /* 帯そのものを、ここで作ってヘッダーの下に差し込みます。\n     以前はCSSとHTMLを全ページに焼き込んでいたため、見た目を1文字直すだけで\n     58ファイルを上げ直す必要がありました。触る場所は、このファイル1本だけにします。 */\n  var header = document.querySelector(\"header\");\n  if (!header) return;\n  if (!document.getElementById(\"nf-pickup-css\")) {\n    var st = document.createElement(\"style\");\n    st.id = \"nf-pickup-css\";\n    st.textContent = NF_CSS;\n    document.head.appendChild(st);\n  }\n  var band = document.createElement(\"div\");\n  band.id = \"nf-pickup\";\n  band.hidden = true;\n  band.setAttribute(\"aria-label\", \"直近の投票\");\n  band.innerHTML = '<div class=\"wrap nf-pk-in\">' +\n    '<span class=\"nf-pk-tag\"><i></i>PICKUP</span>' +\n    '<div class=\"nf-pk-win\"><div class=\"nf-pk-track\"></div></div></div>';\n  header.parentNode.insertBefore(band, header.nextSibling);\n  var track = band.querySelector(\".nf-pk-track\");\n  var MAP = window.NF_PICKUP_MAP || {};\n\n  function die() { band.remove(); }\n\n  function md(iso) {                       /* 2026-08-05T10:00:00Z → 08-05 */\n    var d = new Date(iso);\n    if (isNaN(d)) return \"\";\n    var m = (\"0\" + (d.getMonth() + 1)).slice(-2), day = (\"0\" + d.getDate()).slice(-2);\n    return m + \"-\" + day;\n  }\n\n  var CO = window.NF_PICKUP_CO || [];\n\n  /* 今週の投票は、問いの文から掲載企業を拾う。見つからなければ企業名は出さない */\n  function fromQuestion(q) {\n    q = q || \"\";\n    var best = null;\n    CO.forEach(function (c) {\n      c.keys.forEach(function (k) {\n        if (q.indexOf(k) >= 0 && (!best || k.length > best.len)) best = { c: c, len: k.length };\n      });\n    });\n    return best ? best.c : null;\n  }\n\n  function line(r) {\n    var id = String(r.poll_id || \"\");\n    var n = Number(r.votes || 0);\n    var who, href;\n    if (id.indexOf(\"weekly-\") === 0) {\n      var c = fromQuestion(r.question);\n      who = c ? c.name : \"今週の投票\";\n      href = c ? c.url : \"/#vote\";\n    } else {\n      var m = MAP[id.replace(/^reaction-/, \"\")];\n      who = m ? m.name : \"NEWFOR\";\n      href = m ? m.url : \"/articles/\";\n    }\n    var a = document.createElement(\"a\");\n    a.className = \"nf-pk-item\";\n    a.href = href;\n    a.innerHTML = '<span class=\"nf-pk-d\">' + md(r.at) + '</span>' +\n                  '<span class=\"nf-pk-w\">' + who + '</span>' +\n                  '<span class=\"nf-pk-t\">に<b>「' + (r.label || \"\") + '」</b>が投票されました</span>' +\n                  (n > 1 ? '<span class=\"nf-pk-n\">' + n + '</span>' : '');\n    return a;\n  }\n\n  fetch(URL_ + \"/newfor_recent_votes?order=at.desc&limit=24\", {\n    headers: { apikey: KEY, Authorization: \"Bearer \" + KEY }\n  })\n  .then(function (r) { if (!r.ok) throw new Error(\"supabase \" + r.status); return r.json(); })\n  .then(function (rows) {\n    rows = (rows || []).filter(function (r) { return r.poll_id && r.label; });\n    if (!rows.length) return die();\n\n    var items = rows.map(line);\n    items.forEach(function (a) { track.appendChild(a); });\n\n    /* 流れが途切れないよう、同じ並びをもう一組うしろに足す */\n    items.forEach(function (a) { track.appendChild(a.cloneNode(true)); });\n\n    /* 先に見えるようにしてから測る。\n       隠れたままだと scrollWidth が 0 になり、動かない帯になります（実際になりました）。 */\n    band.hidden = false;\n    var w = track.scrollWidth / 2;\n    track.style.setProperty(\"--nf-pk-w\", w + \"px\");\n    track.style.animationDuration = Math.max(18, Math.round(w / 60)) + \"s\";\n  })\n  .catch(function (e) { console.warn(\"[NEWFOR pickup]\", e); die(); });\n})();\n"
JS = JS.replace('__NFCSS__', json.dumps(CSSTEXT, ensure_ascii=False))
io.open('gh/assets/pickup.js','w',encoding='utf-8').write(JS)
VER = hashlib.md5(JS.encode('utf-8')).hexdigest()[:8]

# ── ページに入れるのは、この2行だけ ──
BAND = ('\n<script src="/assets/pickup-map.js" defer></script>\n'
        '<script src="/assets/pickup.js?v=%s" defer></script>\n'%VER)

n=0
for f in sorted(set(glob.glob('gh/**/*.html',recursive=True))):
    if '/_src/' in f: continue
    s=io.open(f,encoding='utf-8').read()
    if '</header>' not in s: continue
    # 古い形（CSSと帯のHTMLを焼き込んでいたもの）も、新しい形も、いったん外す
    s=re.sub(r'\n?<style id="nf-pickup-css">.*?<script src="/assets/pickup\.js[^"]*" defer></script>\n?','',s,flags=re.S)
    s=re.sub(r'\n?<script src="/assets/pickup-map\.js" defer></script>\s*<script src="/assets/pickup\.js[^"]*" defer></script>\n?','',s,flags=re.S)
    i=s.find('</header>')+len('</header>')
    s=s[:i]+BAND+s[i:]
    io.open(f,'w',encoding='utf-8').write(s); n+=1
print('ピックアップを %d ページへ入れました（ページに入るのは<script>2行だけ）'%n)
