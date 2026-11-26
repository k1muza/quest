"""Safari Rush acceptance smoke test: generated standalone HTML, never network."""
import json, math, os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
DIST=ROOT/'safari-rush.html'
SCREEN=ROOT/'screenshots';SCREEN.mkdir(exist_ok=True)
results=[];errors=[];network=[]
def check(name,ok,detail=None):
    results.append(dict(test=name,passed=bool(ok),detail=detail))
    print(('PASS' if ok else 'FAIL'),name,detail,flush=True)
layout=json.loads((ROOT/'../../environment/layout.json').read_text())
data=json.loads((ROOT/'route.json').read_text())
coords=[(p['c'],p['r']) for p in layout['cells']]
check('Unique modular terrain coordinates',len(set(coords))==len(coords),len(coords))
check('All modular road and river ports matched',not layout['unmatched'])
for name in ['primary','river']:
    pts=layout[name]
    largest=max(math.hypot(a['x']-b['x'],a['y']-b['y']) for a,b in zip(pts,pts[1:]))
    check(name+' continuous centreline',largest<60,largest)
route=data['route']
check('Strictly increasing world-space distance',all(a[0]<b[0] for a,b in zip(route,route[1:])))
check('Map package identity',data['map']=='safari-rush')
check('Capacity and distribution size',DIST.stat().st_size>0,DIST.stat().st_size)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None,headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
    page.goto(DIST.as_uri());page.wait_for_function('window.quest?.ready',timeout=30000)
    def ev(code,arg=None):return page.evaluate(code,arg)
    def shot(name):page.wait_for_timeout(160);page.screenshot(path=str(SCREEN/(name+'.png')))
    def reset(n=4):ev('n=>quest.reset(n)',n);ev('quest.resetCamera();quest.setClean(false)')
    def scores(vals):ev('vals=>{let s=quest.getState();s.phase="active";s.teams.forEach((t,i)=>t.score=vals[i]);quest.applyState(s,{instant:true,quiet:true})}',vals)
    state=ev('quest.getState()')
    check('30 movements / 31 physical stops',state['stopCount']==31 and state['scoreAtFinish']==30)
    for n in [21,31,41,51]:
        q=ev('n=>quest.validate(n)',n)
        # Invalid high-density configurations must be refused, not silently accepted.
        if n==31:check('Default route has 50px centre separation',q['ok'] and q['minimumGap']>=50,q)
        accepted=ev('n=>{let s=quest.getState();s.stopCount=n;s.scoreAtFinish=n-1;try{quest.applyState(s);return true}catch(e){return false}}',n)
        check(f'{n-1} steps capacity validation',accepted==q['ok'] and (n not in [21,31,41] or accepted),q)
    reset();ev('quest.setClean(true)');shot('01-clean-environment');ev('quest.setClean(false)');shot('02-default-board')
    for i,region in enumerate(data['regions'],3):
        ev('r=>quest.inspect(QUEST_DATA.regions[r],2.2)',region);shot(f'{i:02d}-'+region.lower().replace(' ','-'))
    reset();scores([4,10,15,25]);shot('09-four-teams')
    check('One point equals one movement step',all(t['score']==t['step'] for t in ev('quest.positions()')))
    reset(6);scores([3,7,11,15,21,25]);shot('10-six-teams')
    scores([17]*6);shot('11-six-way-tie')
    poses=ev('quest.positions().map(q=>QuestMarkers.pose(q.location,1000))')
    gaps=[math.hypot(a['x']-b['x'],a['y']-b['y'])-a['r']-b['r'] for i,a in enumerate(poses) for b in poses[i+1:]]
    check('Six-team full badge footprint clearance',min(gaps)>=0,min(gaps))
    ev('quest.score(4)');page.wait_for_timeout(150);ev('quest.score(-6)');page.wait_for_timeout(2600)
    check('Backward movement settles',ev('Math.abs(quest.positions()[0].d-quest.positions()[0].target)<0.001'))
    ev('quest.undo()');page.wait_for_timeout(2600);check('Undo restores score',ev('quest.getState().teams[0].score')==21)
    ev('quest.score(100)');page.wait_for_timeout(2600);check('Overflow score preserved, no automatic win',ev('quest.getState().teams[0].score===121 && quest.positions()[0].step===30 && !quest.getState().complete'))
    ev('for(let i=0;i<10;i++)quest.score(i%2?-2:3)');page.wait_for_timeout(2600)
    check('Rapid score reconciliation',ev('quest.getState().teams[0].score===126 && Math.abs(quest.positions()[0].d-quest.positions()[0].target)<0.001'))
    check('Route capacity locked during active game',ev('()=>{let s=quest.getState();s.stopCount=21;s.scoreAtFinish=20;try{quest.applyState(s);return false}catch(e){return true}}'))
    ev('quest.finish()');shot('12-winner');check('Explicit winner',ev('quest.getState().complete && quest.getState().winnerIds.length===1'))
    reset(6);scores([5,10,15,20,24,25]);page.set_viewport_size({'width':1280,'height':720});shot('13-720p')
    check('No browser errors',not errors,errors);check('No external runtime requests',not network,network)
    browser.close()
(ROOT/'qa-results.json').write_text(json.dumps(results,indent=2))
if not all(r['passed'] for r in results):raise SystemExit(1)
