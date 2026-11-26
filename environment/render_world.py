import json,math,random,sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree, Delaunay
from scipy.ndimage import gaussian_filter,distance_transform_edt
from scipy.interpolate import RegularGridInterpolator, LinearNDInterpolator
from shapely.geometry import Polygon,Point,MultiPoint,box
from shapely.ops import unary_union,triangulate
from shapely import contains_xy
from PIL import Image
import trimesh
from numba import njit
from functools import lru_cache
SAFARI='--safari' in sys.argv
OUT=Path('../maps/safari-rush') if SAFARI else Path('.')
R=55;U=math.sqrt(3)*R/2;Y=.83;W=1920;H=1080;OY=178;rng=random.Random(72839)
L=json.load(open('layout.json'));M=json.load(open('map.json'));cells=L['cells'];coords={(t['c'],t['r']):t for t in cells}
def xz(v):return np.array([v['x'],(v['y']-OY)/Y])
def pos(c,r):return xz(coords[c,r])
def dense(a,step=2):
 p=np.array([xz(v) for v in a]);out=[]
 for u,v in zip(p,p[1:]):
  n=max(1,int(np.ceil(np.linalg.norm(v-u)/step)));out.extend(u+(v-u)*np.arange(n)[:,None]/n)
 return np.vstack([out,p[-1]])
rt=cKDTree(np.concatenate([dense(a) for a in [L['primary'],*L['secondary']]]));wt=cKDTree(dense(L['river']))
land=unary_union([Polygon([(x+R*math.cos(math.radians(i*60-90)),z+R*math.sin(math.radians(i*60-90))) for i in range(6)]).buffer(.02) for x,z in map(xz,cells)]);shore=land.buffer(42,quad_segs=12).buffer(-25,quad_segs=12);outer=shore.buffer(18,quad_segs=12).buffer(15,quad_segs=10).buffer(-15,quad_segs=10)
xs=np.arange(0,1921,4);zs=np.arange(-120,941,4);X,Z=np.meshgrid(xs,zs);grid=np.stack([X,Z],-1);D=wt.query(grid)[0];RD=rt.query(grid)[0];coast=distance_transform_edt(contains_xy(land,X,Z))*4
cx,cz=pos(14,3);gx,gz=xz(L['gate'])
def bump(x,z,wx,wz,a):return a*np.exp(-((X-x)/wx)**2-((Z-z)/wz)**2)
height=10+bump(480,160,310,245,38)+bump(550,530,260,250,25)+bump(1170,100,320,160,60)+bump(1230,260,220,140,32)+bump(1430,535,260,215,17)
for x,z,a,wx,wz in [(1000,12,90,62,90),(1090,9,125,72,95),(1180,5,160,75,104),(1260,10,120,75,95),(1340,15,82,70,90),(1120,202,77,64,70),(1205,225,99,70,80),(1280,220,58,65,71)]:height+=bump(x,z,wx,wz,a)
if SAFARI:
 height=10+bump(480,530,290,190,13)+bump(570,110,104,85,108)+bump(665,140,92,100,90)+bump(450,65,75,90,65)+bump(970,90,100,120,75)+bump(1300,270,220,170,22)
height*=.60+.40*np.clip(RD/65,0,1);height*=.35+.65*np.clip(coast/65,0,1);height+=2
plateau=np.maximum(np.abs(X-cx)-110,np.maximum(cz-142-Z,Z-(gz+7)));f=np.clip(1-plateau/120,0,1);f=f*f*(3-2*f);height=height*(1-f)+76*f
f=np.clip((D-24)/67,0,1);f=f*f*(3-2*f);height=4+(height-4)*f;height=gaussian_filter(height,1)
# Angular rock relief is limited to high mountain ground, outside the road corridor.
rockmask=np.clip((height-74)/55,0,1)*np.clip((RD-29)/36,0,1)*(X>865)*(X<1400)*(Z<335)
height+=rockmask*(12*np.sin(X*.087+Z*.031)+9*np.sin(Z*.111-X*.052)+5*np.cos(X*.145+Z*.098))
# Calibrate the original primary road elevation by arc distance. Limit grade to 26%,
# then blend the smoothed profile into a generous shoulder around the road.
from scipy.ndimage import gaussian_filter1d
pr=dense(L['primary']);pr=pr[np.r_[True,np.linalg.norm(np.diff(pr,axis=0),axis=1)>.01]]
sample=RegularGridInterpolator((zs,xs),height,bounds_error=False,fill_value=4)
ph=sample(pr[:,::-1]);ph=gaussian_filter1d(ph,3);ds=np.linalg.norm(np.diff(pr,axis=0),axis=1);arc=np.r_[0,np.cumsum(ds)]
# Gate and courtyard are anchored at plateau height. Raise the ceremonial approach gradually.
bi=pos(*M['bridge']);nearbridge=(np.abs(pr[:,0]-bi[0])<=U+1)&(np.abs(pr[:,1]-bi[1])<4);gateidx=np.argmin(np.linalg.norm(pr-[gx,gz],axis=1));ph=np.maximum(ph,76-.25*np.abs(arc-arc[gateidx]));ph[gateidx:]=76;ph[nearbridge]=4
for _ in range(3):
 for i in range(1,len(ph)):ph[i]=min(ph[i],ph[i-1]+.25*ds[i-1])
 for i in range(len(ph)-2,-1,-1):ph[i]=min(ph[i],ph[i+1]+.25*ds[i])
pd,pi=cKDTree(pr).query(grid);blend=np.exp(-(pd/22)**4);height=height*(1-blend)+ph[pi]*blend
# Keep the river and bridge footprint level, including both abutments.
height=np.where(D<23,4,height);bridgeMask=(np.abs(X-bi[0])<U+2)&(np.abs(Z-bi[1])<15);height=np.where(bridgeMask,4,height)
height=gaussian_filter(height,.6)
# Faceted rock geology: irregular sample lattice creates connected angular planar faces.
# Road shoulder, river and coastline are held fixed; the original road profile is authoritative.
rrng=np.random.default_rng(9183)
px,pz=np.meshgrid(np.arange(825,1475,21),np.arange(-100,365,21));rp=np.column_stack([px.ravel(),pz.ravel()]).astype(float);rp+=rrng.uniform(-8,8,rp.shape)
orig=RegularGridInterpolator((zs,xs),height,bounds_error=False,fill_value=4)
rv=orig(rp[:,::-1]);rv+=rrng.uniform(-17,17,len(rv))+12*np.sin(rp[:,0]*.065+rp[:,1]*.035)
rocktri=Delaunay(rp);facet=LinearNDInterpolator(rocktri,rv)(X,Z);facet=np.where(np.isfinite(facet),facet,height)
rockweight=np.clip((height-55)/45,0,1)*np.clip((RD-29)/23,0,1)*np.clip((D-35)/25,0,1)*np.clip(coast/25,0,1)*(X>875)*(X<1400)*(Z<325)
height=height*(1-rockweight)+facet*rockweight
if SAFARI:
 # The upstream Zambezi is elevated; a short, steep continuous spillway
 # drops into the lower river. The bridge remains on the lower reach.
 riverlevel=4+59*np.clip((113-Z)/17,0,1)
 blendwater=np.clip((68-D)/45,0,1)
 height=height*(1-blendwater)+riverlevel*blendwater
 height=np.where(D<23,riverlevel,height)
hf=RegularGridInterpolator((zs,xs),height,bounds_error=False,fill_value=4)
def elev(x,z):return float(hf((z,x)))
def ea(x,z):return hf(np.stack([z,x],-1))
tri=[];cols=[];placements=[];river_faces=[];farm_footprints=[];farm_stats={"candidates":0,"trimmed":0,"rejected":0}
def push(v,c):
 v=np.asarray(v,float).reshape(-1,3,3);tri.append(v);cols.append(np.broadcast_to(c,(len(v),3)).copy())
@lru_cache(None)
def model(name):
 s=trimesh.load('assets/'+name+'.gltf',force='scene',process=False);vs=[];cs=[]
 for node in s.graph.nodes_geometry:
  mat,k=s.graph[node];m=s.geometry[k]
  if 'gate_door' in k:continue
  v=trimesh.transform_points(m.vertices,mat)[m.faces];uv=m.visual.uv[m.faces].mean(axis=1);tex=np.asarray(m.visual.material.baseColorTexture.convert('RGB'));c=tex[np.clip(((1-uv[:,1])*(tex.shape[0]-1)).astype(int),0,tex.shape[0]-1),np.clip((uv[:,0]*(tex.shape[1]-1)).astype(int),0,tex.shape[1]-1)].astype(float);vs.extend(v);cs.extend(c)
 return np.array(vs),np.array(cs)
def rot(v,a):
 x,y,z=v.transpose(2,0,1);a=math.radians(a);return np.stack([x*np.cos(a)+z*np.sin(a),y,-x*np.sin(a)+z*np.cos(a)],-1)
def asset(name,x,z,s=1,a=0,sy=1,base=None,conform=False):
 v,c=model(name);v=rot(v,a)*U*s;v[:,:,1]*=sy;v[:,:,0]+=x;v[:,:,2]+=z
 if conform:v[:,:,1]+=ea(v[:,:,0],v[:,:,2])
 else:v[:,:,1]+=elev(x,z) if base is None else base
 c=c.copy();green=(c[:,1]>c[:,0]*1.4)&(c[:,1]>c[:,2]*1.2);c[green]=c[green]*[.82,.84,.83]+[10,10,8];push(v,c);placements.append(dict(asset=name,x=round(x,2),z=round(z,2),scale=s,rotation=a,elevation=round(elev(x,z) if base is None else base,2)))
def subdiv(v,c,n=3):
 for _ in range(n):
  a,b,d=v.transpose(1,0,2);ab=(a+b)/2;bd=(b+d)/2;da=(d+a)/2;v=np.concatenate([np.stack([a,ab,da],1),np.stack([ab,b,bd],1),np.stack([da,bd,d],1),np.stack([ab,bd,da],1)]);c=np.tile(c,(4,1))
 return v,c
# Actual KayKit road and river top faces warped into shared heightfield.
for t in cells:
 x,z=xz(t);v,c=model(t['asset']);v=rot(v,t['angle']);n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);mask=n[:,1]>1e-8;v,c=subdiv(v[mask],c[mask]);v*=U;v[:,:,0]+=x;v[:,:,2]+=z
 grass=(c[:,1]>c[:,0]*.93)&(c[:,2]<c[:,1]*.48);water=(c[:,2]>c[:,1]*1.03)&(c[:,2]>c[:,0]*1.35);road=(c[:,0]>c[:,1]*1.05)&(c[:,1]>c[:,2]*1.13)&(c[:,0]>140)
 v[:,:,1]=ea(v[:,:,0],v[:,:,2])+v[:,:,1]*.25;center=v.mean(1);e=center[:,1];farm=x<850 and z>450 and x>425;forest=x<850 and z<455
 base=np.array([94,137,71] if forest else [156,155,83] if farm else [120,156,82]);noise=4*np.sin(center[:,0]*.047)+3*np.cos(center[:,2]*.035);c[grass]=base+noise[grass,None];rocky=grass&(e>63)&(center[:,0]>875)&(center[:,0]<1400)&(center[:,2]<325);ids=rocktri.find_simplex(center[rocky][:,[0,2]]);shade=(((ids*37)%23)-11)*1.8;stone=np.array([123,132,139])+shade[:,None]+6*np.sin(center[rocky,0:1]*.055);f=np.clip((e[rocky]-63)/15,0,1);c[rocky]=c[rocky]*(1-f[:,None])+stone*f[:,None];c[road]=[184,151,100];c[water]=[49,145,155];
 if SAFARI:
  # Region-specific ground material and exposed granite, not dirt mountains.
  dry=np.array([180,161,88]);green=np.array([111,138,76]);wet=np.clip((80-wt.query(center[:,[0,2]])[0])/60,0,1)
  c[grass]=dry+(green-dry)*wet[grass,None]+noise[grass,None]
  rock=grass&(((center[:,0]<820)&(center[:,2]<230)&(e>38))|((wt.query(center[:,[0,2]])[0]<75)&(center[:,2]<160)&(e>25)))
  c[rock]=np.array([139,137,128])+noise[rock,None]*2
  c[road]=[194,151,94]
  c[water]=[39,140,153]
  falls=water&(center[:,2]>96)&(center[:,2]<113);c[falls]=[190,225,222]
 c[water & (np.sin(center[:,0]*.081+center[:,2]*.015)>.8)]=[65,157,161];river_faces.extend(Polygon(f[:,[0,2]]) for f in v[water] if Polygon(f[:,[0,2]]).area>1e-7);push(v,c)
river_polygon=unary_union(river_faces);farm_exclusion=river_polygon.buffer(9.01,quad_segs=64);
def ribbon(a,b,color):
 diff=b.difference(a)
 for t in triangulate(diff):
  if not diff.covers(t.representative_point()) or t.difference(diff).area>1:continue
  p=np.array(t.exterior.coords[:3]);h=np.array([max(-4,elev(*v)*max(0,1-land.distance(Point(v))/16)-land.distance(Point(v))*.35) for v in p]);push(np.stack([p[:,0],h,p[:,1]],1),color)
ribbon(land,shore,[199,178,120]);ribbon(shore,outer,[69,154,155])
# Open the river mouths into the surrounding ocean; no sand bar across the channel.
for end,near in [(xz(L['river'][0]),xz(L['river'][5])),(xz(L['river'][-1]),xz(L['river'][-6]))]:
 d=end-near;d=d/np.linalg.norm(d);n=np.array([-d[1],d[0]])*12;a=end-d*4;b=end+d*39;p=np.array([a+n,a-n,b-n,b+n]);v=np.column_stack([p[:,0],np.ones(4)*(elev(*end)+.3 if SAFARI else 4.3),p[:,1]]);push(v[[[0,2,1],[0,3,2]]],[49,145,155])
bx,bz=pos(*M['bridge']);asset('building_bridge_A',bx,bz,1,60,base=4)
def surface(x,z,w,d,color,offset=.9):
 a=np.array([[x-w/2,z-d/2],[x+w/2,z-d/2],[x+w/2,z+d/2],[x-w/2,z+d/2]]);v=np.column_stack([a[:,0],ea(a[:,0],a[:,1])+offset,a[:,1]]);push(v[[[0,2,1],[0,3,2]]],color)
def pathstrip(a,b,w,color,offset=1.5):
 a,b=np.array(a),np.array(b);d=b-a;n=np.array([-d[1],d[0]])/max(np.linalg.norm(d),.001)*w/2;p=np.array([a+n,a-n,b-n,b+n]);v=np.column_stack([p[:,0],ea(p[:,0],p[:,1])+offset,p[:,1]]);push(v[[[0,2,1],[0,3,2]]],color)
occupied=[];inside=land.buffer(-10)
def available(x,z,r=18,road=20,water=30):return inside.covers(Point(x,z)) and rt.query([x,z])[0]>road+r*.25 and wt.query([x,z])[0]>water and not(abs(x-cx)<122 and cz-155<z<gz+15) and all(math.hypot(x-a,z-b)>r+rr for a,b,rr in occupied)
def place(name,x,z,s=1,a=0,r=18,road=20,water=30):
 if not available(x,z,r,road,water):return False
 occupied.append((x,z,r));asset(name,x,z,s,a);return True
def house(x,z,s=.9,a=0,blue=False,kind=False):return place('building_home_A_blue' if blue else 'building_home_B_red' if kind else 'building_home_A_red',x,z,s,a,15*s,19)
if SAFARI:
 from safari_scene import build
 build(globals())
else:
 # civic sites, frontage blocks and field bands precede vegetation.
 for c,r,dx,dz,name,s in [(13,8,0,0,'building_market_red',.88),(10,8,-4,8,'building_church_red',.92),(12,5,0,0,'building_tavern_red',.87),(15,7,-9,3,'building_blacksmith_blue',.8),(1,7,-15,-5,'building_well_red',.75)]:
  x,z=pos(c,r)+[dx,dz]
  if available(x,z,24,18):
   surface(x,z,76,66,[192,181,151]);place(name,x,z,s,0,23,18)
   # stone paver bands around public buildings
   for k in range(5):surface(x-30+k*15,z+27,12,5,[165,157,131],1.5)
 # Reserve two explicit civic courts before placing frontage houses.
 for x,z,name,s,w,d in [(555,620,'building_well_red',.62,48,43),(550,540,'building_market_red',.48,50,45),(1490,505,'building_well_red',.72,65,65)]:
  if available(x,z,19,15):
   for j in range(int(d//9)):
    for k in range(int(w//10)):
     surface(x-w/2+5+k*10,z-d/2+4.5+j*9,9.6,8.6,[192+(k+j)%3*5,180+(k+j)%3*4,150+(k+j)%3*3],1.2)
   place(name,x,z,s,0,20,15)
   # two ped approaches join the nearest road centreline.
   road=rt.data[rt.query([x,z])[1]];direction=road-[x,z];end=np.array([x,z])+direction/np.linalg.norm(direction)*min(w,d)*.42
   for a,b in zip(np.linspace(end,road,8),np.linspace(end,road,8)[1:]):pathstrip(a,b,6,[183,165,129],1.3)
 for r,cs in [(7,range(10,15)),(5,range(10,15)),(8,range(10,15)),(6,range(10,15)),(8,range(1,4)),(7,range(1,3)),(9,range(1,3))]:
  for c in cs:
   if (c,r) not in coords:continue
   x,z=pos(c,r)
   for dx,dz,a in [(-24,-31,0),(24,-31,0),(-24,31,180),(24,31,180)]:
    xx,zz=x+dx,z+dz;s=.84 if c>9 else .76
    if house(xx,zz,s,a,blue=(c+r)%4==0,kind=(c+r)%3==0):surface(xx,zz,31,33,[154,150,110],.45)
 # Complete polygon footprints, including crop strips and actual model triangles.
 def farm_surface(poly,color,offset):
  for t in triangulate(poly):
   if not poly.covers(t) or t.area<.001:continue
   a=np.array(t.exterior.coords[:3]);push(np.column_stack([a[:,0],ea(a[:,0],a[:,1])+offset,a[:,1]]),color)
 def farm_model(name,x,z,s,a=0,sy=1,conform=False):
  v,_=model(name);v=rot(v,a)*U*s;v[:,:,0]+=x;v[:,:,2]+=z
  footprint=MultiPoint(v[:,:,[0,2]].reshape(-1,2)).convex_hull
  if not inside.covers(footprint) or footprint.intersects(farm_exclusion):return False
  farm_footprints.append((name,footprint));asset(name,x,z,s,a,sy=sy,conform=conform);return True
 for c,r in [(4,8),(5,8),(6,7),(5,7),(5,9),(4,10),(5,10),(6,9),(3,9),(4,7),(6,8),(3,10)]:
  x,z=pos(c,r)
  for dx,dz in [(-24,-22),(24,-22),(-24,22),(24,22)]:
   xx,zz=x+dx,z+dz
   if available(xx,zz,18,19,29):
    farm_stats['candidates']+=1;original=box(xx-21,zz-19,xx+21,zz+19);plot=original.intersection(inside).difference(farm_exclusion)
    if plot.area<original.area*.35:farm_stats['rejected']+=1;continue
    if plot.area<original.area-.01:farm_stats['trimmed']+=1
    farm_footprints.append(('field',plot));farm_surface(plot,[150,115,65],.7)
    for i in range(5):
     sx=xx-16+i*8;strip=box(sx-1.5,zz-16.5,sx+1.5,zz+16.5).intersection(plot)
     if not strip.is_empty:farm_surface(strip,[212,172,73] if (c+r)%3 else [114,145,65],1.6);farm_footprints.append(('crop',strip))
    if (c+r)%3==0:farm_model('building_grain',xx,zz,.39,sy=.75,conform=True)
    occupied.append((xx,zz,17))
 for c,r in [(5,7),(6,8),(4,9),(3,10),(6,10)]:
  x,z=pos(c,r)
  for dx,dz in [(25,-23),(-25,23),(0,0)]:
   xx,zz=x+dx,z+dz
   if available(xx,zz,20,18) and farm_model('building_windmill_red',xx,zz,.8):occupied.append((xx,zz,20));break
 # Geometric validation applies to the full rendered footprint, not its centre.
 from shapely.geometry import mapping
 farm_stats.update(footprints=len(farm_footprints),min_clearance=min(p.distance(river_polygon) for _,p in farm_footprints),river_intersection_area=sum(p.intersection(river_polygon).area for _,p in farm_footprints),bank_intersection_area=sum(p.intersection(farm_exclusion).area for _,p in farm_footprints),required_clearance=9)
 assert farm_stats['min_clearance']>=8.999 and farm_stats['river_intersection_area']<1e-6 and farm_stats['bank_intersection_area']<1e-6,farm_stats
 json.dump(farm_stats,open('farm-validation.json','w'),indent=2)
 json.dump({'river':mapping(river_polygon),'clearance':9,'footprints':[{'kind':k,'geometry':mapping(p)} for k,p in farm_footprints]},open('farm-footprints.json','w'),separators=(',',':'))
 # Village common and market plaza, aligned to local street.
 for c,r,dx,dz in [(1,7,12,7),(13,8,28,12)]:
  x,z=pos(c,r)+[dx,dz]
  if available(x,z,18,13):surface(x,z,40,40,[197,183,147]);place('building_well_red',x,z,.58,0,15,13)
 for c,r in [(13,8),(12,5),(10,8),(1,7),(5,8),(4,9)]:
  x,z=pos(c,r)
  for k in range(12):
   xx,zz=x+rng.uniform(-46,46),z+rng.uniform(-37,37)
   if place(rng.choice(['barrel','crate_A_big','resource_lumber']),xx,zz,.75,0,6,16):break
 # Fences and trees flank the river where space is available; retain the open crossing.
 for c,r in [(6,1),(7,5),(8,7),(7,9),(6,10),(9,6),(5,9)]:
  if (c,r) not in coords:continue
  x,z=pos(c,r)
  for j in range(8):
   xx=x+rng.uniform(-38,38);zz=z+rng.uniform(-35,35)
   if 25<wt.query([xx,zz])[0]<54 and place('rock_single_C',xx,zz,.65,rng.randrange(360),7,18,24):break
 for t in cells:
  x,z=xz(t);c,r=t['c'],t['r'];forest=c<=6 and r<=5;ridge=8<=c<=12 and r<=3;meadow=c in [7,8,9] or r>=9;n=29 if forest else 12 if ridge else 6 if meadow else 2
  for k in range(n):
   a=rng.random()*math.tau;rr=math.sqrt(rng.random())*45;xx=x+math.cos(a)*rr;zz=z+math.sin(a)*rr;h=elev(xx,zz)
   if ridge and h>72:continue
   s=rng.uniform(.65,1.18) if forest else rng.uniform(.45,.85)
   if forest and 395<xx<470 and 100<zz<170:continue
   place('tree_single_A' if rng.random()<.69 else 'tree_single_B',xx,zz,s,rng.randrange(360),10*s,20,25)
 # Irregular rock formations: use the original KayKit rocks rather than stacked hex mountains.
 for x,z in [(1040,35),(1100,5),(1180,12),(1240,15),(1300,40),(1120,210),(1200,230),(1275,225)]:
  for k in range(6):
   xx=x+rng.uniform(-29,29);zz=z+rng.uniform(-27,27)
   if rt.query([xx,zz])[0]>35 and inside.covers(Point(xx,zz)):
    # Consume the historical random draws but omit protruding peak props.
    size,angle,sy=rng.uniform(.9,2.2),rng.uniform(0,360),rng.uniform(1,2.4)
    if elev(xx,zz)<65 and rt.query([xx,zz])[0]>45:asset('rock_single_C',xx,zz,size*.65,angle,sy=.7)
 for t in cells:
  x,z=xz(t)
  if land.boundary.distance(Point(x,z))<57 and rng.random()<.58:place('rock_single_C',x+rng.uniform(-18,18),z+rng.uniform(-18,18),rng.uniform(.55,1.3),rng.randrange(360),9,18,25)
 # Royal complex on level plateau with supporting wings and gardens.
 left,right=cx-101,cx+101;back=cz-132;front=gz;surface(cx,(back+front)/2,right-left,front-back,[190,181,151],1)
 for a,b in [((left,back),(right,back)),((left,back),(left,front)),((right,back),(right,front)),((left,front),(gx-33,front)),((gx+33,front),(right,front))]:
  a,b=np.array(a),np.array(b);n=max(1,round(np.linalg.norm(b-a)/62))
  for j in range(n):
   x,z=a+(b-a)*(j+.5)/n;asset('wall_straight',x,z,np.linalg.norm(b-a)/n/(2*U),0 if abs(b[0]-a[0])>abs(b[1]-a[1]) else 90,base=76)
 asset('wall_straight_gate',gx,front,66/(2*U),0,base=76)
 for x,z in [(left,back),(right,back),(left,front),(right,front)]:asset('building_tower_A_blue',x,z,.67,0,base=76)
 asset('building_castle_blue',cx,cz-77,.94,0,base=76)
 for s in [-1,1]:
  x=cx+s*69;z=cz-3;asset('building_home_A_blue',x,z,.75,0,base=76);surface(x,z+42,46,31,[103,145,77],1.4)
  for dx in [-13,13]:asset('tree_single_B',x+dx,z+43,.45,0,base=76)
 asset('building_well_red',cx+44,cz+38,.65,0,base=76)
 # ceremonial central avenue follows the original route through the gate.
 from shapely.geometry import LineString
 courtline=LineString(pr[gateidx:]).buffer(8,cap_style=1,join_style=1)
 for t in triangulate(courtline):
  if not courtline.covers(t.representative_point()):continue
  p=np.array(t.exterior.coords[:3]);push(np.column_stack([p[:,0],np.full(3,78.5),p[:,1]]),[161,144,108])
 # court landscaping: ornamental cypress pairs, stone garden edging and paving strips.
 for x in [cx-42,cx+42]:
  for z in [cz-25,cz+2]:
   if rt.query([x,z])[0]>17:asset('tree_single_A',x,z,.42,0,base=76)
 for x in [cx-72,cx+72]:
  for z in [cz+22,cz+54]:surface(x,z,45,3,[151,142,109],2)
 # timber dock and hull, original compatible geometry.
 def cube(x,z,w,d,h,base,color):
  a=np.array([[x-w/2,base,z-d/2],[x+w/2,base,z-d/2],[x+w/2,base,z+d/2],[x-w/2,base,z+d/2]]);v=np.vstack([a,a+[0,h,0]]);push(v[[[4,6,5],[4,7,6],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]],color)
 for x in [345,390]:
  bounds=[zz for zz in np.arange(550,950,2) if land.covers(Point(x,zz))]
  if not bounds:continue
  z=max(bounds)-3
  for j in range(13):cube(x,z+j*5,17,4.7,2,3,[139,100,65])
  for j in [0,5,10]:
   for dx in [-7,7]:cube(x+dx,z+j*5,3,3,11,-4,[104,76,51])
  p=np.array([[x+22,z+17],[x+31,z+24],[x+31,z+45],[x+22,z+53],[x+13,z+45],[x+13,z+24]]);v=np.column_stack([p[:,0],np.ones(6)*2,p[:,1]]);top=v+[0,5,0];center=top.mean(0);center[1]-=3
  for i in range(6):
   j=(i+1)%6;push([v[i],top[i],top[j]],[111,75,43]);push([v[i],top[j],v[j]],[111,75,43]);push([top[i],center,top[j]],[185,143,83])

V=np.concatenate(tri);C=np.concatenate(cols);norm=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]);norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-9);norm[norm[:,1]<0]*=-1
print('triangles',len(V),'placements',len(placements),flush=True)
@njit(cache=True)
def depth_raster(p,d,w,h):
 zb=np.full((h,w),-1e9,np.float32)
 for i in range(len(p)):
  ax,ay=p[i,0];bx,by=p[i,1];cx,cy=p[i,2];den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
  if abs(den)<1e-9:continue
  for y in range(max(0,int(math.floor(min(ay,by,cy)))),min(h,int(math.ceil(max(ay,by,cy)))+1)):
   for x in range(max(0,int(math.floor(min(ax,bx,cx)))),min(w,int(math.ceil(max(ax,bx,cx)))+1)):
    a=((by-cy)*(x+.5-cx)+(cx-bx)*(y+.5-cy))/den;b=((cy-ay)*(x+.5-cx)+(ax-cx)*(y+.5-cy))/den;c=1-a-b
    if min(a,b,c)<-1e-5:continue
    z=a*d[i,0]+b*d[i,1]+c*d[i,2]
    if z>zb[y,x]:zb[y,x]=z
 return zb
@njit(cache=True)
def render(p,d,sp,sd,colors,dark,shadow,w,h):
 zb=np.full((h,w),-1e9,np.float32);out=np.zeros((h,w,4),np.uint8)
 for i in range(len(p)):
  ax,ay=p[i,0];bx,by=p[i,1];cx,cy=p[i,2];den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
  if abs(den)<1e-9:continue
  for y in range(max(0,int(math.floor(min(ay,by,cy)))),min(h,int(math.ceil(max(ay,by,cy)))+1)):
   for x in range(max(0,int(math.floor(min(ax,bx,cx)))),min(w,int(math.ceil(max(ax,bx,cx)))+1)):
    a=((by-cy)*(x+.5-cx)+(cx-bx)*(y+.5-cy))/den;b=((cy-ay)*(x+.5-cx)+(ax-cx)*(y+.5-cy))/den;c=1-a-b
    if min(a,b,c)<-1e-5:continue
    z=a*d[i,0]+b*d[i,1]+c*d[i,2]
    if z<=zb[y,x]:continue
    zb[y,x]=z;sx=int(a*sp[i,0,0]+b*sp[i,1,0]+c*sp[i,2,0]);sy=int(a*sp[i,0,1]+b*sp[i,1,1]+c*sp[i,2,1]);sz=a*sd[i,0]+b*sd[i,1]+c*sd[i,2];occ=0
    for dy in (-3,0,3):
     for dx in (-3,0,3):
      xx=sx+dx;yy=sy+dy
      if 0<=xx<shadow.shape[1] and 0<=yy<shadow.shape[0] and shadow[yy,xx]>sz+2.7:occ+=1
    f=occ/9
    for k in range(3):out[y,x,k]=int(max(0,min(255,colors[i,k]*(1-f)+dark[i,k]*f)))
    out[y,x,3]=255
 return out

def bake(name,cos,light,offset=100,ss=1.5):
 sin=math.sqrt(1-cos*cos);light=np.array(light,float);light/=np.linalg.norm(light);right=np.cross([0,1,0],light);right/=np.linalg.norm(right);up=np.cross(light,right);sp=np.stack([V@right,V@up],-1);lo=sp.min((0,1))-8;sp=(sp-lo)*1.5;size=np.ceil(sp.max((0,1))+8).astype(int);sd=V@light;shadow=depth_raster(sp,sd,*size)
 diffuse=np.maximum(0,norm@light);color=np.clip(C*(.64+.45*diffuse[:,None])*[1.09,1.035,.97]+[7,6,5],0,255);dark=np.clip(C*[.55,.65,.72]+[9,13,16],0,255)
 p=np.stack([V[:,:,0],OY+offset+V[:,:,2]*cos-V[:,:,1]*sin],-1)*ss;d=V@np.array([0,cos,sin]);im=Image.fromarray(render(p,d,sp,sd,color,dark,shadow,int(W*ss),int(H*ss)),'RGBA').resize((W,H),Image.Resampling.LANCZOS)
 yy,xx=np.mgrid[:H,:W];v=np.clip(1-np.sqrt(((xx-W*.49)/(W*.75))**2+((yy-H*.45)/(H*.92))**2),0,1);base=np.stack([18+23*v,65+47*v,83+44*v],-1);base+=(np.sin(xx*.031+yy*.071)*.8+np.cos(xx*.009-yy*.019)*1.2)[:,:,None];bg=Image.fromarray(np.uint8(np.clip(base,0,255)),'RGB').convert('RGBA');bg.alpha_composite(im);bg.convert('RGB').save(name,quality=96);print(name,flush=True);return {'cos':cos,'sin':sin,'offset':offset}
# Optional depth-only export for the unified interactive board. Existing bakes are unchanged.
if '--depth-output' in sys.argv:
 output=Path(sys.argv[sys.argv.index('--depth-output')+1]);cos=.76;sin=math.sqrt(1-cos*cos)
 p=np.stack([V[:,:,0],OY+105+V[:,:,2]*cos-V[:,:,1]*sin],-1)
 d=V@np.array([0,cos,sin]);zb=depth_raster(p,d,W,H)
 # RG 16-bit fixed point. Zero = empty background; valid depth is (code-1)/32-128.
 q=np.where(zb>-1e8,np.clip(np.rint((zb+128)*32)+1,1,65535),0).astype(np.uint16)
 rgb=np.zeros((H,W,3),np.uint8);rgb[:,:,0]=q>>8;rgb[:,:,1]=q&255
 output.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(rgb).save(output,optimize=True)
 print('Depth map:',output,flush=True);sys.exit(0)
(OUT/'screenshots').mkdir(parents=True,exist_ok=True)
variants=[('screenshots/01-environment.jpg',.76,[-.65,.82,.42],105),('screenshots/camera-02.jpg',.68,[-.70,.73,-.25],135),('screenshots/camera-03.jpg',.84,[-.35,.91,.3],65)]
if '--one' in sys.argv:variants=variants[:1]
if SAFARI:variants=[(str(OUT/'screenshots/01-environment.jpg'),.76,[-.65,.82,.42],105)]
configs=[bake(*v) for v in variants];json.dump({'step':4,'x0':float(xs[0]),'z0':float(zs[0]),'width':len(xs),'height':len(zs),'values':height.round(2).ravel().tolist(),'projection':configs[0],'placements':placements},open(OUT/'environment.json','w'),separators=(',',':'));json.dump(configs,open(OUT/'camera-configs.json','w'))
