const { chromium } = require('playwright');
const UFO='<path d="M10.6 16.4 L21.4 16.4 L25.8 31 L6.2 31 Z" fill="currentColor" opacity=".16"/><path d="M12.5 16.4 L19.5 16.4 L21.9 26.5 L10.1 26.5 Z" fill="currentColor" opacity=".24"/><ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="currentColor"/><path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" fill="none"/>';
const PAGES=[
 {f:'og-top.png', eyebrow:'新規事業メディア', title:'新規事業は、<br>成功しか語られてこなかった。', sub:'次の事業へ渡されたバトンまで、ぜんぶ記録する。'},
 {f:'og-companies.png', eyebrow:'大企業の新規事業データベース', title:'12社・226事業を<br>公開情報から記録した。', sub:'企業ごとに、いま続く事業と次へ渡した事業を。'},
 {f:'og-kddi.png', eyebrow:'KDDI ／ 企業データ', title:'KDDIの新規事業、<br>18事業の記録。', sub:'2008年のじぶん銀行から、2026年の大阪堺データセンターまで。'},
 {f:'og-kddi-newbusiness.png', eyebrow:'企業の決断 #002', title:'KDDIは、自分ひとりで<br>新規事業を始めたことがない。', sub:'18件のうち14件に、組む相手がいた。'},
 {f:'og-sony-newbusiness.png', eyebrow:'企業の決断 #003', title:'ソニーが作ったのは、<br>事業ではなく「作り方」。', sub:'社内20数件、他社支援1,050件超。'},
 {f:'og-ajinomoto-newbusiness.png', eyebrow:'企業の決断 #011', title:'本業をやめずに、<br>利益率54%の事業を隣に作った。', sub:'売上6%の電子材料が、利益の3割を稼ぐ。'},
 {f:'og-softbank-newbusiness.png', eyebrow:'企業の決断 #012', title:'事業を持ち続けるつもりで<br>始めていない。', sub:'45年の年表と、純利益5兆22億円の出どころ。'},
 {f:'og-fujifilm-newbusiness.png', eyebrow:'企業の決断 #004', title:'買ってきた新規事業より、<br>買わなかった事業のほうが儲かる。', sub:'買った柱776億円 / 買わなかった柱1,392億円。'},
 {f:'og-toyota-newbusiness.png', eyebrow:'企業の決断 #005', title:'トヨタは新規事業のたびに<br>会社をつくる。', sub:'2021年だけで3つ。KINTOは6年目で黒字に。'},
 {f:'og-panasonic-newbusiness.png', eyebrow:'企業の決断 #006', title:'パナソニックは同じ問いに、<br>3回挑んだ。', sub:'HomeX、Yohana、Panasonic Well の7年。'},
 {f:'og-mitsubishi-newbusiness.png', eyebrow:'企業の決断 #007', title:'三菱商事は、同じ会社の<br>持ち方を2回つくり替えた。', sub:'ローソン、1,440億円から4,971億円へ。'},
 {f:'og-jreast-newbusiness.png', eyebrow:'企業の決断 #008', title:'JR東日本の新規事業は、<br>持て余していた資産だった。', sub:'駅の売店、列車の空席、車両基地の跡地。'},
 {f:'og-sevenandi-newbusiness.png', eyebrow:'企業の決断 #009', title:'セブン&アイの10年は、<br>足し算ではなく引き算だった。', sub:'買収2.2兆円、売却8,147億円、社内発は1,200億円。'},
 {f:'og-recruit-newbusiness.png', eyebrow:'企業の決断 #010', title:'12億ドルで買ったブランドを、<br>7年後に畳んだ。', sub:'GlassdoorはIndeedへ。Airレジは90万アカウントへ。'},
 {f:'og-docomo.png', eyebrow:'企業の決断 #001', title:'NTTドコモは、25年かけて<br>「iモード」に帰ってきた。', sub:'海外で1兆円超を投じ、いま金融に全額を張る25年。'},
];
const tpl=(p)=>`<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;overflow:hidden;position:relative;
 background:linear-gradient(160deg,#2730CE 0%,#2F3BD6 52%,#3843E6 100%);
 font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif;color:#fff;
 -webkit-font-smoothing:antialiased}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.055) 1px,transparent 1px);background-size:76px 76px}
.ufo{position:absolute;right:-70px;bottom:-90px;width:520px;color:#fff;opacity:.13}
.in{position:relative;padding:66px 72px;height:100%;display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:13px}
.brand svg{width:46px;height:46px;color:#fff}
.wm{font-family:ui-monospace,Menlo,monospace;font-size:27px;font-weight:800;letter-spacing:.17em}
.wm b{color:#FF8A45}
.eye{margin-top:auto;font-family:ui-monospace,Menlo,monospace;font-size:19px;letter-spacing:.15em;color:#FFB489;font-weight:700}
h1{margin:16px 0 0;font-size:62px;line-height:1.28;letter-spacing:-.035em;font-weight:850}
.sub{margin-top:22px;font-size:24px;color:rgba(255,255,255,.9);line-height:1.6;letter-spacing:-.01em}
.bar{margin-top:30px;height:8px;width:150px;background:#FF5A14;border-radius:99px}
</style></head><body>
<div class="grid"></div>
<svg class="ufo" viewBox="0 0 32 32" fill="none">${UFO}</svg>
<div class="in">
 <div class="brand"><svg viewBox="0 0 32 32" fill="none">${UFO}</svg><span class="wm">NEW<b>FOR</b></span></div>
 <div class="eye">${p.eyebrow}</div>
 <h1>${p.title}</h1>
 <div class="sub">${p.sub}</div>
 <div class="bar"></div>
</div></body></html>`;
(async()=>{const b=await chromium.launch();
for(const p of PAGES){
 const pg=await b.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});
 await pg.setContent(tpl(p));await pg.waitForTimeout(200);
 await pg.screenshot({path:'dist/assets/'+p.f});await pg.close();
 console.log(p.f);
}
await b.close()})();
