"""Record real browser frames of Safari Rush. Run after the standalone build."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import tempfile,subprocess,time,os
R=Path(__file__).resolve().parent
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None,headless=True,args=['--no-sandbox'])
    page=b.new_page(viewport={'width':1280,'height':720})
    page.goto((R/'safari-rush.html').as_uri())
    page.wait_for_function('window.quest?.ready')
    page.evaluate('''()=>{let s=quest.getState();s.phase="active";s.teams.forEach((t,i)=>t.score=i*3);quest.applyState(s,{instant:true});quest.score(9)}''')
    with tempfile.TemporaryDirectory() as d:
        start=time.monotonic()
        for i in range(96):
            if i==28:page.evaluate('quest.score(9)')
            if i==55:page.evaluate('quest.score(12)')
            if i==80:page.evaluate('quest.finish()')
            page.screenshot(path=f'{d}/frame-{i:03}.jpg',type='jpeg',quality=87)
            page.wait_for_timeout(max(0,int((start+(i+1)/12-time.monotonic())*1000)))
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','12','-i',f'{d}/frame-%03d.jpg','-c:v','libx264','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(R/'screenshots'/'demonstration.mp4')],check=True)
    b.close()
