"""Bake genuine KayKit glTF meshes to depth-tested transparent sprites.
Geometry, origin, model textures and normals come from the original glTF files.
Only selected models and rotations are embedded in the standalone runtime.
"""
import glob,json,base64,io,os,math
import numpy as np
from PIL import Image
import trimesh
from numba import njit
ROOT=os.path.dirname(os.path.abspath(__file__))
S=160; cos=.83; sin=math.sqrt(1-cos*cos); sprites={}; audit={}
layout=json.load(open(ROOT+'/layout.json')); used={}
for cell in layout['cells']:used.setdefault(cell['asset'],set()).add(cell['angle'])
for name in ['tree_single_A','tree_single_B','mountain_A','mountain_A_grass','mountain_B_grass','mountain_C_grass_trees','mountain_C','hill_single_A','rock_single_C','building_grain','building_windmill_red','building_market_red','building_castle_blue','building_tower_A_blue','building_church_red','building_tavern_red','building_blacksmith_blue','building_well_red','resource_lumber','barrel','crate_A_big']:used[name]={0}
for name in ['building_home_A_red','building_home_B_red','building_home_A_blue','wall_straight','fence_wood_straight','fence_stone_straight']:used[name]={0,90,180,270}
used['wall_straight_gate']={0};used['building_bridge_A']={60}
@njit
def raster(points,depths,colors,w,h):
 rgba=np.zeros((h,w,4),dtype=np.uint8);zbuf=np.full((h,w),-1e12,dtype=np.float32)
 for n in range(len(points)):
  ax,ay=points[n,0];bx,by=points[n,1];cx,cy=points[n,2]
  den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
  if abs(den)<1e-9:continue
  for yy in range(max(0,int(math.floor(min(ay,by,cy)))),min(h,int(math.ceil(max(ay,by,cy)))+1)):
   for xx in range(max(0,int(math.floor(min(ax,bx,cx)))),min(w,int(math.ceil(max(ax,bx,cx)))+1)):
    a=((by-cy)*(xx+.5-cx)+(cx-bx)*(yy+.5-cy))/den;b=((cy-ay)*(xx+.5-cx)+(ax-cx)*(yy+.5-cy))/den;c=1-a-b
    if min(a,b,c)<-1e-5:continue
    z=a*depths[n,0]+b*depths[n,1]+c*depths[n,2]
    if z>zbuf[yy,xx]:
     zbuf[yy,xx]=z;rgba[yy,xx,0]=colors[n,0];rgba[yy,xx,1]=colors[n,1];rgba[yy,xx,2]=colors[n,2];rgba[yy,xx,3]=255
 return rgba
for path in sorted(glob.glob(ROOT+'/assets/*.gltf')):
 name=os.path.basename(path)[:-5]; scene=trimesh.load(path,force='scene',process=False)
 audit[name]={'bounds':scene.bounds.round(4).tolist(),'meshes':len(scene.geometry),'triangles':sum(len(m.faces) for m in scene.geometry.values()),'rotationsUsed':sorted(used.get(name,set()))}
 for angle in sorted(used.get(name,set())):
  ps=[];depth=[];colors=[]
  for node in scene.graph.nodes_geometry:
   matrix,gname=scene.graph[node];m=scene.geometry[gname]
   if 'gate_door' in gname:continue
   v=trimesh.transform_points(m.vertices,matrix);x,y,z=v.T;theta=math.radians(angle);v=np.column_stack((x*np.cos(theta)+z*np.sin(theta),y,-x*np.sin(theta)+z*np.cos(theta)))
   if name.startswith('hex_'):v[:,1]*=.48
   f=m.faces;vv=v[f];normal=np.cross(vv[:,1]-vv[:,0],vv[:,2]-vv[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-9)
   camera=np.array([0,cos,sin]);keep=(normal@camera)>0.000001
   uv=m.visual.uv[f].mean(axis=1);tex=np.asarray(m.visual.material.baseColorTexture.convert('RGB'));ix=np.clip((uv[:,0]*(tex.shape[1]-1)).astype(int),0,tex.shape[1]-1);iy=np.clip(((1-uv[:,1])*(tex.shape[0]-1)).astype(int),0,tex.shape[0]-1);color=tex[iy,ix].astype(float)
   grass=(color[:,0]>90)&(color[:,1]>color[:,0]*.93)&(color[:,2]<color[:,1]*.48);color[grass]=color[grass]*[.73,.84,.95]+[14,10,43]
   green=(color[:,1]>color[:,0]*1.5)&(color[:,1]>color[:,2]*1.15);color[green]=color[green]*[.9,.85,.72]+[32,14,6]
   if name.startswith('hex_'):
    water=(color[:,2]>color[:,1]*1.03)&(color[:,2]>color[:,0]*1.35);color[water]=color[water]*[.55,.66,.47]+[40,37,35]
   light=np.array([-.55,.82,.22]);light/=np.linalg.norm(light);factor=.65+.35*np.maximum(0,normal@light);color=np.clip(color*factor[:,None]+9,0,255).astype(np.uint8)
   points=np.stack([vv[:,:,0],vv[:,:,2]*cos-vv[:,:,1]*sin],axis=-1)[keep];ps.extend(points);depth.extend((vv@camera)[keep]);colors.extend(color[keep]);
  p=np.array(ps);lo=np.floor(p.min(axis=(0,1))*S)-3;hi=np.ceil(p.max(axis=(0,1))*S)+3;w,h=(hi-lo).astype(int);px=p*S-lo
  im=Image.fromarray(raster(px,np.asarray(depth),np.asarray(colors),w,h),'RGBA');out=io.BytesIO();im.save(out,format='PNG',optimize=True);sprites[f'{name}@{angle}']={'png':base64.b64encode(out.getvalue()).decode(),'x':float(lo[0]/S),'y':float(lo[1]/S),'w':im.width/S,'h':im.height/S}
open(ROOT+'/assets.js','w').write('window.KAYKIT='+json.dumps(sprites,separators=(',',':'))+';\n');open(ROOT+'/asset-audit.json','w').write(json.dumps(audit,indent=2));print(len(sprites),'selected depth-tested sprites',os.path.getsize(ROOT+'/assets.js'))
