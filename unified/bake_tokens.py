"""Original lathed, faceted collectible pawns; no third-party asset dependency.
The colour sprite and per-pixel relative camera depth share an exact projection.
"""
from pathlib import Path
import numpy as np, math
from PIL import Image
ROOT=Path(__file__).resolve().parent
S=2; W=56; H=96; AX=28; AY=82
COS=.76; SIN=math.sqrt(1-COS*COS)
PALETTE=['#c83f38','#287dc5','#d6a137','#8256bb','#288b64','#d85a9a']
# radius, height, material: foot, enamel stem, collar, polished finial
profile=[(0,0,0),(9.8,0,0),(11,1.6,0),(11,3.7,0),(9.8,5.2,1),(8.8,6.8,1),(7.7,8,0),(5.5,11,1),(4.0,19,1),(5.6,23,0),(7.1,25,0),(7.3,27,1),(5.5,28,1),(7.4,30.5,1),(8.4,34.5,1),(7.0,38.1,1),(3.6,40.5,1),(0,41,1)]
light=np.array([-.65,.82,.42]);light/=np.linalg.norm(light)
def bake(hexcolor):
 rgb=np.array([int(hexcolor[i:i+2],16) for i in (1,3,5)]); gold=np.array([213,177,100]); N=18; tris=[];cols=[]
 for (r,h,m),(r2,h2,m2) in zip(profile,profile[1:]):
  for j in range(N):
   a,b=[2*math.pi*k/N for k in (j,j+1)];v=np.array([[r*math.cos(a),h,r*math.sin(a)],[r*math.cos(b),h,r*math.sin(b)],[r2*math.cos(b),h2,r2*math.sin(b)],[r2*math.cos(a),h2,r2*math.sin(a)]])
   for q in [[0,1,2],[0,2,3]]:
    t=v[q];n=np.cross(t[1]-t[0],t[2]-t[0]);norm=np.linalg.norm(n)
    if norm<1e-8:continue
    n/=norm
    if np.dot(n,t.mean(0)-[0,t.mean(0)[1],0])<0:n=-n
    dif=max(0,np.dot(n,light));spec=max(0,np.dot(n,(light+np.array([0,COS,SIN]))/np.linalg.norm(light+np.array([0,COS,SIN]))))**14
    cols.append(np.clip((gold if m==0 else rgb)*(.57+.62*dif)+[8,9,11]+spec*60,0,255));tris.append(t)
 depth=np.full((H,W),-1e9);out=np.zeros((H,W,4),np.uint8)
 for t,col in zip(tris,cols):
  p=np.stack([AX+t[:,0]*S,AY+(t[:,2]*COS-t[:,1]*SIN)*S],-1);d=t@np.array([0,COS,SIN]);a,b,c=p;den=np.cross(b-a,c-a)
  if abs(den)<1e-9:continue
  for y in range(max(0,int(p[:,1].min())),min(H,int(p[:,1].max())+2)):
   for x in range(max(0,int(p[:,0].min())),min(W,int(p[:,0].max())+2)):
    v=np.array([x+.5,y+.5]);u=np.cross(v-a,c-a)/den;w=np.cross(b-a,v-a)/den;z=1-u-w
    if min(u,w,z)<-1e-5:continue
    dep=z*d[0]+u*d[1]+w*d[2]
    if dep>depth[y,x]:depth[y,x]=dep;out[y,x]=[*col,255]
 code=np.where(depth>-1e8,np.clip(np.rint((depth+128)*32)+1,1,65535),0).astype(np.uint16);raw=np.zeros((H,W,3),np.uint8);raw[:,:,0]=code>>8;raw[:,:,1]=code&255
 return Image.fromarray(out),Image.fromarray(raw)
if __name__=='__main__':
 (ROOT/'assets').mkdir(exist_ok=True)
 for i,c in enumerate(PALETTE):
  im,dep=bake(c);im.save(ROOT/'assets'/f'pawn-{i}.png');dep.save(ROOT/'assets'/'pawn-depth.png')
