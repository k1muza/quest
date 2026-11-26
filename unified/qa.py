"""Exercise the exact offline bundle. Set CHROMIUM to override executable path."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, os, math
ROOT=Path(__file__).resolve().parent;SCREEN=ROOT/'screenshots';SCREEN.mkdir(exist_ok=True)
checks=[];errors=[];requests=[]
def check(label,result,detail=None):
 checks.append({'test':label,'pass':bool(result),'detail':detail});print(('PASS' if result else 'FAIL'),label,detail if detail is not None else '',flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);page=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
 page.set_content((ROOT/'kingdom-quest.html').read_text());page.wait_for_function('window.quest?.ready',timeout=15000)
 def ev(s,arg=None):return page.evaluate(s,arg)
 def shot(name):page.wait_for_timeout(110);page.screenshot(path=str(SCREEN/(name+'.png')))
 def scores(values,phase='active',instant=True):
  ev('([values,phase,instant])=>{let s=quest.getState();s.phase=phase;s.complete=false;s.winnerIds=[];s.timerRunning=false;s.teams.forEach((t,i)=>t.score=values[i]);quest.applyState(s,{instant,quiet:true})}',[values,phase,instant])
 def reset(n=4):ev('n=>quest.reset(n)',n);ev('quest.resetCamera();quest.setClean(false);quest.setAmbient(true);quest.setOcclusion(true)')
 def stop_for(region):return ev('r=>Math.round(QUEST_DATA.regions[r]/QUEST_DATA.length*(quest.getState().stopCount-1))',region)
 def zoom(region,scale=2):ev('([r,z])=>quest.inspect(QUEST_DATA.regions[r],z)',[region,scale])
 ev('quest.setClean(true)');shot('01-clean-environment');ev('quest.setClean(false)');ev('document.querySelector("#motion").style.visibility="hidden"');shot('02-stop-markers');ev('document.querySelector("#motion").style.visibility="visible"')
 for n in [30,40,50,60]:
  data=ev('n=>quest.validate(n)',n);check('stop count '+str(n),data['ok'],data)
 geom=ev('''()=>{let a=QUEST_DATA.route,p=QUEST_DATA.projection,max=0,depth=0,g=0,step=0;for(let i=0;i<a.length;i++){let q=a[i];max=Math.max(max,Math.abs(q[4]-q[1]),Math.abs(q[5]-(283+q[3]*p.cos-q[2]*p.sin)));depth=Math.max(depth,Math.abs(q[6]-(q[2]*p.cos+q[3]*p.sin)));if(i){let d=q[0]-a[i-1][0];step=Math.max(step,d);if(d<=0)g++}}return {maxProjectionError:max,maxDepthError:depth,maxStep:step,nonMonotonic:g}}''');check('exact same camera projection and monotonic arc',geom['maxProjectionError']<.001 and geom['maxDepthError']<.001 and geom['nonMonotonic']==0,geom)
 for n in range(2,7):reset(n);check(f'{n} competing teams',len(ev('quest.positions()'))==n)
 reset(4);scores([6,16,25,34]);shot('03-four-teams');reset(6);scores([4,12,19,24,31,38]);shot('04-six-teams')
 for region in ['Willowbrook','Golden Fields','Silverwater','Crownspine','Royal Gate','Royal Citadel']:
  n=stop_for(region);scores([n]*6);positions=ev('quest.positions()');locs={(round(t['location']['x'],2),round(t['location']['y'],2)) for t in positions};check('six tied: '+region,len(locs)==6 and len({t['stop'] for t in positions})==1,{'stop':n+1,'positions':len(locs)});zoom(region,2.4);shot('tie-'+region.lower().replace(' ','-'))
 ev('quest.resetCamera()');scores([19]*6);shot('05-six-way-tie')
 for i,region in enumerate(['Silverwater','Elderwood','Crownspine','Royal Gate','Royal Citadel'],6):
  reset(4);n=stop_for(region);scores([max(0,n-1),4,8,12]);zoom(region,2.15);ev('quest.score(2)');page.wait_for_timeout(240);shot(f'{i:02d}-movement-'+region.lower().replace(' ','-'));page.wait_for_timeout(2500);pos=ev('quest.positions()[0]');check('movement settles: '+region,abs(pos['d']-pos['target'])<.001,pos['stop'])
 reset(4);scores([6,16,25,34]);ev('''()=>{let s=quest.getState();s.remainingTime=23;s.timerRunning=true;quest.applyState(s)}''');shot('11-active-turn');ev('quest.score(3)');page.wait_for_timeout(150);first=ev('quest.positions()[0]');ev('quest.score(-5)');page.wait_for_timeout(2600);second=ev('quest.positions()[0]');check('forward backward reconciliation',first['target']>second['target'] and abs(second['d']-second['target'])<.001)
 ev('quest.undo()');page.wait_for_timeout(2600);check('undo',ev('quest.getState().teams[0].score')==9)
 ev('quest.score(-30)');page.wait_for_timeout(2600);check('negative authoritative score',ev('quest.getState().teams[0].score')==-21 and ev('quest.positions()[0].stop')==1)
 ev('quest.score(100)');page.wait_for_timeout(2600);check('overflow authoritative score; no auto win',ev('quest.getState().teams[0].score')==79 and ev('quest.positions()[0].stop')==40 and not ev('quest.getState().complete'))
 ev('''()=>{for(let i=0;i<12;i++)quest.score(i%2?-5:3)}''');page.wait_for_timeout(2600);q=ev('quest.positions()[0]');check('rapid score final target',q['score']==67 and abs(q['d']-q['target'])<.001)
 ev('''()=>{let s=quest.getState();s.teams[0].score=12;s.teams[1].score=17;s.round=3;s.activeTeamId=s.teams[1].id;s.phase='handover';s.remainingTime=15;s.timerRunning=false;quest.applyState(s);quest.applyState(s)}''');page.wait_for_timeout(2600);q=ev('quest.positions()');check('snapshot idempotent reconciliation',q[0]['score']==12 and q[1]['score']==17 and all(abs(x['d']-x['target'])<.001 for x in q))
 check('route setup locked during play',ev('''()=>{let s=quest.getState();s.stopCount=60;try{quest.applyState(s);return false}catch(e){return true}}'''))
 ev('''()=>{let s=quest.getState();s.remainingTime=1;s.timerRunning=true;s.phase='active';quest.applyState(s)}''');page.wait_for_timeout(1300);check('timer reaches turn-complete',ev('quest.getState().phase')=='turn-complete' and ev('quest.getState().remainingTime')==0)
 ev('''()=>{let s=quest.getState();s.remainingTime=12;s.timerRunning=false;quest.applyState(s)}''');page.wait_for_timeout(500);check('paused timer',abs(ev('quest.getState().remainingTime')-12)<.01)
 reset(6);scores([39,35,31,22,17,6]);ev('quest.finish()');shot('12-winner-celebration');check('explicit authoritative winner',ev('quest.getState().winnerIds')==['team-1'] and page.locator('#results').is_visible())
 reset(4);scores([6,16,25,34]);ev('quest.setOcclusion(true)');page.wait_for_timeout(200);a=ev('quest.metrics()');ev('quest.setOcclusion(false)');page.wait_for_timeout(200);b0=ev('quest.metrics()');check('depth mask actually clips foreground pixels',a['clippedPixels']>0 and b0['clippedPixels']==0,{'enabled':a['clippedPixels'],'disabled':b0['clippedPixels']});ev('quest.setOcclusion(true)')
 # Narrow bridge geometry and actual rendered scene comparisons: inspect depth at each sampled route location.
 visibility=ev('''()=>{let n=0,maxRun=0,run=0,start=0;for(let a of QUEST_DATA.route){let hidden=quest.sceneDepth(a[4],a[5]-20)>a[6]+20*QUEST_DATA.projection.cos+3;if(hidden){n++;if(!run)start=a[0];run=a[0]-start+.01;maxRun=Math.max(maxRun,run)}else run=0}return {samples:QUEST_DATA.route.length,approxUpperPawnOccludedSamples:n,longestOccludedSpanWorldUnits:maxRun}}''');check('scene depth available along route',visibility['samples']>1000,visibility)
 # Floating team indicators are intentionally rendered above foreground; ground shadows retain depth masks.
 for region in ['Willowbrook','Golden Fields','Silverwater','Crownspine','Royal Gate','Royal Citadel']:
  reset(6);n=stop_for(region);scores([n]*6);positions=ev('quest.positions()');anchor=positions[0]['location']['anchor'];unique={(q['location']['anchor']['x'],q['location']['anchor']['y']) for q in positions};poses=ev('quest.positions().map(q=>QuestMarkers.pose(q.location,1000))');gaps=[math.hypot(a['x']-b['x'],a['y']-b['y'])-a['r']-b['r'] for i,a in enumerate(poses) for b in poses[i+1:]];check('floating shared anchor and badge clearance: '+region,len(unique)==1 and min(gaps)>=0 and all(0<q['x']-q['r']<q['x']+q['r']<1920 and 0<q['y']-q['r']<q['y']+q['r']<1080 for q in poses),{'minimumGap':round(min(gaps),2),'anchor':anchor})
 reset(4);scores([6,16,25,34]);check('idle hover changes while route anchor remains fixed',ev('''()=>{let q=quest.positions()[0].location;let a=QuestMarkers.pose(q,1000),b=QuestMarkers.pose(q,1500);return a.y!==b.y&&a.x===b.x&&q.anchor.y===q.y}'''))
 for size in [(1280,720),(3840,2160)]:
  page.set_viewport_size({'width':size[0],'height':size[1]});page.wait_for_timeout(300);bounds=page.locator('#stage').bounding_box();check('responsive '+str(size),abs(bounds['width']-size[0])<1 and abs(bounds['height']-size[1])<1);shot('resolution-'+str(size[0]))
 page.set_viewport_size({'width':1920,'height':1080});page.keyboard.press('o');check('operator separate',page.locator('#operator').is_visible());page.keyboard.press('o');check('operator hidden in spectator',page.locator('#operator').is_hidden());page.keyboard.press('c');check('clean map',page.locator('#hud').is_hidden() and page.locator('#markers').is_hidden());page.keyboard.press('c')
 try:
  page.keyboard.press('f');page.wait_for_timeout(300);check('fullscreen',ev('!!document.fullscreenElement'));page.keyboard.press('f')
 except Exception as e:check('fullscreen',False,str(e))
 reset(6);scores([5,12,19,24,31,38]);page.wait_for_timeout(4300);metrics=ev('quest.metrics()');check('no page errors',not errors,errors);check('offline: no external requests',not requests,requests)
 output={'checks':checks,'passed':sum(c['pass'] for c in checks),'total':len(checks),'metrics':metrics,'bundleBytes':(ROOT/'kingdom-quest.html').stat().st_size,'browser':b.version,'errors':errors,'externalRequests':requests};(ROOT/'qa-results.json').write_text(json.dumps(output,indent=2));print(json.dumps({k:v for k,v in output.items() if k!='checks'},indent=2));b.close()
