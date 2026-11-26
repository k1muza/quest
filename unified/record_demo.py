"""Record actual browser frames and additional arrival/gate/winner captures."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import tempfile,subprocess,time,os
R=Path(__file__).resolve().parent
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);page=b.new_page(viewport={'width':1920,'height':1080});page.set_content((R/'kingdom-quest.html').read_text());page.wait_for_function('quest.ready');
 def setup(scores):page.evaluate('a=>{quest.reset(a.length);let s=quest.getState();s.phase="active";s.teams.forEach((t,i)=>t.score=a[i]);quest.applyState(s,{instant:true,quiet:true})}',scores)
 def shot(name,ms=150):page.wait_for_timeout(ms);page.screenshot(path=str(R/'screenshots'/name))
 setup([38,4,8,12]);page.evaluate('quest.inspect(QUEST_DATA.regions["Royal Gate"],2.15)');shot('09-movement-royal-gate.png');page.evaluate('quest.score(1)');shot('10-movement-royal-citadel.png',700)
 setup([39,35,31,22,17,6]);page.evaluate('quest.resetCamera();quest.finish()');shot('12-winner-celebration.png',700)
 page.set_viewport_size({'width':1280,'height':720});setup([14,10,8,6]);page.evaluate('quest.resetCamera();quest.score(10)')
 with tempfile.TemporaryDirectory() as d:
  start=time.monotonic()
  for i in range(72):
   if i==30:page.evaluate('quest.score(15)')
   if i==55:page.evaluate('quest.finish()')
   page.screenshot(path=f'{d}/frame-{i:03}.jpg',type='jpeg',quality=87)
   page.wait_for_timeout(max(0,int((start+(i+1)/12-time.monotonic())*1000)))
  subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','12','-i',f'{d}/frame-%03d.jpg','-c:v','libx264','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(R/'screenshots'/'demonstration.mp4')],check=True)
 b.close()
