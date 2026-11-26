"""Build the cinematic prototype from the unified engine with narrowly scoped presentation extensions."""
from pathlib import Path
import json,base64,sys,math,importlib.util
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent; U=R.parent/'unified'; E=R.parent/'environment';A=R/'assets'
D=json.loads((U/'route.json').read_text());b=json.loads((R/'bake-results.json').read_text());cameras=b['cameras']
def uri(p):
 return 'data:image/'+{'jpg':'jpeg','png':'png','webp':'webp'}[p.suffix[1:]]+';base64,'+base64.b64encode(p.read_bytes()).decode()
def glints(p):
 im=np.asarray(Image.open(p).resize((1920,1080)).convert('RGB')).astype(int);r,g,b=im.transpose(2,0,1);water=(g>r*1.45)&(b>r*1.5)&(g>85)&(b>85)&(b>g*.9);rng=np.random.default_rng(73);out=[]
 for y in range(12,1070,9):
  for x in range(12,1910,12):
   if water[y-1:y+2,x-5:x+6].all() and rng.random()<.11:out.append([x,y,round(float(rng.uniform(2,5)),2),round(float(rng.random()*6.28),2)])
 return out
# Each alternate angle has a fresh pawn projection and relative-depth sprite.
spec=importlib.util.spec_from_file_location('tokens',U/'bake_tokens.py');tokens=importlib.util.module_from_spec(spec);spec.loader.exec_module(tokens)
views={}
for k,p in cameras.items():
 image=A/('gold-4k.jpg' if k=='overview' else k+'.jpg');f=A/(k+'-runtime.jpg');im=Image.open(image);im.thumbnail((2560,1440));im.save(f,quality=88,optimize=True)
 if k=='overview':
  sprites=[U/'assets'/f'pawn-{i}.png' for i in range(6)];pd=U/'assets'/'pawn-depth.png'
 else:
  tokens.COS=p['cos'];tokens.SIN=p['sin'];sprites=[];pd=A/(k+'-pawn-depth.png')
  for i,c in enumerate(tokens.PALETTE):
   im,dep=tokens.bake(c);f1=A/f'{k}-pawn-{i}.png';im.save(f1);sprites.append(f1);dep.save(pd)
 views[k]={'projection':p,'background':uri(f),'depth':uri(A/(k+'-depth.png')),'pawns':[uri(s) for s in sprites],'pawnDepth':uri(pd),'glints':glints(f)}
# 4K uses WebP in the optional profile, 1440p JPEG is the compatibility fallback.
standard={'background':uri(E/'screenshots'/'01-environment.jpg'),'depth':uri(U/'assets'/'scene-depth.png'),'pawns':views['overview']['pawns'],'pawnDepth':views['overview']['pawnDepth']}
extra={'views':views,'ultra':uri(R/'gallery'/'resolution-3840.webp'),'lights':{k:uri(A/(k+'.jpg')) for k in ['day','dusk','morning','night','ceremony']},'standard':standard['background'],'standardGlints':D['glints']}
base='window.QUEST_DATA='+json.dumps(D,separators=(',',':'))+';window.QUEST_ASSETS='+json.dumps(standard,separators=(',',':'))+';window.CINEMATIC='+json.dumps(extra,separators=(',',':'))+';'
html=(U/'index.html').read_text().replace('<title>Kingdom Quest | Royal Road</title>','<title>Kingdom Quest | Cinematic Lab</title>')
html=html.replace('<div id="toast"','<div id="viewLabel" aria-live="polite" hidden></div><div id="cut" aria-hidden="true"></div><div id="toast"')
html=html.replace('<fieldset><legend>Display</legend>','''<fieldset><legend>Cinematic lab</legend><label>Quality<select id="profile"><option>standard</option><option selected>enhanced</option><option>cinematic</option></select></label><label>Lighting<select id="light"><option value="gold">Golden hour</option><option>day</option><option>morning</option><option>dusk</option><option>night</option><option>ceremony</option></select></label><label>Landmark<select id="landmark"></select></label><div class="actions"><button id="overview">Overview</button><button id="follow">Follow active</button><button id="landmarkGo">Landmark</button><button id="bridgeView">Bridge angle</button><button id="citadelView">Citadel angle</button><button id="sequence">Score sequence</button></div><label class="check"><input id="cinemaAuto" type="checkbox"> Automatic cinematic events</label></fieldset><fieldset><legend>Display</legend>''')
js=(U/'board.js').read_text();ext=(R/'cinematic.js').read_text()
# Keep base API/state unchanged. Camera functions and FX call extension hooks.
js=js.replace('fx={d:D.length,time:t,type:\'WINNER\'}','fx={d:visuals.get(win.id).target,time:t,type:\'WINNER\'}')
js=js.replace('renderHUD();return getState()','renderHUD();if(ready) cinematicEvent(prev,state,options);return getState()')
js=js.replace('function render(t){','function render(t){cinemaTick(t);')
js=js.replace('function resetCamera(){zoom=1;','function resetCamera(){cancelMotion();zoom=1;')
js=js.replace('function inspect(distance,z=2.4){let q=at(distance),','function inspect(distance,z=2.4){cancelMotion();let q=at(distance),')
js=js.replace("$('world').addEventListener('wheel',e=>{e.preventDefault();","$('world').addEventListener('wheel',e=>{cancelMotion();e.preventDefault();")
js=js.replace("$('world').addEventListener('pointerdown',e=>{if(zoom<=1)","$('world').addEventListener('pointerdown',e=>{cancelMotion();if(zoom<=1)")
# preserve exact source anchors for reproducibility
assert 'cinematicEvent(prev,state,options)' in js and 'cinemaTick(t)' in js
js=js.replace('Promise.all([load(A.background)',ext+'\nPromise.all([load(A.background)')
js=js.replace('ready=true;startedAt=now()-startedAt;requestAnimationFrame(render)','ready=true;startedAt=now()-startedAt;requestAnimationFrame(render);setProfile("enhanced").catch(console.error)')
css=(U/'style.css').read_text()+'\n'+(R/'cinematic.css').read_text()
html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>').replace('<script src="data.js"></script>','<script>'+base+'</script>').replace('<script src="board.js"></script>','<script>'+js+'</script>')
(R/'kingdom-quest.html').write_text(html);print('bundle',len(html.encode()))
