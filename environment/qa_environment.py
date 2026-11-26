from playwright.sync_api import sync_playwright
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parent
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files']);page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1);errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url) if r.url.startswith('http') else None)
 page.set_content((ROOT/'kingdom-quest-environment.html').read_text());page.wait_for_function('window.quest && quest.ready',timeout=12000);page.wait_for_timeout(300)
 def shot(n):page.wait_for_timeout(100);page.screenshot(path=str(ROOT/'screenshots'/n))
 shot('01-complete-browser.png');reports=[]
 for n in [30,40,50,60]:
  page.evaluate(f'quest.generate({n})');reports.append(page.evaluate('quest.validate()'))
 for name,c,r,z in [('02-mountains',11,1,1.95),('03-starting-village',2,8,2.15),('04-agriculture',5,9,2.15),('05-woodland',3,3,1.75),('06-bridge',7,3,2.6),('07-township',12,7,1.9),('08-citadel',14,3,2.15),('09-harbour',2,9,2.25)]:
  page.evaluate(f'quest.inspect({c},{r},{z})');shot(name+'.png')
 page.evaluate('quest.resetCamera()');page.wait_for_timeout(2200);metrics=page.evaluate('quest.metrics()');print(json.dumps({'validations':reports,'metrics':metrics,'errors':errors,'externalRequests':requests,'hiddenUI':page.locator('#hud').is_hidden() and page.locator('#footer').is_hidden()},indent=2));(ROOT/'qa-results.json').write_text(json.dumps({'validations':reports,'metrics':metrics,'errors':errors,'externalRequests':requests,'hiddenUI':page.locator('#hud').is_hidden() and page.locator('#footer').is_hidden()},indent=2));browser.close()
