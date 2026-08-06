# -*- coding: utf-8 -*-
import io
OLD = '''function roll(step){
  tix=(tix+(step||1)+TODAY.length)%TODAY.length;
  if(tix===0&&step===undefined&&tTxt.textContent===""){tPaint();tBarRestart();return;}
  tTxt.classList.add("out");
  setTimeout(function(){tPaint();tTxt.classList.remove("out");},250);
  tBarRestart();
}'''
NEW = '''function roll(step){
  tix=(tix+(step||1)+TODAY.length)%TODAY.length;
  tTxt.classList.add("out");
  setTimeout(function(){tPaint();tTxt.classList.remove("out");},250);
  tBarRestart();
}'''
OLD_BOOT='tix=-1;roll(1);tStart();vrender();'
NEW_BOOT='tix=0;tPaint();tStart();vrender();'
for f in ['newfor-top-light.html','newfor-top.html']:
    s=io.open(f,encoding='utf-8').read()
    assert OLD in s and OLD_BOOT in s, f
    s=s.replace(OLD,NEW).replace(OLD_BOOT,NEW_BOOT)
    io.open(f,'w',encoding='utf-8').write(s); print(f,'ok')
