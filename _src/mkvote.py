# -*- coding: utf-8 -*-
"""読者の投票を、ページに組み込む

やっていること

  1. vote-client.js に vote.css を流し込んで、gh/assets/vote.js を書き出す
     （見た目もJSの中。ページ側は読み込み1行だけ。広告・ピックアップと同じ考え方です）
  2. トップの投票のかたまりを、新しい「新規事業の目利き」に差し替える
  3. 全ページの <script src="/assets/vote.js?v=…"> から版番号を外す
     （版番号を付けていると、投票を1文字直すたびに全ページのHTMLが変わります）

トップの右側にあった「あなたの1票でできること」の3つの説明も、
期待度投票のための文章だったので、目利きの文章に書き換えます。
"""
import io, os, re, json, glob

JS = io.open('vote-client.js', encoding='utf-8').read()
CSS = io.open('vote.css', encoding='utf-8').read()
JS = JS.replace('__NFVCSS__', json.dumps(CSS, ensure_ascii=False))

os.makedirs('gh/assets', exist_ok=True)
io.open('gh/assets/vote.js', 'w', encoding='utf-8').write(JS)

# ── トップの投票のかたまり ──
VOTE_BLOCK = '''<!-- ══ VOTE ══ -->
<div class="band vio">
<section class="blk" id="vote">
  <div class="wrap">
    <div class="shd"><h2>読者の投票</h2><span class="sub">1日1件・ログイン不要・1タップ</span></div>
    <div class="vgrid">
      <div class="vote-slot" data-poll="daily"></div>
      <div class="vwhy">
        <h4>あなたの1票でできること</h4>
        <dl>
          <dt>挑戦している人の追い風になる</dt>
          <dd>期待度は社内を通すときの材料になります。世の中がどう見ているかは、数字にしないと伝わりません。</dd>
          <dt>否定の選択肢は置きません</dt>
          <dd>「様子見」は保留という意味です。どちらに入れても、誰かを下げることにはなりません。</dd>
          <dt>毎日ちがう1件を出します</dt>
          <dd>いちばん新しい発表から順に、1日1件。毎日いらしていただければ、毎日1票を入れられます。</dd>
        </dl>
      </div>
    </div>
  </div>
</section>
</div>'''


def swap_top():
    p = 'gh/index.html'
    s = io.open(p, encoding='utf-8').read()
    i = s.find('<!-- ══ VOTE ══ -->')
    if i < 0:
        print('  トップに投票のかたまりが見あたりません'); return
    j = s.find('<!-- ══ MISSION ══ -->', i)
    if j < 0:
        print('  投票のかたまりの終わりが分かりません'); return
    s = s[:i] + VOTE_BLOCK + '\n\n' + s[j:]

    # 出題表は、投票のJSより先に読ませる
    if '/assets/poll.js' not in s:
        s = s.replace('<script src="/assets/vote.js', '<script src="/assets/poll.js" defer></script>\n'
                                                      '<script src="/assets/vote.js', 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('  gh/index.html の投票を「新規事業の目利き」に差し替えました')


swap_top()

# ── 版番号を外す ──
n = 0
for f in sorted(glob.glob('gh/**/*.html', recursive=True)):
    if '/_src/' in f:
        continue
    s = io.open(f, encoding='utf-8').read()
    t = re.sub(r'<script src="/assets/vote\.js\?v=\d+" defer></script>',
               '<script src="/assets/vote.js" defer></script>', s)
    if t != s:
        io.open(f, 'w', encoding='utf-8').write(t); n += 1
print('  投票JSの版番号を外したページ: %d' % n)
print('-> gh/assets/vote.js  %.1fKB' % (os.path.getsize('gh/assets/vote.js') / 1024.0))
