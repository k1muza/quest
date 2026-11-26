"""Record the actual Chromium canvas/HUD, not an offline simulated video."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from tempfile import TemporaryDirectory
import time,subprocess,os
R=Path(__file__).resolve().parent
with sync_playwright() as p, TemporaryDirectory() as d:
 b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);page=b.new_page(viewport={'width':1280,'height':720});page.set_content((R/'kingdom-quest.html').read_text());page.wait_for_function('quest.ready && quest.cinema.state().viewReady',timeout=30000);ev=page.evaluate
 ev('''()=>{quest.reset(6);let s=quest.getState();s.phase='active';s.teams.forEach((t,i)=>t.score=[17,9,13,15,18,16][i]);quest.applyState(s,{instant:true,quiet:true});quest.cinema.setAuto(true)}''')
 for i in range(90):
  start=time.monotonic()
  if i==8:ev('quest.cinema.sequence(5)')
  if i==20:ev('quest.cinema.changeView("bridge","Silverwater")')
  if i==35:ev('quest.cinema.changeView("overview")')
  if i==47:ev('quest.cinema.changeView("citadel","Royal Citadel")')
  if i==59:ev('quest.cinema.setLighting("dusk")')
  if i==70:ev('quest.finish()')
  page.screenshot(path=f'{d}/{i:03d}.jpg',type='jpeg',quality=83)
  page.wait_for_timeout(max(0,125-round((time.monotonic()-start)*1000)))
 b.close();subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','8','-i',f'{d}/%03d.jpg','-c:v','libx264','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(R/'gallery'/'cinematic-demo.mp4')],check=True)
