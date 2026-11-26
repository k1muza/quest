from pathlib import Path
from playwright.sync_api import sync_playwright
import time,json,base64,os
from PIL import Image
R=Path(__file__).resolve().parent;G=R/'gallery';checks=[];errors=[];req=[];bench=[];formats=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail});print('PASS' if ok else 'FAIL',name,detail,flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);page=b.new_page(viewport={'width':1920,'height':1080});page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:req.append(r.url) if r.url.startswith(('http:','https:')) else None)
 t=time.monotonic();page.set_content((R/'kingdom-quest.html').read_text());page.wait_for_function('window.quest?.ready && quest.cinema.state().viewReady',timeout=30000);startup=round((time.monotonic()-t)*1000)
 ev=page.evaluate
 def shot(n):page.wait_for_timeout(260);page.screenshot(path=str(G/(n+'.jpg')),type='jpeg',quality=91)
 def set_scores(scores):ev('a=>{quest.reset(a.length);let s=quest.getState();s.phase="active";s.teams.forEach((t,i)=>t.score=a[i]);quest.applyState(s,{instant:true,quiet:true})}',scores)
 set_scores([5,13,19,25,31,38]);before=ev('quest.positions().map(x=>[x.id,x.score,x.target])');shot('interactive-overview')
 for view,region in [('bridge','Silverwater'),('citadel','Royal Citadel'),('overview',None)]:
  t=time.monotonic();ev('async ([v,r])=>await quest.cinema.changeView(v,r)',[view,region]);dt=round((time.monotonic()-t)*1000)
  detail=ev('''()=>{let p=QUEST_DATA.projection,a=QUEST_DATA.route,err=Math.max(...a.map(r=>Math.abs(r[5]-(178+p.offset+r[3]*p.cos-r[2]*p.sin)))),depthErr=Math.max(...a.map(r=>Math.abs(r[6]-(r[2]*p.cos+r[3]*p.sin)))),valid=a.filter(r=>quest.sceneDepth(r[4],r[5])>-1e8).length;return {err,depthErr,valid,total:a.length,view:quest.cinema.state().view}}''');detail['switchMs']=dt
  check('projection '+view,detail['err']<1e-6 and detail['depthErr']<1e-6 and detail['valid']>detail['total']*.96 and detail['view']==view,detail)
  check('state preserved '+view,before==ev('quest.positions().map(x=>[x.id,x.score,x.target])'));shot('interactive-'+view)
 for light in ['day','morning','dusk','night','ceremony','gold']:
  ev('l=>quest.cinema.setLighting(l)',light);check('lighting '+light,ev('quest.cinema.state().lighting')==light and before==ev('quest.positions().map(x=>[x.id,x.score,x.target])'));shot('light-'+light)
 for profile,width,height,n in [('standard',1280,720,2),('enhanced',1920,1080,6),('cinematic',3840,2160,6)]:
  page.set_viewport_size({'width':width,'height':height});t=time.monotonic();ev('p=>quest.cinema.setProfile(p)',profile);switch=round((time.monotonic()-t)*1000);set_scores([5,13,19,25,31,38][:n]);ev('quest.cinema.followActive();quest.score(4)');page.wait_for_timeout(4400);m=ev('quest.metrics()');m.update({'profile':profile,'viewport':[width,height],'teams':n,'switchMs':switch,'imageWidth':ev('document.getElementById("background").naturalWidth')});bench.append(m);check('profile '+profile,ev('quest.cinema.state().profile')==profile and m['imageWidth']>0 and m['medianMs']<100,m);shot('profile-'+profile)
 page.set_viewport_size({'width':1920,'height':1080});ev('quest.cinema.setProfile("enhanced")');set_scores([19,8,15,25,30,33]);ev('quest.cinema.sequence(4)');page.wait_for_timeout(600);shot('sequence-follow');ev('''async()=>{let a=quest.cinema.changeView('bridge','Silverwater'),b=quest.cinema.changeView('citadel','Royal Citadel');for(let i=0;i<8;i++)quest.score(i%2?-1:2);await Promise.all([a,b])}''');page.wait_for_timeout(2600);check('interrupted camera and score reconciliation',ev('quest.cinema.state().view')=='citadel' and ev('quest.getState().teams[0].score')==27 and ev('quest.positions().every(p=>Math.abs(p.d-p.target)<.001)'));ev('quest.cinema.changeView("overview")');ev('quest.cinema.setAuto(true);quest.finish()');page.wait_for_timeout(1600);check('winner uses explicit authoritative winner',ev('quest.getState().winnerIds')==['team-6']);shot('sequence-finale');ev('quest.cinema.setAuto(false);quest.cinema.overview()');page.wait_for_timeout(1000);check('return to overview',abs(ev('quest.cinema.state().zoom')-1)<.001)
 for f in sorted(G.glob('resolution-*')):
  if f.suffix not in ['.jpg','.png','.webp']:continue
  mime={'.jpg':'jpeg','.png':'png','.webp':'webp'}[f.suffix];src='data:image/'+mime+';base64,'+base64.b64encode(f.read_bytes()).decode();times=ev('''async src=>{let arr=[];for(let j=0;j<3;j++){let i=new Image(),t=performance.now();i.src=src+'';await i.decode();arr.push(performance.now()-t)}return arr}''',src);w,h=Image.open(f).size;formats.append({'file':f.name,'bytes':f.stat().st_size,'width':w,'height':h,'rgbaMiB':round(w*h*4/1048576,2),'decodeMs':times})
 check('no external requests',not req,req);check('no JavaScript errors',not errors,errors);report={'checks':checks,'passed':sum(c['pass'] for c in checks),'total':len(checks),'startupMs':startup,'browser':b.version,'profiles':bench,'formats':formats,'bundleBytes':(R/'kingdom-quest.html').stat().st_size};(R/'cinematic-qa.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2));b.close()
