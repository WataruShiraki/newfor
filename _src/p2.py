# -*- coding: utf-8 -*-
import io
TOPS = ['newfor-top-light.html','newfor-top.html']

OLD_STRIP = '''        今日の一件
      </span>
      <span class="txt" id="todayTxt"></span>
      <button class="re" id="reroll">別の一件</button>
    </div>'''
NEW_STRIP = '''        今週の一件
      </span>
      <span class="txt" id="todayTxt"></span>
      <span class="tno" id="todayNo"></span>
      <button class="re" id="reroll">次の一件</button>
      <span class="tprog"><i id="tbar"></i></span>
    </div>'''

OLD_TODAY_START = 'var TODAY=['
OLD_TODAY_END = '];\nvar tix=-1;'

NEW_TODAY = '''var TODAY=[
 ["KDDI","au Starlink Direct が接続数400万人を突破。空が見えればつながる","2025年4月開始"],
 ["NTTドコモ","dポイントマーケットが1年9カ月で役目を終え、d払い経済圏へ集約","2024年10月開始"],
 ["KDDI","Syn.構想で組んだ約120億円と提携網は、その後のau経済圏づくりへ","2014年10月 - 2018年7月"],
 ["JR東日本","駅ナカの空きスペースで無人リユース店舗を実証","2026年7月開始"],
 ["三井物産","荷主横断の共同輸送を担う新会社を設立","2026年7月設立"],
 ["資生堂","肌診断AIをBtoB外販モデルへ転換","2026年7月開始"],
 ["ソニーグループ","社内起業制度から生まれた事業が累計47件","2015年以降"],
 ["KDDI","GeForce NOW Powered by au が5年間の提供を走り切った","2020年9月 - 2025年10月"]
];
var tix=-1;'''

OLD_ROLL = '''function roll(){
  var i=tix;while(i===tix){i=Math.floor(Math.random()*TODAY.length);}
  tix=i;var t=TODAY[i];
  document.getElementById("todayTxt").innerHTML="<b>"+t[0]+"</b>　"+t[1]+"　<em>"+t[2]+"</em>";
}
document.getElementById("reroll").addEventListener("click",roll);'''

NEW_ROLL = '''var tTxt=document.getElementById("todayTxt"),tNo=document.getElementById("todayNo"),
    tBar=document.getElementById("tbar"),tStrip=tTxt.closest(".today"),
    tTimer=null,T_PERIOD=7000,
    tReduce=window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches;
function tPaint(){
  var t=TODAY[tix];
  tTxt.innerHTML="<b>"+t[0]+"</b>　"+t[1]+"　<em>"+t[2]+"</em>";
  tNo.textContent=(tix+1)+"/"+TODAY.length;
}
function tBarRestart(){
  if(!tBar||tReduce)return;
  tBar.style.animation="none";void tBar.offsetWidth;
  tBar.style.animation="tgrow "+(T_PERIOD/1000)+"s linear forwards";
}
function roll(step){
  tix=(tix+(step||1)+TODAY.length)%TODAY.length;
  if(tix===0&&step===undefined&&tTxt.textContent===""){tPaint();tBarRestart();return;}
  tTxt.classList.add("out");
  setTimeout(function(){tPaint();tTxt.classList.remove("out");},250);
  tBarRestart();
}
function tStart(){tStop();if(tReduce)return;tTimer=setInterval(function(){roll(1);},T_PERIOD);tBarRestart();}
function tStop(){if(tTimer){clearInterval(tTimer);tTimer=null;}}
if(tStrip){
  tStrip.addEventListener("mouseenter",function(){tStop();if(tBar)tBar.style.animationPlayState="paused";});
  tStrip.addEventListener("mouseleave",function(){if(tBar)tBar.style.animationPlayState="running";tStart();});
}
document.addEventListener("visibilitychange",function(){document.hidden?tStop():tStart();});
document.getElementById("reroll").addEventListener("click",function(){roll(1);tStart();});'''

OLD_BOOT = 'roll();vrender();'
NEW_BOOT = 'tix=-1;roll(1);tStart();vrender();'

for f in TOPS:
    s = io.open(f, encoding='utf-8').read()
    assert OLD_STRIP in s, f+' strip'
    s = s.replace(OLD_STRIP, NEW_STRIP)
    a = s.index(OLD_TODAY_START); b = s.index(OLD_TODAY_END, a)+len(OLD_TODAY_END)
    s = s[:a] + NEW_TODAY + s[b:]
    assert OLD_ROLL in s, f+' roll'
    s = s.replace(OLD_ROLL, NEW_ROLL)
    assert OLD_BOOT in s, f+' boot'
    s = s.replace(OLD_BOOT, NEW_BOOT)
    io.open(f,'w',encoding='utf-8').write(s)
    print(f,'B ok')
