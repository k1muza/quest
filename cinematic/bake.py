"""Re-light the approved mesh and bake independently projected views. No geometry changes."""
from pathlib import Path
import os,sys,time,json,math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
R=Path(__file__).resolve().parent; E=R.parent/'environment'; A=R/'assets';G=R/'gallery'; A.mkdir(exist_ok=True);G.mkdir(exist_ok=True)
os.chdir(E)
exec(compile((E/'render_world.py').read_text().split('# Optional depth-only export')[0],str(E/'render_world.py'),'exec'))
if '--mesh' in sys.argv:np.savez_compressed(A.parent/'scene.npz',vertices=V.astype('float32'),colors=C.astype('uint8'))
lights={'day':([-.55,.95,.30],[1.0,.98,.92],[.55,.68,.8],1.),'gold':([-.80,.56,.36],[1.32,1.02,.72],[.55,.65,.83],1.),'dusk':([.72,.29,-.47],[1.09,.51,.29],[.27,.38,.62],.78),'morning':([.68,.68,.35],[1.13,1.04,.84],[.48,.61,.77],.96),'night':([-.45,.74,-.45],[.32,.42,.69],[.16,.23,.38],.56),'ceremony':([-.70,.63,.42],[1.21,1.03,.72],[.43,.57,.76],1.)}
configs={'overview':(.76,105),'bridge':(.65,140),'citadel':(.84,65)};records=[]
def bake_new(name,view,lighting,scale):
 t=time.monotonic();co,offset=configs[view];si=math.sqrt(1-co*co);light,sun,sky,exposure=lights[lighting];light=np.array(light);light/=np.linalg.norm(light);sun=np.array(sun);sky=np.array(sky)
 right=np.cross([0,1,0],light);right/=np.linalg.norm(right);up=np.cross(light,right);sp=np.stack([V@right,V@up],-1);sp=(sp-sp.min((0,1))+10)*1.7;sd=V@light;shadow=depth_raster(sp,sd,*np.ceil(sp.max((0,1))+8).astype(int))
 lin=(np.maximum(C,0)/255)**2.2;diff=np.maximum(0,norm@light);hemi=.55+.45*np.clip(norm[:,1],0,1);ambient=sky*hemi[:,None]*.75;direct=diff[:,None]*sun*.85
 color=(np.clip(lin*(ambient+direct)*exposure,0,1)**(1/2.2))*255;dark=(np.clip(lin*ambient*exposure,0,1)**(1/2.2))*255
 water=(C[:,2]>C[:,0]*1.5)&(C[:,1]>C[:,0]*1.5)&(norm[:,1]>.8);half=light+np.array([0,co,si]);half/=np.linalg.norm(half);spec=np.maximum(0,norm@half)**28;color[water]+=spec[water,None]*np.array([55,68,64])
 p=np.stack([V[:,:,0],OY+offset+V[:,:,2]*co-V[:,:,1]*si],-1)*scale;d=V@np.array([0,co,si]);w,h=int(W*scale),int(H*scale);raw=render(p,d,sp,sd,color,dark,shadow,w,h)
 zb=depth_raster(p/scale,d,W,H);valid=zb>-1e8;ao=np.zeros_like(zb)
 for dy,dx in [(0,4),(0,-4),(4,0),(-4,0),(6,6),(-6,6),(6,-6),(-6,-6),(0,10),(0,-10)]:
  shift=np.roll(zb,(dy,dx),(0,1));ao+=np.where(valid&(shift>-1e8),np.clip((shift-zb-2)/25,0,1),0)
 ao=gaussian_filter(ao/10,1);aoi=np.asarray(Image.fromarray(ao).resize((w,h),Image.Resampling.BILINEAR));rgb=raw[:,:,:3].astype('float32');rgb*=1-.32*aoi[:,:,None]
 fog=np.clip((570-zb)/850,0,.10)*valid;fog=np.asarray(Image.fromarray(fog).resize((w,h),Image.Resampling.BILINEAR));rgb=rgb*(1-fog[:,:,None])+np.array([113,157,163],np.float32)*fog[:,:,None];raw[:,:,:3]=np.uint8(np.clip(rgb,0,255));del rgb,aoi,fog
 yy,xx=np.ogrid[:h,:w];rad=np.clip(1-np.sqrt(((xx-w*.49)/(w*.75))**2+((yy-h*.45)/(h*.92))**2),0,1);bg=np.empty((h,w,3),np.uint8);mult=.65 if lighting=='night' else .85 if lighting=='dusk' else 1
 for i,(a,b) in enumerate([(15,29),(52,61),(73,58)]):bg[:,:,i]=np.uint8((a+b*rad)*mult)
 im=Image.fromarray(bg).convert('RGBA');im.alpha_composite(Image.fromarray(raw));im=im.convert('RGB');path=A/(name+'.jpg');im.save(path,quality=92,subsampling=0,optimize=True)
 if name in ('gold-4k','bridge','citadel'):
  q=np.where(valid,np.clip(np.rint((zb+128)*32)+1,1,65535),0).astype(np.uint16);depth=np.zeros((H,W,3),np.uint8);depth[:,:,0]=q>>8;depth[:,:,1]=q&255;Image.fromarray(depth).save(A/(view+'-depth.png'),optimize=True)
 records.append({'name':name,'view':view,'light':lighting,'width':w,'height':h,'bytes':path.stat().st_size,'seconds':round(time.monotonic()-t,2)});print(records[-1],flush=True)
 if name=='gold-4k':
  for w2 in (1920,2560,3840):
   pic=im.resize((w2,w2*9//16),Image.Resampling.LANCZOS)
   for ext,kw in [('jpg',{'quality':90,'optimize':True}),('webp',{'quality':90,'method':2}),('png',{})]:pic.save(G/f'resolution-{w2}.{ext}',**kw)
for args in [('gold-4k','overview','gold',2),('day','overview','day',1),('bridge','bridge','gold',1.5),('citadel','citadel','gold',1.5),('dusk','overview','dusk',1),('morning','overview','morning',1),('night','overview','night',1),('ceremony','overview','ceremony',1)]:bake_new(*args)
json.dump({'renders':records,'cameras':{k:{'cos':c,'sin':math.sqrt(1-c*c),'offset':o} for k,(c,o) in configs.items()},'triangles':len(V)},open(A.parent/'bake-results.json','w'),indent=2)
