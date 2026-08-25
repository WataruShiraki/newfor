const { chromium } = require('playwright');
const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath: process.env.PW_CHROMIUM || '/opt/pw-browsers/chromium'});
async function svg2png(svgPath,out,w,h){
  const svg=fs.readFileSync(svgPath,'utf8');
  const p=await b.newPage({viewport:{width:w,height:h}});
  await p.setContent(`<body style="margin:0">${svg.replace(/width="\d+"/,'width="'+w+'"').replace(/height="\d+"/,'height="'+h+'"')}</body>`);
  await p.waitForTimeout(120);
  await p.screenshot({path:out,omitBackground:false});
  await p.close();
}
await svg2png('dist/assets/favicon.svg','dist/assets/favicon-32.png',32,32);
await svg2png('dist/assets/favicon.svg','dist/assets/favicon-192.png',192,192);
await svg2png('dist/assets/favicon.svg','dist/assets/favicon-512.png',512,512);
await svg2png('dist/assets/apple.svg','dist/assets/apple-touch-icon.png',180,180);
await b.close();console.log('png ok')})();
