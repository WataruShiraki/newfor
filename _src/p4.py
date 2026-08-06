# -*- coding: utf-8 -*-
import io,re
FILES=['newfor-top-light.html','newfor-top.html','newfor-site.html','newfor-company-kddi.html']

CSS='''
/* アフィリエイト：採用／顧問・プロ人材の2枠 */
.aff-tab{display:flex;gap:3px;margin-left:auto;background:rgba(127,127,140,.14);padding:3px;border-radius:10px}
.aff-tab button{border:0;background:transparent;color:var(--tx-2);cursor:pointer;font:inherit;font-size:12px;
  font-weight:650;padding:6px 12px;border-radius:8px;white-space:nowrap}
.aff-tab button.on{background:var(--surface);color:var(--tx-1);box-shadow:var(--sh)}
.aff-h .n{display:none}
:root[data-theme="light"] .aff-h .aff-tab{background:rgba(255,255,255,.2)}
:root[data-theme="light"] .aff-h .aff-tab button{color:rgba(255,255,255,.82)}
:root[data-theme="light"] .aff-h .aff-tab button.on{background:#fff;color:#3A21BE;box-shadow:none}
.aff-pane[hidden]{display:none}
@media (max-width:560px){.aff-tab{margin-left:0;width:100%}.aff-tab button{flex:1}}
'''

PRO = '''      <div class="aff-pane" data-af="pro" hidden>
      <div class="aff-r top">
        <span class="rk">1</span>
        <span>
          <span class="nm">サーキュレーション（プロシェアリング） <span class="best">マニアのおすすめ</span></span>
          <span class="ds">事業開発の実務経験者に、月数日から入ってもらう形。立ち上げの伴走で使われることが多い。</span>
          <span class="tg2"><span>プロシェアリング</span><span>月数日〜</span><span>事業開発</span></span>
        </span>
        <a class="btn-a" href="#aff" rel="nofollow sponsored">相談してみる
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7M9 7h8v8"/></svg></a>
      </div>
      <div class="aff-r">
        <span class="rk">2</span>
        <span>
          <span class="nm">ビザスク</span>
          <span class="ds">1時間から有識者に話を聞ける。市場を調べる段階や、仮説をぶつけたい初期に向く。</span>
          <span class="tg2"><span>スポット相談</span><span>1時間〜</span><span>リサーチ</span></span>
        </span>
        <a class="btn-a" href="#aff" rel="nofollow sponsored">相談してみる
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7M9 7h8v8"/></svg></a>
      </div>
      <div class="aff-r">
        <span class="rk">3</span>
        <span>
          <span class="nm">HiPro Biz</span>
          <span class="ds">経営顧問・プロ人材の紹介。大企業の新規事業部門でのプロジェクト単位の活用が中心。</span>
          <span class="tg2"><span>経営顧問</span><span>プロジェクト型</span><span>大企業</span></span>
        </span>
        <a class="btn-a" href="#aff" rel="nofollow sponsored">相談してみる
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7M9 7h8v8"/></svg></a>
      </div>
      </div>
'''

JS = '''
/* アフィリエイト枠のタブ */
(function(){
  var T={job:"新規事業に強い採用サービス BEST 3",pro:"新規事業の顧問・プロ人材が探せるサービス BEST 3"};
  Array.prototype.forEach.call(document.querySelectorAll(".aff"),function(box){
    var ttl=box.querySelector(".aff-h .t");
    Array.prototype.forEach.call(box.querySelectorAll(".aff-tab button"),function(b){
      b.addEventListener("click",function(){
        var k=b.getAttribute("data-af");
        Array.prototype.forEach.call(box.querySelectorAll(".aff-tab button"),function(x){x.classList.toggle("on",x===b);});
        Array.prototype.forEach.call(box.querySelectorAll(".aff-pane"),function(p){p.hidden=p.getAttribute("data-af")!==k;});
        if(ttl)ttl.textContent=T[k];
      });
    });
  });
})();
'''

for f in FILES:
    s=io.open(f,encoding='utf-8').read()
    # header: add tabs
    old_h = '''        <span class="t">新規事業に強い採用サービス BEST 3</span>
        <span class="n">2026年7月時点</span>
      </div>'''
    assert old_h in s, f+' affh'
    new_h = '''        <span class="t">新規事業に強い採用サービス BEST 3</span>
        <span class="aff-tab">
          <button class="on" data-af="job">採用</button>
          <button data-af="pro">顧問・プロ人材</button>
        </span>
      </div>
      <div class="aff-pane" data-af="job">'''
    s=s.replace(old_h,new_h)
    # close job pane before aff-f
    old_f = '      <div class="aff-f">'
    assert old_f in s, f+' afff'
    s=s.replace(old_f, '      </div>\n'+PRO+old_f, 1)
    # footer note
    s=s.replace('本枠は広告（アフィリエイトプログラム）を含みます。順位は筆者が新規事業関連求人の掲載傾向をもとに決めており、報酬額では変えません。',
                '本枠は広告（アフィリエイトプログラム）を含みます。順位は筆者が新規事業関連の求人・支援実績の傾向をもとに決めており、報酬額では変えません。')
    # css + js
    i=s.rindex('</style>'); s=s[:i]+CSS+s[i:]
    j=s.rindex('</script>'); s=s[:j]+JS+s[j:]
    io.open(f,'w',encoding='utf-8').write(s)
    print(f,'aff ok')
