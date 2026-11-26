"""Bundle the approved environment with canonical interactive source. Rebuild with --bake-depth if geometry changes."""
from pathlib import Path
import json,base64,math,sys,subprocess
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;E=R.parent/'environment'; A=R/'assets';A.mkdir(exist_ok=True)
if '--bake-depth' in sys.argv:subprocess.run([sys.executable,'render_world.py','--depth-output',str(A/'scene-depth.png')],cwd=E,check=True)
if '--bake-tokens' in sys.argv:subprocess.run([sys.executable,str(R/'bake_tokens.py')],check=True)
M=json.loads((E/'map.json').read_text());L=json.loads((E/'layout.json').read_text());env=json.loads((E/'environment.json').read_text());P=env['projection'];cos=P['cos'];sin=P['sin'];oy=178;Y=.83;U=math.sqrt(3)*55/2
h=np.array(env['values']).reshape(env['height'],env['width']);bx=205+2*U*(M['bridge'][0]+(M['bridge'][1]&1)*.5);bz=82.5*M['bridge'][1]
def height(x,z):
 a=(x-env['x0'])/env['step'];b=(z-env['z0'])/env['step'];i=max(0,min(h.shape[1]-2,math.floor(a)));j=max(0,min(h.shape[0]-2,math.floor(b)));fx=max(0,min(1,a-i));fz=max(0,min(1,b-j));return (h[j,i]*(1-fx)+h[j,i+1]*fx)*(1-fz)+(h[j+1,i]*(1-fx)+h[j+1,i+1]*fx)*fz
def deck(x,z):
 u=(x-bx)/U
 if abs(z-bz)*Y>2 or abs(u)>1:return 0
 return float(np.interp(u,[v[0] for v in L['bridgeDeck']],[v[1] for v in L['bridgeDeck']]))*U
def projected(x,z,y):return [x,oy+P['offset']+z*cos-y*sin,y*cos+z*sin]
route=[];distance=0;prev=None
for a,b in zip(L['primary'],L['primary'][1:]):
 x,z=a['x'],(a['y']-oy)/Y;xx,zz=b['x'],(b['y']-oy)/Y;n=max(1,math.ceil(math.hypot(xx-x,zz-z)/2))
 for k in range(n):
  f=k/n;v=(x+(xx-x)*f,z+(zz-z)*f)
  if prev and math.hypot(v[0]-prev[0],v[1]-prev[1])<1e-5:continue
  y=height(*v)+deck(*v);world=[v[0],y,v[1]]
  if route:distance+=math.dist(world,route[-1][1:4])
  route.append([distance,*world,*projected(v[0],v[1],y)]);prev=v
last=L['primary'][-1];x,z=last['x'],(last['y']-oy)/Y;y=height(x,z)+deck(x,z);world=[x,y,z];distance+=math.dist(world,route[-1][1:4]);route.append([distance,*world,*projected(x,z,y)])
# Derive water highlights from actual visible river/coastal pixels, not a global overlay.
im=np.asarray(Image.open(E/'screenshots/01-environment.jpg').convert('RGB')).astype(int);r,g,b=im.transpose(2,0,1);water=(g>r*1.45)&(b>r*1.5)&(g>95)&(b>95)&(b>g*.9);rng=np.random.default_rng(73);glints=[]
for y in range(12,1070,9):
 for x in range(12,1910,12):
  if water[y-1:y+2,x-5:x+6].all() and rng.random()<.13:glints.append([x,y,round(float(rng.uniform(2,5)),2),round(float(rng.random()*6.28),2)])
regions={}
for name,ref in [('Willowbrook',M['route'][0]),('Golden Fields',[4,8]),('Elderwood',[3,3]),('Silverwater',M['bridge']),('Crownspine',[11,1]),('Stonehaven',[12,6]),('Royal Gate',[14,4]),('Royal Citadel',M['route'][-1])]:
 c,r=ref;x=205+2*U*(c+(r&1)*.5);z=82.5*r
 if name=='Royal Gate':x=L['gate']['x'];z=(L['gate']['y']-oy)/Y
 q=min(route,key=lambda q:(q[1]-x)**2+(q[3]-z)**2);regions[name]=round(q[0],4)
regions['Royal Citadel']=distance
# Metadata remains in world space, including depth; stops are generated at runtime.
data={'map':M['id'],'projection':P,'width':1920,'height':1080,'route':[ [round(v,5) for v in a] for a in route],'length':distance,'regions':regions,'glints':glints,'tiles':len(L['cells']),'routeCells':len(M['route']),'unmatched':L['unmatched'],'bridge':{'x':bx,'z':bz},'gate':L['gate']}
(R/'route.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
def uri(path):return 'data:image/'+('jpeg' if path.suffix=='.jpg' else 'png')+';base64,'+base64.b64encode(path.read_bytes()).decode()
assets={'background':uri(E/'screenshots/01-environment.jpg'),'depth':uri(A/'scene-depth.png'),'pawns':[uri(A/f'pawn-{i}.png') for i in range(6)],'pawnDepth':uri(A/'pawn-depth.png')}
js='window.QUEST_DATA='+json.dumps(data,separators=(',',':'))+';window.QUEST_ASSETS='+json.dumps(assets,separators=(',',':'))+';'
html=(R/'index.html').read_text().replace('<link rel="stylesheet" href="style.css">','<style>'+(R/'style.css').read_text()+'</style>').replace('<script src="data.js"></script>','<script>'+js+'</script>').replace('<script src="board.js"></script>','<script>'+(R/'board.js').read_text()+'</script>')
(R/'data.js').write_text(js);(R/'kingdom-quest.html').write_text(html);print(f'Route {distance:.2f}, {len(route)} samples, {len(glints)} glints. HTML {len(html.encode()):,} bytes')
