"""Derive tile orientations and local road centrelines from original glTF texture polygons."""
from inspect_ports import surfaces,sig,ports
from shapely.affinity import rotate
from shapely import contains_xy
from scipy.ndimage import distance_transform_edt,gaussian_filter1d
from skimage.graph import route_through_array
from pathlib import Path
import numpy as np, math, json, glob
M=json.loads(Path('map.json').read_text());R=55;Y=.83;DX=math.sqrt(3)*R;U=DX/2;OX=205;OY=178;DY=1.5*R*Y
cells={(c,r):{'c':c,'r':r,'road':set(),'river':set()} for r,(a,b) in enumerate(M['rows']) for c in range(a,b+1)}
def world(cell):c,r=cell;return np.array([OX+DX*(c+(r%2)*.5),OY+DY*r])
def port(a,b):dx,dy=(world(b)-world(a))/[1,Y];return round(math.atan2(dy,dx)/(math.pi/3))%6
paths=[M['route']]+M['secondary'];river=M['river']
for network,lines in [('road',paths),('river',[river])]:
 for path in lines:
  for a,b in zip(path,path[1:]):
   a,b=tuple(a),tuple(b);d=port(a,b);cells[a][network].add(d);cells[b][network].add((d+3)%6)
for i,j in [(0,1),(-1,-2)]:
 a,b=tuple(river[i]),tuple(river[j]);d=port(a,b);cells[a]['river'].add((d+3)%6)
variants={};geos={};audit={}
for path in sorted(glob.glob('assets/hex*.gltf')):
 name=Path(path).stem
 if not ('road_' in name or 'river_' in name) or 'sloped' in name:continue
 a,b=surfaces(path);rs,ws=sig(a),sig(b);audit[name]={'roadPorts':rs,'riverPorts':ws}
 for steps in range(6):
  road=tuple(sorted((i-steps)%6 for i in rs));water=tuple(sorted((i-steps)%6 for i in ws));key=(road,water)
  variants.setdefault(key,(name,steps*60));geos[(name,steps*60)]=(rotate(a,-steps*60,origin=(0,0)),rotate(b,-steps*60,origin=(0,0)))
print('VARIANTS',len(variants));unmatched=[]
for c,t in cells.items():
 k=(tuple(sorted(t['road'])),tuple(sorted(t['river'])));t['road']=list(k[0]);t['river']=list(k[1]);t['x'],t['y']=world(c).tolist();t['asset'],t['angle']=variants.get(k,('hex_grass',0));
 if k!=((),()) and k not in variants:unmatched.append((c,k))
print('UNMATCHED',unmatched)
# actual road/river polygon centreline. Locate the centre of the surface at each edge,
# then use a distance-to-boundary weighted geodesic. Crossings use bridge centreline.
D=150;grid=np.linspace(-1.2,1.2,D);xx,zz=np.meshgrid(grid,grid)
def local_path(t,kind,entry,exit):
 g=geos.get((t['asset'],t['angle']))
 a=ports[entry] if entry is not None else np.array([0.,0.]);b=ports[exit] if exit is not None else np.array([0.,0.]);
 if g is None or ('crossing' in t['asset'] and kind=='road'):return [a.tolist(),b.tolist()]
 poly=g[0 if kind=='road' else 1];mask=contains_xy(poly.buffer(.003),xx,zz);distance=distance_transform_edt(mask);cost=np.where(mask,1+15/(distance+1),1e6)
 def nearest(v):
  ds=(xx-v[0])**2+(zz-v[1])**2;ds[~mask]=np.inf;return np.unravel_index(np.argmin(ds),ds.shape)
 if not mask.any():return [a.tolist(),b.tolist()]
 if entry is None and not poly.covers(__import__('shapely').geometry.Point(a)):
  iy,ix=nearest(a);a=np.array([grid[ix],grid[iy]])
 if exit is None and not poly.covers(__import__('shapely').geometry.Point(b)):
  iy,ix=nearest(b);b=np.array([grid[ix],grid[iy]])
 pa,_=route_through_array(cost,nearest(a),nearest(b),fully_connected=True,geometric=True);pa=np.array(pa);vals=np.stack([grid[pa[:,1]],grid[pa[:,0]]],axis=-1);vals=gaussian_filter1d(vals,2,axis=0);vals=vals[::4];return [a.tolist(),*vals.tolist(),b.tolist()]
def transform(t,pts):return [{'x':round(t['x']+v[0]*U,3),'y':round(t['y']+v[1]*U*Y,3)} for v in pts]
def complete(path,kind):
 result=[]
 for i,c in enumerate(path):
  c=tuple(c);t=cells[c];a=port(c,path[i-1]) if i else None;b=port(c,path[i+1]) if i<len(path)-1 else None
  if kind=='river':
   if a is None:a=(b+3)%6
   if b is None:b=(a+3)%6
  pts=local_path(t,kind,a,b);t.setdefault('pathMetadata',[]).append({'kind':kind,'entry':a,'exit':b,'localXZ':pts});result+=transform(t,pts)
 return result
route=complete(M['route'],'road');secondary=[complete(a,'road') for a in M['secondary']];riverpath=complete(river,'river');bridge=cells[tuple(M['bridge'])];print('BRIDGE',bridge['asset'],bridge['angle'],bridge['road'],bridge['river']);
# Find exact gate alignment at wall y = cit.y+73. The castle courtyard overlays the actual tile geometry.
cit=world((14,3));gate_y=cit[1]+73;gate_x=cit[0]
for a,b in zip(route,route[1:]):
 if min(a['y'],b['y'])<=gate_y<=max(a['y'],b['y']) and abs(a['x']-cit[0])<115 and abs(b['x']-cit[0])<115 and a['y']!=b['y']:
  gate_x=a['x']+(b['x']-a['x'])*(gate_y-a['y'])/(b['y']-a['y']);
# Measure centreline deck elevation by barycentric vertical ray intersections on the
# original bridge mesh. Its long axis is 60 degrees in model X/Z coordinates.
import trimesh
mesh=list(trimesh.load('assets/building_bridge_A.gltf',force='scene',process=False).geometry.values())[0]
x,y,z=mesh.vertices.T;theta=math.pi/3;verts=np.stack([x*math.cos(theta)+z*math.sin(theta),y,-x*math.sin(theta)+z*math.cos(theta)],axis=1);a,b,c=verts[mesh.faces].transpose(1,0,2);normal=np.cross(b-a,c-a);aa=a[:,[0,2]];bb=b[:,[0,2]];cc=c[:,[0,2]];den=(bb[:,1]-cc[:,1])*(aa[:,0]-cc[:,0])+(cc[:,0]-bb[:,0])*(aa[:,1]-cc[:,1]);valid=np.abs(den)>1e-9;deck=[]
for xx0 in np.linspace(-1,1,41):
 w1=np.divide((bb[:,1]-cc[:,1])*(xx0-cc[:,0])+(cc[:,0]-bb[:,0])*(-cc[:,1]),den,out=np.zeros_like(den),where=valid);w2=np.divide((cc[:,1]-aa[:,1])*(xx0-cc[:,0])+(aa[:,0]-cc[:,0])*(-cc[:,1]),den,out=np.zeros_like(den),where=valid);w3=1-w1-w2;hits=valid&(w1>=-1e-5)&(w2>=-1e-5)&(w3>=-1e-5)&(normal[:,1]>0);height=w1*a[:,1]+w2*b[:,1]+w3*c[:,1];deck.append([round(float(xx0),3),round(max(0,float(height[hits].max())) if hits.any() else 0,4)])
layout={'bridgeDeck':deck,'cells':list(cells.values()),'primary':route,'secondary':secondary,'river':riverpath,'gate':{'x':gate_x,'y':gate_y},'unmatched':unmatched,'tilePortAudit':audit}
Path('map.js').write_text('window.KINGDOM='+json.dumps(M,separators=(',',':'))+';\n');Path('layout.js').write_text('window.KINGDOM_LAYOUT='+json.dumps(layout,separators=(',',':'))+';\n');Path('layout.json').write_text(json.dumps(layout,indent=2));print('gate',gate_x,gate_y,'cells',len(cells),'route points',len(route))
