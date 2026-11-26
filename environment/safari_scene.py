"""Original low-poly Safari Rush props, using the canonical world's mesh collector.
No external asset downloads. All coordinates use the existing KayKit layout units.
"""
import math
import numpy as np
from shapely.geometry import Point, LineString

def build(g):
    push, elev, rt, wt, land, rng = (g[k] for k in ('push','elev','rt','wt','land','rng'))
    cx,cz,gx,gz = (g[k] for k in ('cx','cz','gx','gz'))
    place_asset=g['asset']; placements=g['placements']
    inside=land.buffer(-8); occupied=[]
    road=LineString(g['pr']).buffer(24)
    water=g['river_polygon'].buffer(9)
    def reserve(kind,x,z,r):
        p=Point(x,z).buffer(r)
        if not inside.covers(p) or p.intersects(road) or p.intersects(water): return False
        if abs(x-cx)<125+r and cz-150-r<z<gz+r: return False
        if any(p.intersects(q) for q in occupied): return False
        hs=[elev(x+r*math.cos(a),z+r*math.sin(a)) for a in np.linspace(0,math.tau,8,endpoint=False)]
        if max(hs)-min(hs)>r*.9: return False
        occupied.append(p);placements.append(dict(asset=kind,x=x,z=z,footprintRadius=r,elevation=elev(x,z)))
        return True
    def mesh(x,z,y,rx,ry,rz,color,n=10,bands=5):
        # Faceted ellipsoid, with closed poles and deterministic face colour.
        rings=[]
        for j in range(bands+1):
            a=-math.pi/2+math.pi*j/bands
            rings.append(np.array([[x+rx*math.cos(a)*math.cos(t),y+ry*math.sin(a),z+rz*math.cos(a)*math.sin(t)] for t in np.arange(n)*math.tau/n]))
        for j in range(bands):
            for i in range(n):
                k=(i+1)%n; a,b=rings[j],rings[j+1]
                push([a[i],b[i],b[k]],color);push([a[i],b[k],a[k]],color)
    def frustum(x,z,y,r0,r1,h,color,n=10,top=True):
        t=np.arange(n)*math.tau/n
        a=np.column_stack((x+r0*np.cos(t),np.full(n,y),z+r0*np.sin(t)))
        b=np.column_stack((x+r1*np.cos(t),np.full(n,y+h),z+r1*np.sin(t)))
        for i in range(n):
            j=(i+1)%n
            push([a[i],a[j],b[j]],color);push([a[i],b[j],b[i]],color)
            if top:push([b[i],b[j],[x,y+h,z]],color)
    def block(x,z,y,w,d,h,color):
        a=np.array([[x-w/2,y,z-d/2],[x+w/2,y,z-d/2],[x+w/2,y,z+d/2],[x-w/2,y,z+d/2]])
        v=np.vstack([a,a+[0,h,0]])
        push(v[[[4,6,5],[4,7,6],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]],color)
    def tree(x,z,baobab=False):
        r=22 if baobab else 17
        if not reserve('baobab' if baobab else 'acacia',x,z,r):return
        y=elev(x,z); trunk=[116,91,61]
        frustum(x,z,y,8 if baobab else 3,5 if baobab else 1.6,28 if baobab else 22,trunk,8)
        if baobab:
            for i in range(5):
                a=i*math.tau/5;xx=x+9*math.cos(a);zz=z+9*math.sin(a)
                mesh(xx,zz,y+32,6,8,6,trunk,7,3)
                mesh(xx,zz,y+38,10,6,9,[103,124,65],9,4)
        else:
            for i in range(4):
                a=i*math.tau/4
                mesh(x+7*math.cos(a),z+7*math.sin(a),y+23,10,4,9,[111,132,59],8,3)
    def hut(x,z,r=15):
        if not reserve('thatched lodge',x,z,r+4):return
        y=elev(x,z);frustum(x,z,y,r*.8,r*.8,13,[178,136,91],12)
        frustum(x,z,y+13,r,1,15,[191,153,75],12)
        block(x,z+r*.77,y,5,1.8,9,[76,54,38])
    def tent(x,z):
        if not reserve('safari tent',x,z,15):return
        y=elev(x,z); a=np.array([[x-10,y,z-8],[x+10,y,z-8],[x,y+12,z-8],[x-10,y,z+8],[x+10,y,z+8],[x,y+12,z+8]])
        push(a[[[0,1,2],[3,5,4],[0,2,5],[0,5,3],[1,4,5],[1,5,2]]],[176,158,109])
    def jeep(x,z):
        if not reserve('safari vehicle',x,z,19):return
        y=elev(x,z);block(x,z,y+4,24,12,8,[106,119,65]);block(x-4,z,y+12,10,11,7,[88,108,103]);block(x-4,z,y+19,11,12,2,[190,175,125])
        for dx in (-8,8):
            for dz in (-6,6):mesh(x+dx,z+dz,y+4,4,4,2,[49,47,40],8,4)
    def rock(x,z,r,bal=False):
        if not reserve('granite formation',x,z,r+2):return
        y=elev(x,z);mesh(x,z,y+r*.35,r,r*.65,r*.8,[130,132,125],11,5)
        if bal:
            mesh(x+2,z,y+r*.95,r*.42,r*.42,r*.42,[149,145,134],9,4)
            mesh(x-1,z,y+r*1.38,r*.58,r*.30,r*.47,[121,126,121],10,4)
    def animal(kind,x,z):
        r=18 if kind=='elephant' else 12
        if not reserve(kind,x,z,r):return
        y=elev(x,z)
        if kind=='elephant':
            c=[124,127,126];mesh(x,z,y+11,12,9,7,c);mesh(x+11,z,y+13,6,7,5,c)
            for dz in (-5,5):mesh(x+9,z+dz,y+14,4,6,2,[143,143,139])
            frustum(x+15,z,y+3,1.6,2.3,10,c,7)
            for dx in (-7,7):
                for dz in (-4,4):frustum(x+dx,z+dz,y,2.4,2.7,9,c,7)
        elif kind=='giraffe':
            c=[199,153,79];mesh(x,z,y+12,8,5,4,c)
            for dx in (-5,5):
                for dz in (-3,3):frustum(x+dx,z+dz,y,1,1.5,12,c,6)
            frustum(x+6,z,y+12,2.8,1.5,18,c,7);mesh(x+8,z,y+31,4,2.5,2,c,8,3)
            for j in range(4):mesh(x+5,z-1.5,y+16+j*4,1.4,1.1,.8,[119,79,42],6,3)
        else:
            c=[232,225,197] if kind=='zebra' else [174,127,67]
            mesh(x,z,y+7,8,4,3.7,c);mesh(x+7,z,y+11,3,4,2,c)
            for dx in (-5,5):
                for dz in (-2.5,2.5):frustum(x+dx,z+dz,y,1,1.3,7,c,6)
            if kind=='zebra':
                for dx in (-5,-2,1,4):
                    mesh(x+dx,z,y+7,.7,4.1,3.8,[53,53,48],8,4)
    # Camp at the inherited southwest trailhead. Keep the route and road shoulders open.
    sx,sz=g['pr'][0]
    for dx,dz in [(-43,-25),(-48,28),(40,38),(66,58),(-10,60),(29,-50)]:
        hut(sx+dx,sz+dz,14)
    for dx,dz in [(-65,4),(36,62),(65,-36)]:tent(sx+dx,sz+dz)
    jeep(sx+42,sz-35)
    # Wildlife is grouped in open savanna rather than randomly distributed.
    for kind,xx,zz in [('zebra',525,560),('giraffe',390,340),('antelope',690,490),('elephant',805,410),('elephant',1010,510)]:
        for i in range(55):
            animal(kind,xx+rng.uniform(-62,62),zz+rng.uniform(-48,48))
            if sum(p['asset']==kind for p in placements)>= (8 if kind=='zebra' else 5 if kind=='giraffe' else 10):break
    for xx,zz in [(500,110),(600,140),(710,145),(680,205),(415,135)]:
        rock(xx,zz,24,True)
    for t in g['cells']:
        x,z=g['xz'](t)
        for i in range(3 if x<850 else 4):
            xx=x+rng.uniform(-43,43);zz=z+rng.uniform(-37,37)
            if rng.random()<.72:tree(xx,zz,rng.random()<.12)
            elif reserve('granite outcrop',xx,zz,10):mesh(xx,zz,elev(xx,zz)+3,9,6,7,[144,139,124],8,4)
        # Dry grass clusters (full footprint reservation, no water/road overlap).
        for i in range(5):
            xx=x+rng.uniform(-43,43);zz=z+rng.uniform(-37,37)
            if not reserve('dry grass',xx,zz,4):continue
            y=elev(xx,zz)
            for j in range(4):
                dx=rng.uniform(-2,2);dz=rng.uniform(-2,2)
                push([[xx+dx-1,y,zz+dz],[xx+dx+1,y,zz+dz],[xx+dx+1,y+rng.uniform(3,8),zz+dz+1]],[174,151,73])
    # Great Zimbabwe-inspired elliptical enclosure. Omit any section overlapping
    # the actual road footprint, so the entry is derived from the route.
    centerz=(cz-105+gz)/2; rx=98;rz=(gz-(cz-105))/2
    for i in range(48):
        a=(i+.5)*math.tau/48;x=cx+rx*math.cos(a);z=centerz+rz*math.sin(a)
        if road.intersects(Point(x,z).buffer(12)):continue
        y=elev(x,z)
        for j in range(4):
            block(x,z,y+j*5,15-j*.7,13-j*.7,5,[151+j*3,132+j*3,104+j*3])
    for dx,dz,r,h in [(55,-50,17,43),(-52,-55,15,24)]:
        x=cx+dx;z=cz+dz
        if not road.intersects(Point(x,z).buffer(r+4)):
            y=elev(x,z)
            for j in range(10):
                frustum(x,z,y+j*h/10,r*(1-j*.085),r*(1-(j+1)*.085),h/10,[157+j%3*6,138+j%3*5,111+j%3*4],12)
    # Gravel ceremonial gathering area, with the real road still visible.
    for dx in (-55,55):
        for dz in (-15,10,35):
            x=cx+dx;z=cz+dz
            if not road.intersects(Point(x,z).buffer(13)):
                frustum(x,z,elev(x,z),11,10,3,[169,147,117],10)
