
/* ============================================================
   NEWFOR 広告枠

   【2026-09-01 作り直し】
   わたるさんの指示:
   > 「福利厚生JPとかOFFICELOVERSみたいなバナーを出す方がいいにきまってんだろ」

   これまではテキストのボタンだけを並べていて、バナー画像を1枚も
   使っていませんでした。A8でNEWFOR用（サイトID 003）に発行した
   バナーに差し替えます。

   ■ 数え方について、ここに書いておきます

   A8のクリックは px.a8.net のURLが読み込まれた回数、
   表示（imp）はバナー画像と1×1画像が読み込まれた回数で数えられます。
   人が押したかどうかは見ていません。だから次の3つを守ります。

     1. ひとつの枠から出すバナーは、必ず1枚だけ。
        PC用とスマホ用を両方出して、片方をCSSで隠すことはしません。
        隠しても画像の読み込みは起きるので、表示回数が二重になります。
        （福利厚生JPで実際に起きました）
        ここはJavaScriptで作っているので、画面の幅を見てから
        1枚だけ選べます。

     2. バナーと1×1画像は、枠が画面に入ったときに同時に入れます。
        片方だけ先に読ませない。1枠 ＝ バナー1回 ＝ 1×1画像1回。

     3. リンクのURLはページのHTMLに書かず、このJavaScriptの中で
        組み立てます。HTMLに直接書くと、巡回ロボットがリンクを
        たどってクリックとして数えられます。

   見た目のCSSもここから入れます。トップと企業DBは手書きHTMLで、
   ページ側のCSSに新しい書き方が入っていないためです。
   ============================================================ */
var A = {"biz":{"items":[{"n":"会社設立の無料相談（経営サポートプラスアルファ）","mat":"4B9ZDA+B4OSG2+5LH2+5YZ75","lead":"会社にするか、個人のまま進むか。決める前に、税理士に無料で聞けます。","sq":{"s":"www28.a8.net","a":"260806222673","e":"01","m":"s00000026111001003000","w":300,"h":250,"t":"4B9ZDA+B4OSG2+5LH2+5YZ75","p":"www15.a8.net"},"wide":null},{"n":"弥生の起業支援サービス【起業・開業ナビ】","mat":"4BA2HC+10BI82+35XE+HWPVL","lead":"開業届、青色申告、屋号。起業のときの事務を、順番に片づけます。","sq":{"s":"www22.a8.net","a":"260810256061","e":"01","m":"s00000014765003008000","w":300,"h":250,"t":"4BA2HC+10BI82+35XE+HWPVL","p":"www14.a8.net"},"wide":null},{"n":"バーチャルオフィス1","mat":"4B9ZDA+9JJ6DE+5A2I+5ZEMP","lead":"登記に使う住所を、自宅にするかどうか。先に決めておきたいところです。","sq":{"s":"www26.a8.net","a":"260806222577","e":"01","m":"s00000024633001005000","w":300,"h":250,"t":"4B9ZDA+9JJ6DE+5A2I+5ZEMP","p":"www12.a8.net"},"wide":{"s":"www21.a8.net","a":"260806222577","e":"01","m":"s00000024633001007000","w":728,"h":90,"t":"4B9ZDA+9JJ6DE+5A2I+5ZU29","p":"www19.a8.net"}},{"n":"FASIOビジネスカード","mat":"4BA2HC+4V1I6A+49Z2+614CX","lead":"経費と生活費を分ける。事業用のカードは、そのいちばん簡単な方法です。","sq":{"s":"www29.a8.net","a":"260810256294","e":"01","m":"s00000019955001013000","w":300,"h":250,"t":"4BA2HC+4V1I6A+49Z2+614CX","p":"www14.a8.net"},"wide":{"s":"www29.a8.net","a":"260810256294","e":"01","m":"s00000019955001007000","w":468,"h":60,"t":"4BA2HC+4V1I6A+49Z2+5ZU29","p":"www17.a8.net"}},{"n":"マネーフォワード クラウド確定申告","mat":"4B9ZDA+AXJL6Q+4JGQ+BXYE9","lead":"数字を月に一度そろえておくと、資金の残りが自分で見えるようになります。","sq":{"s":"www21.a8.net","a":"260806222661","e":"01","m":"s00000021185002006000","w":300,"h":250,"t":"4B9ZDA+AXJL6Q+4JGQ+BXYE9","p":"www16.a8.net"},"wide":{"s":"www23.a8.net","a":"260806222661","e":"01","m":"s00000021185002004000","w":728,"h":90,"t":"4B9ZDA+AXJL6Q+4JGQ+BXIYP","p":"www15.a8.net"}}]},"job":{"items":[{"n":"会社設立の無料相談（経営サポートプラスアルファ）","mat":"4B9ZDA+B4OSG2+5LH2+5YZ75","lead":"会社にするか、個人のまま進むか。決める前に、税理士に無料で聞けます。","sq":{"s":"www28.a8.net","a":"260806222673","e":"01","m":"s00000026111001003000","w":300,"h":250,"t":"4B9ZDA+B4OSG2+5LH2+5YZ75","p":"www15.a8.net"},"wide":null},{"n":"弥生の起業支援サービス【起業・開業ナビ】","mat":"4BA2HC+10BI82+35XE+HWPVL","lead":"開業届、青色申告、屋号。起業のときの事務を、順番に片づけます。","sq":{"s":"www22.a8.net","a":"260810256061","e":"01","m":"s00000014765003008000","w":300,"h":250,"t":"4BA2HC+10BI82+35XE+HWPVL","p":"www14.a8.net"},"wide":null},{"n":"バーチャルオフィス1","mat":"4B9ZDA+9JJ6DE+5A2I+5ZEMP","lead":"登記に使う住所を、自宅にするかどうか。先に決めておきたいところです。","sq":{"s":"www26.a8.net","a":"260806222577","e":"01","m":"s00000024633001005000","w":300,"h":250,"t":"4B9ZDA+9JJ6DE+5A2I+5ZEMP","p":"www12.a8.net"},"wide":{"s":"www21.a8.net","a":"260806222577","e":"01","m":"s00000024633001007000","w":728,"h":90,"t":"4B9ZDA+9JJ6DE+5A2I+5ZU29","p":"www19.a8.net"}},{"n":"FASIOビジネスカード","mat":"4BA2HC+4V1I6A+49Z2+614CX","lead":"経費と生活費を分ける。事業用のカードは、そのいちばん簡単な方法です。","sq":{"s":"www29.a8.net","a":"260810256294","e":"01","m":"s00000019955001013000","w":300,"h":250,"t":"4BA2HC+4V1I6A+49Z2+614CX","p":"www14.a8.net"},"wide":{"s":"www29.a8.net","a":"260810256294","e":"01","m":"s00000019955001007000","w":468,"h":60,"t":"4BA2HC+4V1I6A+49Z2+5ZU29","p":"www17.a8.net"}},{"n":"マネーフォワード クラウド確定申告","mat":"4B9ZDA+AXJL6Q+4JGQ+BXYE9","lead":"数字を月に一度そろえておくと、資金の残りが自分で見えるようになります。","sq":{"s":"www21.a8.net","a":"260806222661","e":"01","m":"s00000021185002006000","w":300,"h":250,"t":"4B9ZDA+AXJL6Q+4JGQ+BXYE9","p":"www16.a8.net"},"wide":{"s":"www23.a8.net","a":"260806222661","e":"01","m":"s00000021185002004000","w":728,"h":90,"t":"4B9ZDA+AXJL6Q+4JGQ+BXIYP","p":"www15.a8.net"}}]},"pro":{"items":[{"n":"オンラインアシスタント【フジ子さん】","mat":"4B9ZDA+9OAN7M+3TWG+5ZMCH","lead":"ひとりで全部やらない。事務を外に出すと、自分の時間が戻ってきます。","sq":{"s":"www27.a8.net","a":"260806222585","e":"01","m":"s00000017872001006000","w":300,"h":250,"t":"4B9ZDA+9OAN7M+3TWG+5ZMCH","p":"www15.a8.net"},"wide":{"s":"www28.a8.net","a":"260806222585","e":"01","m":"s00000017872001004000","w":468,"h":60,"t":"4B9ZDA+9OAN7M+3TWG+5Z6WX","p":"www19.a8.net"}},{"n":"採用代行【採善策】","mat":"4B9XTF+FG2XC2+52NU+5ZMCH","lead":"最初の一人を、どうやって探すか。採用を専門の人に任せる手もあります。","sq":{"s":"www29.a8.net","a":"260804211934","e":"01","m":"s00000023673001006000","w":300,"h":250,"t":"4B9XTF+FG2XC2+52NU+5ZMCH","p":"www15.a8.net"},"wide":{"s":"www25.a8.net","a":"260804211934","e":"01","m":"s00000023673001004000","w":468,"h":60,"t":"4B9XTF+FG2XC2+52NU+5Z6WX","p":"www10.a8.net"}},{"n":"顧客紹介サービス「セールス ハブ」","mat":"4B9ZDA+9ERPJ6+41RS+601S1","lead":"つくったものを、誰に最初に見せるか。紹介でつながるという方法があります。","sq":{"s":"www27.a8.net","a":"260806222569","e":"01","m":"s00000018892001008000","w":300,"h":250,"t":"4B9ZDA+9ERPJ6+41RS+601S1","p":"www12.a8.net"},"wide":{"s":"www24.a8.net","a":"260806222569","e":"01","m":"s00000018892001004000","w":468,"h":60,"t":"4B9ZDA+9ERPJ6+41RS+5Z6WX","p":"www19.a8.net"}},{"n":"STORES","mat":"4B9ZDA+9R9T8I+434O+62MDD","lead":"売り先をつくる。ネットショップと決済は、その日のうちに用意できます。","sq":{"s":"www20.a8.net","a":"260806222590","e":"01","m":"s00000019068001020000","w":300,"h":250,"t":"4B9ZDA+9R9T8I+434O+62MDD","p":"www10.a8.net"},"wide":{"s":"www22.a8.net","a":"260806222590","e":"01","m":"s00000019068001207000","w":728,"h":90,"t":"4B9ZDA+9R9T8I+434O+76P9T","p":"www10.a8.net"}}]},"learn":{"items":[{"n":"AI Agent Camp","mat":"4B9ZDA+85IRK2+5VRC+5YZ75","lead":"人手が足りないところを、AIに任せられるか。まず自分で触ってみる。","sq":{"s":"www25.a8.net","a":"260806222493","e":"01","m":"s00000027444001003000","w":300,"h":250,"t":"4B9ZDA+85IRK2+5VRC+5YZ75","p":"www16.a8.net"},"wide":null},{"n":"デイトラ","mat":"4B9XTG+2J3DVM+5IZ2+5YZ75","lead":"外注する前に、自分で一度つくってみる。話が通じるようになります。","sq":{"s":"www20.a8.net","a":"260804212153","e":"01","m":"s00000025787001003000","w":300,"h":250,"t":"4B9XTG+2J3DVM+5IZ2+5YZ75","p":"www10.a8.net"},"wide":null},{"n":"オンスク.JP","mat":"4B9XTG+2UEMDE+408S+5ZMCH","lead":"簿記や法務は、あとから効いてきます。すきま時間で少しずつ。","sq":{"s":"www29.a8.net","a":"260804212172","e":"01","m":"s00000018694001006000","w":300,"h":250,"t":"4B9XTG+2UEMDE+408S+5ZMCH","p":"www17.a8.net"},"wide":{"s":"www27.a8.net","a":"260804212172","e":"01","m":"s00000018694001004000","w":468,"h":60,"t":"4B9XTG+2UEMDE+408S+5Z6WX","p":"www10.a8.net"}}]}};

(function () {
  if (document.getElementById('nf-aff-css')) return;
  var st = document.createElement('style'); st.id = 'nf-aff-css';
  st.textContent = [
    '.nfa{display:block;margin:34px 0;padding:0;border:0;text-align:center}',
    '.nfa-h{display:flex;align-items:flex-start;justify-content:center;gap:9px;margin:0 0 11px;flex-wrap:nowrap;max-width:620px;margin-left:auto;margin-right:auto}',
    '.nfa-pr{flex:0 0 auto;margin-top:2px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10px;letter-spacing:.14em;color:#6B7280;border:1px solid #D7D9E3;border-radius:3px;padding:1px 5px;line-height:1.6}',
    '.nfa-lead{margin:0;font-size:13.5px;line-height:1.75;color:#3C4250;font-weight:650;text-align:left;letter-spacing:-.005em}',
    '.nfa-a{display:inline-block;max-width:100%;line-height:0}',
    '.nfa-a img{max-width:100%;height:auto;border:0;border-radius:6px}',
    '.nfa-note{margin:10px auto 0;max-width:620px;font-size:11px;line-height:1.75;color:#8B90A0;text-align:left}',
    '.nfa-px{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}',
    '@media (max-width:640px){.nfa{margin:26px 0}.nfa-lead{font-size:13px}}',
    '[data-theme="dark"] .nfa-lead{color:#C8CEDE}',
    '[data-theme="dark"] .nfa-pr{color:#9AA1B4;border-color:#3A3F52}',
    '[data-theme="dark"] .nfa-note{color:#7C8296}'
  ].join('\n');
  document.head.appendChild(st);
})();

var A8CLICK = 'https://px.a8.net/svt/ejp?a8mat=';

/* バナー画像のURL。A8がNEWFOR（wid=003）用に出しているものと同じ形です。 */
function affBanner(b) {
  return 'https://' + b.s + '/svt/bgt?aid=' + b.a + '&wid=003&eno=' + b.e + '&mid=' + b.m + '&mc=1';
}
/* 成果計測の1×1画像。A8の規定どおり、バナーと一緒に置きます。 */
function affPixel(b) {
  return 'https://' + b.p + '/0.gif?a8mat=' + b.t;
}

/* 同じページを読み直したときに、広告が入れ替わらないようにする。
   URLの文字から数を作って、その数で選びます。くじ引きではなく、
   出席番号のようなものです。 */
function affHash(s) {
  var x = 5381;
  for (var i = 0; i < s.length; i++) { x = ((x << 5) + x + s.charCodeAt(i)) >>> 0; }
  return x;
}

function affBuild(el) {
  var key = el.getAttribute('data-aff') || 'biz';
  var grp = A[key] || A.biz;
  if (!grp || !grp.items || !grp.items.length) { el.remove(); return; }
  var it = grp.items[affHash(location.pathname + '|' + key) % grp.items.length];
  /* 画面の幅を見て、出すバナーを1枚だけ決める。両方は出しません。 */
  var b = (it.wide && window.innerWidth >= 760) ? it.wide : it.sq;
  if (!b || !b.t) { el.remove(); return; }

  el.classList.add('nfa');
  el.style.position = 'relative';
  el.innerHTML =
      '<div class="nfa-h"><span class="nfa-pr">広告</span>'
    + '<p class="nfa-lead">' + it.lead + '</p></div>'
    + '<a class="nfa-a" href="' + A8CLICK + b.t + '" target="_blank" rel="nofollow sponsored noopener"></a>'
    + '<p class="nfa-note">この枠は広告です（アフィリエイトプログラムを含みます）。'
    + 'バナーは広告主が配っているものをそのまま出しています。'
    + '並び順は、このページを読んでいる方との近さで決めており、報酬額では変えません。</p>';

  var a = el.querySelector('.nfa-a');
  var done = false;
  /* 枠が画面に入ってから、バナーと1×1画像を同時に入れる。
     見ていない広告を「見た」と数えさせないため。 */
  var show = function () {
    if (done) return;
    done = true;
    var img = document.createElement('img');
    img.setAttribute('border', '0');
    img.width = b.w; img.height = b.h;
    img.alt = ''; img.decoding = 'async';
    img.src = affBanner(b);
    a.appendChild(img);
    var px = document.createElement('img');
    px.setAttribute('border', '0');
    px.className = 'nfa-px';
    px.width = 1; px.height = 1; px.alt = '';
    px.src = affPixel(b);
    el.appendChild(px);
  };
  if (window.IntersectionObserver) {
    var io = new IntersectionObserver(function (es) {
      for (var i = 0; i < es.length; i++) {
        if (es[i].isIntersecting) { show(); io.disconnect(); return; }
      }
    }, { rootMargin: '200px' });
    io.observe(el);
  } else {
    show();
  }
}

/* ============================================================
   ★2026-09-02 1ページに3種類（メイン／サブ／誰でも）を出す

   わたるさんの指示（全媒体で守るルール）:
   > 「メインターゲット、サブターゲット、誰でも、みたいな感じで
   >   3種類をアフィリ広告入れるってのを統一で守って欲しい」

   これまでのNEWFORは1ページに枠が1つだけで、しかもその枠は記事の
   いちばん下にありました。実測で、ページ全体13,768pxのうち12,029px
   地点＝9割スクロールしないと出てきません。

   ページのHTMLは1,292本あるので触りません。ここ（JavaScript）から
   枠を2つ足して、記事の途中に置きます。

   3つの分け方:
     start（メイン）= これから始める人。会社をつくる・住所を借りる
     run  （サブ）  = もう回している人。お金・カード・人手・お店
     any  （誰でも）= 立場を問わない。学び直し・スキル
   同じ広告主が1ページに2回出ないよう、3つのプールで中身を分けます。
   （これまでは biz と job の中身がまったく同じでした）
   ============================================================ */
var _bi = (A.biz && A.biz.items) || [];
var _pi = (A.pro && A.pro.items) || [];
var _li = (A.learn && A.learn.items) || [];
A.start = { items: _bi.slice(0, 3) };
A.run = { items: _bi.slice(3).concat(_pi) };
A.any = { items: _li.slice() };

function affPoolOK(k) { return A[k] && A[k].items && A[k].items.length > 0; }

/* 見出しの前に枠を入れる。ページの高さを見て、上から25%と55%の
   あたりにいちばん近い見出しを選びます。文章の切れ目に入るので、
   読んでいる途中で唐突に出てくることがありません。 */
function affSpread() {
  var slots = document.querySelectorAll(".affslot");
  if (!slots.length) return;
  if (affPoolOK("any")) slots[slots.length - 1].setAttribute("data-aff", "any");
  if (slots.length > 1) return;
  var main = document.querySelector("main") || document.body;
  var hs = [];
  var all = main.querySelectorAll("h2");
  for (var i = 0; i < all.length; i++) { if (all[i].offsetHeight > 0) hs.push(all[i]); }
  if (hs.length < 3) return;
  var H = document.body.scrollHeight;
  var used = [];
  var near = function (ratio) {
    var best = null, bd = 1e9;
    for (var i = 1; i < hs.length; i++) {
      if (used.indexOf(hs[i]) >= 0) continue;
      var y = hs[i].getBoundingClientRect().top + (window.pageYOffset || 0);
      var d = Math.abs(y - H * ratio);
      if (d < bd) { bd = d; best = hs[i]; }
    }
    if (best) used.push(best);
    return best;
  };
  var mk = function (key) {
    var d = document.createElement("div");
    d.className = "affslot";
    d.setAttribute("data-aff", key);
    return d;
  };
  var a = affPoolOK("start") ? near(0.25) : null;
  var b = affPoolOK("run") ? near(0.55) : null;
  if (b) b.parentNode.insertBefore(mk("run"), b);
  if (a) a.parentNode.insertBefore(mk("start"), a);
}
affSpread();

Array.prototype.forEach.call(document.querySelectorAll('.affslot, .affmini-slot'), affBuild);
