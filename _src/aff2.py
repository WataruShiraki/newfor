# -*- coding: utf-8 -*-
import io

FILES=['newfor-top-light.html','newfor-top.html','newfor-companies.html','newfor-company-kddi.html','newfor-site.html']

JS = r'''
/* ===== アフィリエイト枠：読者タイプ別に出し分ける ===== */
(function(){
var ARROW='<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7M9 7h8v8"/></svg>';
var G={
 job:{tab:"転職・採用",title:"新規事業に強い採用サービス BEST 3",
   who:"新規事業のポジションを探している方へ",cta:"無料登録へ",
   items:[
    {n:"ビズリーチ",best:1,d:"新規事業責任者・事業開発ポジションの掲載が多い。大企業の非公開求人が中心。",t:["ハイクラス","スカウト型","年収600万〜"]},
    {n:"フォースタートアップス",d:"スタートアップ・成長企業に特化。大企業からの越境転職の支援実績が多い。",t:["スタートアップ","エージェント型","CxO・事業責任者"]},
    {n:"doda X",d:"ヘッドハンター経由のスカウト。事業会社の新規事業部門からの声がかかりやすい。",t:["ハイクラス","ヘッドハンター","年収800万〜"]}
   ]},
 pro:{tab:"顧問・プロ人材",title:"新規事業の顧問・プロ人材が探せるサービス BEST 3",
   who:"社内に足りない知見を、外から借りたい方へ",cta:"相談してみる",
   items:[
    {n:"サーキュレーション（プロシェアリング）",best:1,d:"事業開発の実務経験者に、月数日から入ってもらう形。立ち上げの伴走で使われることが多い。",t:["プロシェアリング","月数日〜","事業開発"]},
    {n:"ビザスク",d:"1時間から有識者に話を聞ける。市場を調べる段階や、仮説をぶつけたい初期に向く。",t:["スポット相談","1時間〜","リサーチ"]},
    {n:"HiPro Biz",d:"経営顧問・プロ人材の紹介。大企業の新規事業部門でのプロジェクト単位の活用が中心。",t:["経営顧問","プロジェクト型","大企業"]}
   ]},
 learn:{tab:"学ぶ",title:"新規事業の学びに使えるサービス",
   who:"新規事業の担当になったばかりの方へ",cta:"無料で試す",
   items:[
    {n:"グロービス学び放題",best:1,d:"事業開発・マーケ・ファイナンスを動画で。担当になった最初の3カ月の土台づくりに。",t:["動画学習","定額","ビジネス基礎"]},
    {n:"flier（フライヤー）",d:"ビジネス書の要約。記事の参考文献を、読む前にあたりをつけたいときに。",t:["書籍要約","10分","定額"]},
    {n:"クラウドワークス",d:"検証フェーズの手を借りる。リサーチ、LP制作、資料づくりを外に出せる。",t:["外部リソース","単発","検証フェーズ"]}
   ]},
 biz:{tab:"別会社で始める",title:"別会社で始めるときに使うサービス",
   who:"出向起業・カーブアウト・独立で、自分の会社をつくる方へ",cta:"詳しく見る",
   items:[
    {n:"officee",best:1,d:"オフィス・レンタルオフィスの仲介。数人のチームで始めるときの拠点探しから。",t:["拠点","仲介無料","小規模〜"]},
    {n:"ラクスルバンク",d:"法人口座。会社をつくったら最初に必要になるもの。オンラインで完結。",t:["法人口座","ネット銀行","開設無料"]},
    {n:"GMOオフィスサポート",d:"バーチャルオフィス。登記できる住所だけ先に押さえたいときに。",t:["登記可","月額制","住所のみ"]},
    {n:"freee会計",d:"設立直後の経理。クレジットカードや口座と繋いで、記帳を止めない。",t:["クラウド会計","法人向け","無料期間あり"]}
   ]}
};
var ORDER=["job","pro","learn","biz"];

function rows(k){
  return G[k].items.map(function(it,i){
    return '<div class="aff-r'+(i===0?' top':'')+'">'
      +'<span class="rk">'+(i+1)+'</span><span>'
      +'<span class="nm">'+it.n+(it.best?' <span class="best">マニアのおすすめ</span>':'')+'</span>'
      +'<span class="ds">'+it.d+'</span>'
      +'<span class="tg2">'+it.t.map(function(x){return '<span>'+x+'</span>'}).join('')+'</span>'
      +'</span>'
      +'<a class="btn-a" href="#aff" rel="nofollow sponsored">'+G[k].cta+ARROW+'</a></div>';
  }).join('');
}
function build(el){
  var def=el.getAttribute("data-aff")||"job";
  var html='<div class="aff"><div class="aff-h"><span class="pr">広告</span>'
   +'<span class="t"></span><span class="aff-tab">'
   +ORDER.map(function(k){return '<button data-af="'+k+'"'+(k===def?' class="on"':'')+'>'+G[k].tab+'</button>'}).join('')
   +'</span></div><div class="aff-who"></div>'
   +ORDER.map(function(k){return '<div class="aff-pane" data-af="'+k+'"'+(k===def?'':' hidden')+'>'+rows(k)+'</div>'}).join('')
   +'<div class="aff-f">本枠は広告（アフィリエイトプログラムを含みます）。順位は筆者が新規事業関連の求人・支援実績の傾向をもとに決めており、報酬額では変えません。</div></div>';
  el.innerHTML=html;
  var box=el.querySelector(".aff"),ttl=box.querySelector(".aff-h .t"),who=box.querySelector(".aff-who");
  function set(k){
    ttl.textContent=G[k].title; who.textContent=G[k].who;
    Array.prototype.forEach.call(box.querySelectorAll(".aff-tab button"),function(x){x.classList.toggle("on",x.getAttribute("data-af")===k)});
    Array.prototype.forEach.call(box.querySelectorAll(".aff-pane"),function(p){p.hidden=p.getAttribute("data-af")!==k});
  }
  Array.prototype.forEach.call(box.querySelectorAll(".aff-tab button"),function(b){
    b.addEventListener("click",function(){set(b.getAttribute("data-af"))});
  });
  set(def);
}
function buildMini(el){
  var k=el.getAttribute("data-aff")||"pro",it=G[k].items[0];
  el.innerHTML='<div class="affmini"><span class="pr">広告</span>'
   +'<span class="bd"><span class="nm">'+it.n+'</span><span class="ds">'+it.d+'</span></span>'
   +'<a class="btn-a" href="#aff" rel="nofollow sponsored">'+G[k].cta+ARROW+'</a></div>';
}
Array.prototype.forEach.call(document.querySelectorAll(".affslot"),build);
Array.prototype.forEach.call(document.querySelectorAll(".affmini-slot"),buildMini);
})();
'''

CSS = '''
/* アフィリエイト枠の追加スタイル */
.aff-who{padding:11px 20px;font-size:12.5px;color:var(--tx-2);background:var(--surface-2);
  border-bottom:1px solid var(--border);font-weight:650}
:root[data-theme="light"] .aff-who{background:rgba(47,59,214,.06);color:#2A2266}
.affmini{display:flex;align-items:center;gap:15px;border:1px solid var(--border);border-radius:14px;
  background:var(--surface);padding:14px 17px;box-shadow:var(--sh);margin:30px 0}
.affmini .pr{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.12em;color:var(--tx-3);
  border:1px solid var(--border-2);border-radius:5px;padding:2px 6px;flex-shrink:0;align-self:flex-start;margin-top:2px}
.affmini .bd{flex:1;min-width:0}
.affmini .nm{display:block;font-weight:750;font-size:14.5px;letter-spacing:-.015em}
.affmini .ds{display:block;font-size:12.5px;color:var(--tx-2);margin-top:3px;line-height:1.7}
.affmini .btn-a{flex-shrink:0;display:inline-flex;align-items:center;gap:6px;padding:10px 16px;border-radius:10px;
  font-size:13px;font-weight:700;white-space:nowrap}
@media (max-width:640px){.affmini{flex-wrap:wrap;gap:10px}.affmini .btn-a{width:100%;justify-content:center}}
:root[data-theme="light"] .affmini{border-color:rgba(47,59,214,.2)}
'''

for f in FILES:
    s=io.open(f,encoding='utf-8').read()
    i=s.rindex('</style>'); s=s[:i]+CSS+s[i:]
    j=s.rindex('</script>'); s=s[:j]+JS+s[j:]
    io.open(f,'w',encoding='utf-8').write(s)
    print(f,'ok')
