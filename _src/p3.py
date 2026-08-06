# -*- coding: utf-8 -*-
import io
TOPS=['newfor-top-light.html','newfor-top.html']

OLD_VOTE='''      <div class="vote" id="voteCard">
        <p class="q">ドコモが2026年夏に出すAIエージェント「SyncMe」。あなたの期待度は？</p>
        <div class="opts">
          <button class="opt a" data-k="a"><span class="fill"></span>
            <span class="top"><span class="em">🚀</span><span class="nm">めちゃくちゃ期待！</span><span class="pct" data-p></span></span></button>
          <button class="opt b" data-k="b"><span class="fill"></span>
            <span class="top"><span class="em">👀</span><span class="nm">今は様子見！</span><span class="pct" data-p></span></span></button>
        </div>
        <div class="vfoot"><span id="vcount"></span><span class="ok">✓ 受け付けました</span></div>
      </div>'''

NEW_VOTE='''      <div class="vote" id="voteCard">
        <div class="vhead">
          <span class="vwho">新規事業に取り組んでいる、あなたへ</span>
          <span class="vleft">今週の投票　あと3日</span>
        </div>
        <p class="q">ドコモが2026年夏に出すAIエージェント「SyncMe」。あなたの期待度は？</p>
        <p class="vask">1タップで、この事業を応援できます。ログインもメールも要りません。<b>今すぐ投票！</b></p>
        <div class="opts">
          <button class="opt a" data-k="a"><span class="fill"></span>
            <span class="top"><span class="em">🚀</span><span class="nm">めちゃくちゃ期待！</span><span class="you">あなた</span><span class="arw">→</span><span class="pct" data-p></span></span></button>
          <button class="opt b" data-k="b"><span class="fill"></span>
            <span class="top"><span class="em">👀</span><span class="nm">今は様子見！</span><span class="you">あなた</span><span class="arw">→</span><span class="pct" data-p></span></span></button>
        </div>
        <div class="vfoot"><span id="vcount"></span><span class="ok">✓ 受け付けました</span></div>
        <div class="vthx">ありがとうございます。<b>あなたの1票が、この事業への応援になりました。</b>結果は毎週月曜に更新して、記事の中でも紹介します。</div>
      </div>'''

OLD_WHY='''        <h4>期待度とは</h4>
        <dl>
          <dt>読者の8割が新規事業の当事者</dt>
          <dd>だから期待度は、そのまま人が集まるかの指標になります。</dd>
          <dt>否定の選択肢は置かない</dt>
          <dd>「様子見」は保留。企業を傷つけません。</dd>
          <dt>公開情報からは作れない</dt>
          <dd>NEWFORにしかない数字です。</dd>
        </dl>'''
NEW_WHY='''        <h4>あなたの1票でできること</h4>
        <dl>
          <dt>挑戦している人の追い風になる</dt>
          <dd>期待度は社内を通すときの材料になります。世の中がどう見ているかは、数字にしないと伝わりません。</dd>
          <dt>否定の選択肢は置きません</dt>
          <dd>「様子見」は保留という意味です。どちらに入れても、誰かを下げることにはなりません。</dd>
          <dt>読者の8割が新規事業の当事者</dt>
          <dd>だからこの数字は、公開情報からは作れません。NEWFORにしかない、あなたたちの声です。</dd>
        </dl>'''

OLD_VC='''  document.getElementById("vcount").textContent=hasVoted
    ?"期待度 "+Math.round(votes.a/t*100)+"%　"+t.toLocaleString()+"ユーザーが投票"
    :t.toLocaleString()+"ユーザーが投票済み　タップで結果を表示";'''
NEW_VC='''  document.getElementById("vcount").textContent=hasVoted
    ?"期待度 "+Math.round(votes.a/t*100)+"%　あなたを含む "+t.toLocaleString()+"ユーザーが応援"
    :"すでに "+t.toLocaleString()+"ユーザーが応援しています　1タップで結果も見られます";'''

OLD_M1='''成功だけが語り継がれ、その手前の試行錯誤は残らない。'''
OLD_M2='''だから毎回、ゼロから始めることになる。'''

for f in TOPS:
    s=io.open(f,encoding='utf-8').read()
    for o,n in [(OLD_VOTE,NEW_VOTE),(OLD_WHY,NEW_WHY),(OLD_VC,NEW_VC)]:
        assert o in s, f+' :: '+o[:40]
        s=s.replace(o,n)
    assert OLD_M1 in s and OLD_M2 in s, f+' mission'
    s=s.replace(OLD_M1,'本気の挑戦には、それだけで価値がある。')
    s=s.replace(OLD_M2,'成功した事業だけが語り継がれて、その手前の試行錯誤が残らないのは、もったいない。')
    io.open(f,'w',encoding='utf-8').write(s)
    print(f,'C/D ok')
