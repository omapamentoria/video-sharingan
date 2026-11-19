const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
 const dir=process.argv[2], n=+process.argv[3];
 const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
 for(let i=1;i<=n;i++){const f=`${dir}/slide-${String(i).padStart(2,'0')}`;
   await pg.goto('file://'+f+'.html'); await pg.waitForTimeout(200);
   const bot=await pg.evaluate(()=>{const c=document.querySelector('.card');return c?c.getBoundingClientRect().bottom:0});
   if(bot>1190)console.log(`AVISO slide ${i}: cartao ${bot.toFixed(0)}px`);
   await pg.screenshot({path:f+'.jpg',type:'jpeg',quality:92}); fs.unlinkSync(f+'.html');}
 await b.close(); console.log('ok',n);
})();
