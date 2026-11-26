import trimesh,numpy as np,math,glob
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from pathlib import Path
from PIL import Image
ports=np.array([[math.cos(i*math.pi/3),math.sin(i*math.pi/3)] for i in range(6)])
def surfaces(path):
 scene=trimesh.load(path,force='scene',process=False);road=[];water=[]
 for node in scene.graph.nodes_geometry:
  mat,gname=scene.graph[node];m=scene.geometry[gname];v=trimesh.transform_points(m.vertices,mat);tri=v[m.faces];uv=m.visual.uv[m.faces].mean(axis=1);tex=np.asarray(m.visual.material.baseColorTexture.convert('RGB'));c=tex[np.clip(((1-uv[:,1])*(tex.shape[0]-1)).astype(int),0,tex.shape[0]-1),np.clip((uv[:,0]*(tex.shape[1]-1)).astype(int),0,tex.shape[1]-1)].astype(float)
  kind=(c[:,0]>c[:,1]*1.05)&(c[:,1]>c[:,2]*1.13)&(c[:,0]>140);blue=(c[:,2]>c[:,1]*1.03)&(c[:,2]>c[:,0]*1.35)
  for arr,mask in [(road,kind),(water,blue)]:
   for t in tri[mask & (np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])[:,1]>1e-6)]:
    p=Polygon(t[:,[0,2]]); 
    if p.area>1e-8:arr.append(p)
 return [unary_union(a) for a in [road,water]]
def sig(p):return [i for i,v in enumerate(ports) if p.distance(Point(v*.96))<.06] if not p.is_empty else []
if __name__=='__main__':
 for path in sorted(glob.glob('assets/hex*.gltf')):
  a,b=surfaces(path);print(Path(path).stem,sig(a),sig(b),round(a.area,2),round(b.area,2))
